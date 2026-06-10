from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from unicodedata import normalize
from domain.entities.usuario import Usuario
from domain.interfaces.unit_of_work import IUnitOfWork
from infrastructure.security.jwt_service import JwtService
from infrastructure.unit_of_work.unit_of_work_impl import get_uow

bearer_scheme = HTTPBearer()

ADMIN_CITY_POLICIES = {
    "MEDELLIN": {"GET", "POST", "DELETE"},
    "BOGOTA": {"GET", "POST", "PUT", "PATCH"},
}


def _normalize_city(ciudad: str | None) -> str:
    if not ciudad:
        return ""
    return normalize("NFKD", ciudad.strip().upper()).encode("ascii", "ignore").decode("ascii")


def _validate_admin_city_policy(usuario: Usuario, accion: str) -> None:
    ciudad = _normalize_city(usuario.ciudad)
    acciones = ADMIN_CITY_POLICIES.get(ciudad)
    if not acciones or accion.upper() not in acciones:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Politica de ciudad denegada para {accion.upper()}",
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), uow: IUnitOfWork = Depends(get_uow)) -> Usuario:
    payload = JwtService().verify_token(credentials.credentials)
    user_id = int(payload.get("sub"))
    async with uow:
        usuario = await uow.usuarios.get_by_id(user_id)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")
        return usuario


def require_roles(*roles: str):
    async def dependency(usuario: Usuario = Depends(get_current_user)) -> Usuario:
        if usuario.rol not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tiene permisos para esta accion")
        return usuario
    return dependency


def require_roles_with_admin_city_policy(accion: str, *roles: str):
    async def dependency(usuario: Usuario = Depends(require_roles(*roles))) -> Usuario:
        if usuario.rol == "ADMIN":
            _validate_admin_city_policy(usuario, accion)
        return usuario
    return dependency


async def require_admin(usuario: Usuario = Depends(get_current_user)) -> Usuario:
    if usuario.rol != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo ADMIN puede realizar esta accion")
    return usuario


def require_admin_city_policy(accion: str):
    async def dependency(usuario: Usuario = Depends(require_admin)) -> Usuario:
        _validate_admin_city_policy(usuario, accion)
        return usuario
    return dependency


async def require_empleado_owner_or_admin(id: int, usuario: Usuario = Depends(get_current_user), uow: IUnitOfWork = Depends(get_uow)) -> Usuario:
    if usuario.rol == "ADMIN":
        return usuario
    async with uow:
        empleado = await uow.empleados.get_by_id(id)
        if not empleado:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Empleado con ID {id} no encontrado")
        if usuario.compania_id is None or empleado.compania_id != usuario.compania_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Politica EsPropietarioDeCompania denegada")
        return usuario


def require_empleado_owner_or_admin_city_policy(accion: str):
    async def dependency(id: int, usuario: Usuario = Depends(get_current_user), uow: IUnitOfWork = Depends(get_uow)) -> Usuario:
        if usuario.rol == "ADMIN":
            _validate_admin_city_policy(usuario, accion)
            return usuario
        async with uow:
            empleado = await uow.empleados.get_by_id(id)
            if not empleado:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Empleado con ID {id} no encontrado")
            if usuario.compania_id is None or empleado.compania_id != usuario.compania_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Politica EsPropietarioDeCompania denegada")
            return usuario
    return dependency
