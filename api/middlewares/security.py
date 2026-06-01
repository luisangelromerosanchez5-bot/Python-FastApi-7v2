from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from domain.entities.usuario import Usuario
from domain.interfaces.unit_of_work import IUnitOfWork
from infrastructure.security.jwt_service import JwtService
from infrastructure.unit_of_work.unit_of_work_impl import get_uow

bearer_scheme = HTTPBearer()


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


async def require_admin(usuario: Usuario = Depends(get_current_user)) -> Usuario:
    if usuario.rol != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo ADMIN puede realizar esta accion")
    return usuario


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
