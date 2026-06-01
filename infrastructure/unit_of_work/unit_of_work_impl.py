import logging
from domain.interfaces.unit_of_work import IUnitOfWork
from infrastructure.database.connection import SessionLocal
from infrastructure.repositories.compania_repository_impl import CompaniaRepositoryImpl
from infrastructure.repositories.empleado_repository_impl import EmpleadoRepositoryImpl
from infrastructure.repositories.usuario_repository_impl import UsuarioRepositoryImpl

logger = logging.getLogger(__name__)


class UnitOfWorkImpl(IUnitOfWork):
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self._session = None
        self._companias = None
        self._empleados = None
        self._usuarios = None

    async def __aenter__(self):
        self._session = self.session_factory()
        self._companias = CompaniaRepositoryImpl(self._session)
        self._empleados = EmpleadoRepositoryImpl(self._session)
        self._usuarios = UsuarioRepositoryImpl(self._session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type:
                logger.error(f"Error en transaccion async: {exc_val}. Haciendo rollback.")
                await self.rollback()
        finally:
            if self._session:
                await self._session.close()

    @property
    def companias(self) -> CompaniaRepositoryImpl:
        return self._companias

    @property
    def empleados(self) -> EmpleadoRepositoryImpl:
        return self._empleados

    @property
    def usuarios(self) -> UsuarioRepositoryImpl:
        return self._usuarios

    async def commit(self) -> None:
        logger.info("Confirmando transaccion async (commit).")
        if self._session:
            await self._session.commit()

    async def rollback(self) -> None:
        logger.warning("Revirtiendo transaccion async (rollback).")
        if self._session:
            await self._session.rollback()

    async def save_changes(self) -> None:
        await self.commit()


def get_uow() -> IUnitOfWork:
    return UnitOfWorkImpl(session_factory=SessionLocal)
