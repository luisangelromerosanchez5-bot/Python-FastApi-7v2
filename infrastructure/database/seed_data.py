from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from domain.entities.compania import Compania
from domain.entities.empleado import Empleado
from domain.entities.usuario import Usuario
from infrastructure.security.password_hasher import PasswordHasher


async def seed_data(db: AsyncSession):
    hasher = PasswordHasher()

    existing_companias = await db.execute(select(Compania).limit(1))
    if existing_companias.scalar_one_or_none() is not None:
        existing_usuario = await db.execute(select(Usuario).limit(1))
        if existing_usuario.scalar_one_or_none() is None:
            db.add(
                Usuario(
                    nombre="Administrador",
                    correo="admin@demo.com",
                    contrasena_hash=hasher.hash("Admin123"),
                    rol="ADMIN",
                    compania_id=None,
                )
            )
            await db.commit()
        return

    c1 = Compania(nombre="Tech Solutions S.A.S", direccion="Calle 45 # 10-20", telefono="3001234567")
    c2 = Compania(nombre="Innovatech Colombia", direccion="Av El Dorado # 68-50", telefono="6017654321")
    c3 = Compania(nombre="DataCorp Ltda", direccion="Carrera 7 # 32-16", telefono="3157894561")

    db.add_all([c1, c2, c3])
    await db.flush()

    empleados = [
        Empleado(nombre="Juan", apellido="Perez", correo="juan.perez@techsolutions.com", cargo="Desarrollador", salario=3500000.0, compania_id=c1.id),
        Empleado(nombre="Maria", apellido="Gomez", correo="maria.gomez@techsolutions.com", cargo="Analista", salario=4000000.0, compania_id=c1.id),
        Empleado(nombre="Carlos", apellido="Rodriguez", correo="carlos.rod@techsolutions.com", cargo="Scrum Master", salario=6000000.0, compania_id=c1.id),
        Empleado(nombre="Ana", apellido="Martinez", correo="ana.martinez@innovatech.co", cargo="Tester", salario=2500000.0, compania_id=c2.id),
        Empleado(nombre="Luis", apellido="Sanchez", correo="luis.sanchez@innovatech.co", cargo="Desarrollador", salario=4500000.0, compania_id=c2.id),
        Empleado(nombre="Laura", apellido="Diaz", correo="laura.diaz@innovatech.co", cargo="DevOps", salario=5500000.0, compania_id=c2.id),
        Empleado(nombre="Diego", apellido="Giraldo", correo="diego.giraldo@datacorp.com", cargo="Analista", salario=3800000.0, compania_id=c3.id),
        Empleado(nombre="Sofia", apellido="Torres", correo="sofia.torres@datacorp.com", cargo="Desarrollador", salario=4800000.0, compania_id=c3.id),
        Empleado(nombre="Andres", apellido="Castro", correo="andres.castro@datacorp.com", cargo="DevOps", salario=5800000.0, compania_id=c3.id),
        Empleado(nombre="Valentina", apellido="Ruiz", correo="valentina.ruiz@datacorp.com", cargo="Tester", salario=2800000.0, compania_id=c3.id),
    ]

    usuarios = [
        Usuario(nombre="Administrador", correo="admin@demo.com", contrasena_hash=hasher.hash("Admin123"), rol="ADMIN", compania_id=None),
        Usuario(nombre="Usuario Tech", correo="usuario@demo.com", contrasena_hash=hasher.hash("Usuario123"), rol="USUARIO", compania_id=c1.id),
    ]

    db.add_all(empleados + usuarios)
    await db.commit()
