from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from domain.entities.usuario import Usuario
from domain.interfaces.usuario_repository import IUsuarioRepository


class UsuarioRepositoryImpl(IUsuarioRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> List[Usuario]:
        result = await self.session.execute(select(Usuario))
        return list(result.scalars().all())

    async def get_by_id(self, id: int) -> Usuario | None:
        result = await self.session.execute(select(Usuario).where(Usuario.id == id))
        return result.scalar_one_or_none()

    async def get_by_correo(self, correo: str) -> Usuario | None:
        result = await self.session.execute(select(Usuario).where(Usuario.correo == correo))
        return result.scalar_one_or_none()

    async def create(self, usuario: Usuario) -> None:
        self.session.add(usuario)
        await self.session.flush()
