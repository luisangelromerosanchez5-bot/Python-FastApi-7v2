# API REST — Onion Architecture (Python + FastAPI + SQLAlchemy + SQL Server)

Este proyecto implementa una API REST completa en Python siguiendo la **Arquitectura Onion** (Arquitectura de Cebolla) y el patrón **Repository & Unit of Work**.

## Estructura del Proyecto

```
proyecto/
├── domain/                  # Capa de Dominio (Núcleo)
│   ├── entities/            # Entidades de negocio (SQLAlchemy Mappings)
│   └── interfaces/          # Contratos / Repositorios y Unit of Work
├── application/             # Capa de Aplicación
│   ├── services/            # Lógica de aplicación y orquestación
│   └── dtos/                # Validaciones y transferencia de datos (Pydantic v2)
├── infrastructure/          # Capa de Infraestructura
│   ├── database/            # Conexión a la BD y Seeding de datos
│   ├── repositories/        # Implementaciones de repositorios
│   └── unit_of_work/        # Implementación de Unit of Work (Context Manager)
├── api/                     # Capa de Entrada / API
│   ├── controllers/         # Controladores / Endpoints
│   ├── middlewares/         # Middleware global para manejo de errores
│   └── main.py              # Punto de entrada de FastAPI
├── alembic/                 # Migraciones de base de datos
├── alembic.ini
├── .env                     # Variables de entorno
├── requirements.txt         # Dependencias
└── README.md
```

## Requisitos de Instalación

1. Crear un entorno virtual e instalar las dependencias:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # En Windows
   pip install -r requirements.txt
   ```

2. Configurar el archivo `.env` con las credenciales de tu base de datos SQL Server.

3. Ejecutar las migraciones de Alembic (opcional, ya que en el startup se autogenera la base de datos si no existe):
   ```bash
   alembic upgrade head
   ```

4. Ejecutar el servidor:
   ```bash
   uvicorn api.main:app --reload --port 8000
   ```

5. Acceder a la documentación interactiva (Swagger) en: `http://localhost:8000/docs`.

## Parte II - Guia Onion Architecture + JWT

Esta version amplía la API de la Parte I con CRUD de colecciones, validaciones, pruebas, seguridad JWT por roles y una policy de propiedad.

### Usuarios iniciales

El seeding crea estos usuarios:

| Correo | Contraseña | Rol | Uso |
| --- | --- | --- | --- |
| `admin@demo.com` | `Admin123` | `ADMIN` Medellin | Puede consultar, crear, crear en lote y eliminar. No puede actualizar con PUT/PATCH. |
| `admin.bogota@demo.com` | `Admin123` | `ADMIN` Bogota | Puede consultar, crear, crear en lote y actualizar con PUT/PATCH. No puede eliminar. |
| `usuario@demo.com` | `Usuario123` | `USUARIO` | Puede consultar, crear y editar empleados de su propia compañía. |

## CRUD de colecciones

Endpoints agregados:

| Método | Ruta | Descripción |
| --- | --- | --- |
| `GET` | `/api/empleados?pagina=1&tamano=10&orden=apellido&dir=asc&buscar=gomez` | Listado paginado, filtrado y ordenado. |
| `GET` | `/api/companias/{id}/empleados?pagina=1&tamano=10` | Empleados de una compañía con paginación. |
| `POST` | `/api/empleados/lote` | Creación masiva dentro de una sola transacción. |
| `PATCH` | `/api/empleados/{id}` | Actualización parcial. |
| `DELETE` | `/api/empleados/lote` | Eliminación múltiple dentro de una sola transacción. |

La respuesta paginada usa un envelope:

```json
{
  "datos": [],
  "pagina": 1,
  "tamano": 10,
  "total": 57,
  "totalPaginas": 6
}
```

Los repositorios solo agregan, consultan o marcan entidades. El `commit` y el `rollback` siguen centralizados en el Unit of Work.

## Programación asíncrona

FastAPI soporta `async def` sobre ASGI y SQLAlchemy soporta acceso asíncrono mediante `AsyncSession`. En esta versión se implementó async real en el flujo principal usando SQL Server + SQLAlchemy + `aioodbc`.

Evidencia en el código:

- `infrastructure/database/connection.py`: usa `create_async_engine`, `async_sessionmaker` y la URL `mssql+aioodbc`.
- `infrastructure/unit_of_work/unit_of_work_impl.py`: usa `async def __aenter__`, `async def __aexit__`, `await commit()` y `await rollback()`.
- `infrastructure/repositories/*_repository_impl.py`: usan `AsyncSession`, `select(...)` y `await session.execute(...)`.
- `application/services/*_service.py`: los casos de uso son `async def` y usan `async with self.uow`.
- `api/controllers/*_controller.py`: los endpoints son `async def` y llaman los servicios con `await`.

El flujo real es:

```text
Controller async -> await Service -> await UnitOfWork -> await Repository -> AsyncSession -> DB
```

Precaución principal: una `AsyncSession` no debe compartirse entre tareas concurrentes; se mantiene una sesión por unidad de trabajo.

## Validaciones

Se usa Pydantic, mecanismo recomendado en FastAPI:

- Compañía: nombre obligatorio entre 3 y 100 caracteres.
- Compañía: teléfono obligatorio, solo dígitos, entre 7 y 15 caracteres.
- Empleado: nombre y apellido obligatorios.
- Empleado: correo con formato válido y validación de unicidad en el servicio.
- Empleado: salario mayor que 0.
- Empleado: `compania_id` obligatorio y existente.

