from typing import Any, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from domain.entities.compania import Compania
from domain.interfaces.compania_repository import ICompaniaRepository


class CompaniaRepositoryImpl(ICompaniaRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> List[Compania]:
        result = await self.session.execute(select(Compania))
        return list(result.scalars().all())

    async def get_by_id(self, id: int) -> Compania | None:
        result = await self.session.execute(select(Compania).where(Compania.id == id))
        return result.scalar_one_or_none()

    async def create(self, compania: Compania) -> None:
        self.session.add(compania)
        await self.session.flush()

    async def update(self, compania: Compania) -> None:
        await self.session.merge(compania)

    async def delete(self, compania: Compania) -> None:
        await self.session.delete(compania)

    async def find_by_condition(self, condition: Any) -> List[Compania]:
        result = await self.session.execute(select(Compania).where(condition))
        return list(result.scalars().all())

    async def get_with_empleados(self, id: int) -> Compania | None:
        result = await self.session.execute(
            select(Compania)
            .options(joinedload(Compania.empleados))
            .where(Compania.id == id)
        )
        return result.unique().scalar_one_or_none()
