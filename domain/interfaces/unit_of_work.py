from abc import ABC, abstractmethod
from domain.interfaces.compania_repository import ICompaniaRepository
from domain.interfaces.empleado_repository import IEmpleadoRepository
from domain.interfaces.usuario_repository import IUsuarioRepository


class IUnitOfWork(ABC):
    @property
    @abstractmethod
    def companias(self) -> ICompaniaRepository:
        pass

    @property
    @abstractmethod
    def empleados(self) -> IEmpleadoRepository:
        pass

    @property
    @abstractmethod
    def usuarios(self) -> IUsuarioRepository:
        pass

    @abstractmethod
    async def commit(self) -> None:
        pass

    @abstractmethod
    async def rollback(self) -> None:
        pass

    @abstractmethod
    async def save_changes(self) -> None:
        pass

    @abstractmethod
    async def __aenter__(self) -> "IUnitOfWork":
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        pass
