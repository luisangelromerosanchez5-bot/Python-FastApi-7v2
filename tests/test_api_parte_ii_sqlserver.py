"""
Pruebas de integración para la Parte II usando el mismo stack del proyecto:
FastAPI + SQLAlchemy + SQL Server.

Requisitos antes de ejecutar:
1. Tener SQL Server/LocalDB activo.
2. Configurar el archivo .env con la base de datos de prueba o desarrollo.
3. Ejecutar: pytest

Nota: estas pruebas usan la misma configuración de infrastructure/database/connection.py.
No cambian el ORM ni usan SQLite.
"""

from fastapi.testclient import TestClient
from api.main import app


def auth_headers(client: TestClient, correo="admin@demo.com", contrasena="Admin123"):
    response = client.post("/api/auth/login", json={"correo": correo, "contrasena": contrasena})
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_login_y_perfil():
    with TestClient(app) as client:
        headers = auth_headers(client)
        response = client.get("/api/auth/perfil", headers=headers)
        assert response.status_code == 200
        assert response.json()["rol"] == "ADMIN"


def test_listado_paginado_empleados():
    with TestClient(app) as client:
        headers = auth_headers(client)
        response = client.get("/api/empleados?pagina=1&tamano=5&orden=apellido&dir=asc&buscar=a", headers=headers)
        assert response.status_code == 200
        body = response.json()
        assert set(body.keys()) == {"datos", "pagina", "tamano", "total", "totalPaginas"}


def test_bulk_patch_y_delete_lote():
    with TestClient(app) as client:
        headers = auth_headers(client)
        bulk = {
            "empleados": [
                {
                    "nombre": "Pedro",
                    "apellido": "Bulk",
                    "correo": "pedro.bulk@example.com",
                    "cargo": "QA",
                    "salario": 2500,
                    "compania_id": 1,
                },
                {
                    "nombre": "Lucia",
                    "apellido": "Bulk",
                    "correo": "lucia.bulk@example.com",
                    "cargo": "Dev",
                    "salario": 3000,
                    "compania_id": 1,
                },
            ]
        }
        created = client.post("/api/empleados/lote", json=bulk, headers=headers)
        assert created.status_code == 201
        ids = [item["id"] for item in created.json()]

        patched = client.patch(f"/api/empleados/{ids[0]}", json={"cargo": "Lead QA"}, headers=headers)
        assert patched.status_code == 200

        deleted = client.request("DELETE", "/api/empleados/lote", json={"ids": ids}, headers=headers)
        assert deleted.status_code == 204


def test_rol_usuario_no_puede_eliminar():
    with TestClient(app) as client:
        headers = auth_headers(client, "usuario@demo.com", "Usuario123")
        response = client.delete("/api/empleados/1", headers=headers)
        assert response.status_code == 403


def test_policy_owner_permite_editar_empleado_de_su_compania():
    with TestClient(app) as client:
        headers = auth_headers(client, "usuario@demo.com", "Usuario123")
        response = client.patch("/api/empleados/1", json={"cargo": "Actualizado por policy"}, headers=headers)
        assert response.status_code == 200


def test_rollback_transaccional_compania_con_empleados():
    with TestClient(app) as client:
        headers = auth_headers(client)
        payload = {
            "nombre": "Rollback Corp",
            "direccion": "Calle rollback 123",
            "telefono": "3009998888",
            "empleados": [
                {
                    "nombre": "Duplicado",
                    "apellido": "Correo",
                    "correo": "juan.perez@techsolutions.com",
                    "cargo": "Dev",
                    "salario": 1000,
                }
            ],
        }
        response = client.post("/api/companias/con-empleados", json=payload, headers=headers)
        assert response.status_code == 400

        companias = client.get("/api/companias", headers=headers).json()
        assert all(c["nombre"] != "Rollback Corp" for c in companias)
