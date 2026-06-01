from typing import Any, List
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from domain.entities.empleado import Empleado
from domain.interfaces.empleado_repository import IEmpleadoRepository


class EmpleadoRepositoryImpl(IEmpleadoRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> List[Empleado]:
        result = await self.session.execute(select(Empleado))
        return list(result.scalars().all())

    async def get_by_id(self, id: int) -> Empleado | None:
        result = await self.session.execute(select(Empleado).where(Empleado.id == id))
        return result.scalar_one_or_none()

    async def get_by_compania(self, compania_id: int) -> List[Empleado]:
        result = await self.session.execute(select(Empleado).where(Empleado.compania_id == compania_id))
        return list(result.scalars().all())

    async def get_paged(self, pagina: int, tamano: int, orden: str, direccion: str, buscar: str | None = None, compania_id: int | None = None) -> tuple[List[Empleado], int]:
        allowed_order_fields = {
            "id": Empleado.id,
            "nombre": Empleado.nombre,
            "apellido": Empleado.apellido,
            "correo": Empleado.correo,
            "cargo": Empleado.cargo,
            "salario": Empleado.salario,
        }
        order_column = allowed_order_fields.get(orden, Empleado.id)
        conditions = []

        if compania_id is not None:
            conditions.append(Empleado.compania_id == compania_id)

        if buscar:
            pattern = f"%{buscar}%"
            conditions.append(
                or_(
                    Empleado.nombre.ilike(pattern),
                    Empleado.apellido.ilike(pattern),
                    Empleado.correo.ilike(pattern),
                )
            )

        count_stmt = select(func.count()).select_from(Empleado)
        stmt = select(Empleado)
        if conditions:
            count_stmt = count_stmt.where(*conditions)
            stmt = stmt.where(*conditions)

        total_result = await self.session.execute(count_stmt)
        total = int(total_result.scalar_one())

        if direccion.lower() == "desc":
            order_column = order_column.desc()

        offset = (pagina - 1) * tamano
        result = await self.session.execute(stmt.order_by(order_column).offset(offset).limit(tamano))
        return list(result.scalars().all()), total

    async def create(self, empleado: Empleado) -> None:
        self.session.add(empleado)
        await self.session.flush()

    async def create_range(self, empleados: List[Empleado]) -> None:
        self.session.add_all(empleados)
        await self.session.flush()

    async def update(self, empleado: Empleado) -> None:
        await self.session.merge(empleado)

    async def delete(self, empleado: Empleado) -> None:
        await self.session.delete(empleado)

    async def delete_range(self, empleados: List[Empleado]) -> None:
        for empleado in empleados:
            await self.session.delete(empleado)

    async def find_by_condition(self, condition: Any) -> List[Empleado]:
        result = await self.session.execute(select(Empleado).where(condition))
        return list(result.scalars().all())
