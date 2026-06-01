from abc import ABC, abstractmethod
from typing import Any, List
from domain.entities.compania import Compania


class ICompaniaRepository(ABC):
    @abstractmethod
    async def get_all(self) -> List[Compania]:
        pass

    @abstractmethod
    async def get_by_id(self, id: int) -> Compania | None:
        pass

    @abstractmethod
    async def create(self, compania: Compania) -> None:
        pass

    @abstractmethod
    async def update(self, compania: Compania) -> None:
        pass

    @abstractmethod
    async def delete(self, compania: Compania) -> None:
        pass

    @abstractmethod
    async def find_by_condition(self, condition: Any) -> List[Compania]:
        pass

    @abstractmethod
    async def get_with_empleados(self, id: int) -> Compania | None:
        pass
