from abc import ABC, abstractmethod
from typing import Any, List
from domain.entities.empleado import Empleado


class IEmpleadoRepository(ABC):
    @abstractmethod
    async def get_all(self) -> List[Empleado]:
        pass

    @abstractmethod
    async def get_by_id(self, id: int) -> Empleado | None:
        pass

    @abstractmethod
    async def get_by_compania(self, compania_id: int) -> List[Empleado]:
        pass

    @abstractmethod
    async def get_paged(self, pagina: int, tamano: int, orden: str, direccion: str, buscar: str | None = None, compania_id: int | None = None) -> tuple[List[Empleado], int]:
        pass

    @abstractmethod
    async def create(self, empleado: Empleado) -> None:
        pass

    @abstractmethod
    async def create_range(self, empleados: List[Empleado]) -> None:
        pass

    @abstractmethod
    async def update(self, empleado: Empleado) -> None:
        pass

    @abstractmethod
    async def delete(self, empleado: Empleado) -> None:
        pass

    @abstractmethod
    async def delete_range(self, empleados: List[Empleado]) -> None:
        pass

    @abstractmethod
    async def find_by_condition(self, condition: Any) -> List[Empleado]:
        pass
