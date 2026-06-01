from abc import ABC, abstractmethod
from typing import List
from domain.entities.usuario import Usuario


class IUsuarioRepository(ABC):
    @abstractmethod
    async def get_all(self) -> List[Usuario]:
        pass

    @abstractmethod
    async def get_by_id(self, id: int) -> Usuario | None:
        pass

    @abstractmethod
    async def get_by_correo(self, correo: str) -> Usuario | None:
        pass

    @abstractmethod
    async def create(self, usuario: Usuario) -> None:
        pass