Los errores se centralizan en `api/middlewares/error_handler.py` y devuelven `422`, `400`, `401`, `403` o `404` según corresponda.

## Pruebas

Framework usado: `pytest` con `TestClient`, usando la misma configuración SQL Server + SQLAlchemy del proyecto.

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Ejecutar pruebas:

```bash
pytest
```

Las pruebas cubren:

- Login y perfil autenticado.
- Listado paginado.
- Creación masiva.
- PATCH.
- Eliminación múltiple.
- Validación de rol insuficiente.
- Policy de propiedad.
- Rollback transaccional cuando falla `POST /api/companias/con-empleados`.

## Seguridad

### Autenticación con JWT

Endpoints:

| Método | Ruta | Descripción |
| --- | --- | --- |
| `POST` | `/api/auth/registro` | Registra usuario y guarda hash de contraseña. |
| `POST` | `/api/auth/login` | Valida credenciales y devuelve JWT. |
| `GET` | `/api/auth/perfil` | Devuelve el usuario autenticado. |

La contraseña nunca se guarda en texto plano. Se usa PBKDF2-HMAC-SHA256 con salt aleatorio. El JWT usa HS256 y contiene claims como `sub`, `correo`, `rol`, `ciudad`, `compania_id`, `permisos` y `exp`.

### Autorización por roles

Matriz aplicada:

| Operación | Rol requerido |
| --- | --- |
| GET | Usuario autenticado |
| POST | `ADMIN` o `USUARIO` |
| PUT/PATCH | `ADMIN` o `USUARIO`, más policy cuando aplica |
| DELETE | `ADMIN` |
| `POST /api/companias/con-empleados` | `ADMIN` |

### Autorización por políticas

Policies implementadas: `EsPropietarioDeCompania` y permisos de `ADMIN` por ciudad.

Regla de compania: un usuario con rol `USUARIO` solo puede actualizar empleados cuya `compania_id` coincida con la `compania_id` del token/usuario autenticado.

Regla de admins por ciudad:

| Ciudad | Permisos |
| --- | --- |
| Medellin | `GET`, `POST`, `POST /api/empleados/lote`, `POST /api/companias/con-empleados`, `DELETE` |
| Bogota | `GET`, `POST`, `POST /api/empleados/lote`, `POST /api/companias/con-empleados`, `PUT`, `PATCH` |

En FastAPI se implementa como dependencia compuesta en `api/middlewares/security.py`, equivalente conceptual a `[Authorize(Policy="...")]` en ASP.NET Core.

## Variables de entorno

```env
DB_SERVER=(localdb)\MSSQLLocalDB
DB_PORT=
DB_NAME=companias_db
DB_DRIVER=ODBC Driver 17 for SQL Server
DB_TRUSTED_CONNECTION=True
DB_USER=
DB_PASSWORD=
JWT_SECRET_KEY=cambie-esta-clave-por-una-muy-segura
JWT_EXPIRATION_MINUTES=60
```

Para pruebas se recomienda usar una base SQL Server de prueba configurada en el `.env`, por ejemplo cambiando `DB_NAME` a una base dedicada como `companias_db_test`.

## Comparación ampliada con ASP.NET Core

| Concepto en ASP.NET Core | Equivalente en FastAPI / SQLAlchemy |
| --- | --- |
| Endpoints de colección (`IEnumerable` / `List`) | Rutas que reciben/devuelven `list[...]` con DTOs Pydantic. |
| Paginación (`Skip/Take`) | `offset()` y `limit()` en SQLAlchemy. |
| `async / await + Task<T>` | `async def`, `await`, `AsyncSession`, `create_async_engine` y `mssql+aioodbc`. |
| DataAnnotations / FluentValidation | Pydantic `Field(...)` y `field_validator`. |
| xUnit / NUnit + Moq | `pytest`, `TestClient` y base SQL Server de prueba. |
| `AddAuthentication().AddJwtBearer()` | Dependencia `HTTPBearer` + servicio JWT. |
| `[Authorize(Roles="ADMIN")]` | Dependencia `require_admin` o `require_roles(...)`. |
| `[Authorize(Policy="...")]` + `IAuthorizationHandler` | Dependencia `require_empleado_owner_or_admin`. |
| `ClaimsPrincipal / Claims` | Payload del JWT y entidad `Usuario` recuperada en `get_current_user`. |

## Evidencia de uso de IA

Prompts usados como base:

- Prompt 7: CRUD de colecciones con bulk, PATCH, delete múltiple, paginación, filtros y orden.
- Prompt 8: Soporte async en FastAPI y SQLAlchemy con `AsyncSession` y `aioodbc`.
- Prompt 9: Validaciones recomendadas con Pydantic.
- Prompt 10: Pruebas con pytest y TestClient.
- Prompt 11: JWT por roles en FastAPI.
- Prompt 12: Diferencia entre roles y policies, implementada como dependencia de ownership.

## Conclusiones de la Parte II

La API evolucionó hacia una solución más cercana a producción. Mantiene el flujo Controller -> Service -> Unit of Work -> Repository -> ORM -> DB, agrega operaciones de colección, validaciones, pruebas, JWT, roles y una política de autorización por propiedad comparable con las policies de ASP.NET Core.
