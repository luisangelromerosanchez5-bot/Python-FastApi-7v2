from fastapi import APIRouter, Depends, Response, status
from domain.interfaces.unit_of_work import IUnitOfWork
from infrastructure.unit_of_work.unit_of_work_impl import get_uow
from application.services.empleado_service import EmpleadoService
from application.dtos.empleado_dto import (
    EmpleadoBulkCreateDTO,
    EmpleadoCreateDTO,
    EmpleadoDeleteRangeDTO,
    EmpleadoPagedResponseDTO,
    EmpleadoResponseDTO,
    EmpleadoUpdateDTO,
)
from api.middlewares.security import get_current_user, require_admin, require_empleado_owner_or_admin, require_roles

router = APIRouter(prefix="/api/empleados", tags=["Empleados"])


@router.get("", response_model=EmpleadoPagedResponseDTO)
async def get_all(
    pagina: int = 1,
    tamano: int = 10,
    orden: str = "id",
    dir: str = "asc",
    buscar: str | None = None,
    uow: IUnitOfWork = Depends(get_uow),
    _usuario=Depends(get_current_user),
):
    return await EmpleadoService(uow).get_paged(pagina, tamano, orden, dir, buscar)


@router.post("/lote", response_model=list[EmpleadoResponseDTO], status_code=status.HTTP_201_CREATED)
async def create_lote(dto: EmpleadoBulkCreateDTO, uow: IUnitOfWork = Depends(get_uow), _usuario=Depends(require_roles("ADMIN", "USUARIO"))):
    return await EmpleadoService(uow).create_range(dto.empleados)


@router.delete("/lote", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lote(dto: EmpleadoDeleteRangeDTO, uow: IUnitOfWork = Depends(get_uow), _usuario=Depends(require_admin)):
    await EmpleadoService(uow).delete_range(dto.ids)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{id}", response_model=EmpleadoResponseDTO)
async def get_by_id(id: int, uow: IUnitOfWork = Depends(get_uow), _usuario=Depends(get_current_user)):
    return await EmpleadoService(uow).get_by_id(id)


@router.post("", response_model=EmpleadoResponseDTO, status_code=status.HTTP_201_CREATED)
async def create(dto: EmpleadoCreateDTO, uow: IUnitOfWork = Depends(get_uow), _usuario=Depends(require_roles("ADMIN", "USUARIO"))):
    return await EmpleadoService(uow).create(dto)


@router.put("/{id}", response_model=EmpleadoResponseDTO)
async def update(id: int, dto: EmpleadoUpdateDTO, uow: IUnitOfWork = Depends(get_uow), _usuario=Depends(require_empleado_owner_or_admin)):
    return await EmpleadoService(uow).update(id, dto)


@router.patch("/{id}", response_model=EmpleadoResponseDTO)
async def patch(id: int, dto: EmpleadoUpdateDTO, uow: IUnitOfWork = Depends(get_uow), _usuario=Depends(require_empleado_owner_or_admin)):
    return await EmpleadoService(uow).patch(id, dto)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(id: int, uow: IUnitOfWork = Depends(get_uow), _usuario=Depends(require_admin)):
    await EmpleadoService(uow).delete(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
