from fastapi import APIRouter, Depends, Response, status
from domain.interfaces.unit_of_work import IUnitOfWork
from infrastructure.unit_of_work.unit_of_work_impl import get_uow
from application.services.compania_service import CompaniaService
from application.services.empleado_service import EmpleadoService
from application.dtos.compania_dto import (
    CompaniaConEmpleadosCreateDTO,
    CompaniaCreateDTO,
    CompaniaResponseDTO,
    CompaniaUpdateDTO,
)
from application.dtos.empleado_dto import EmpleadoPagedResponseDTO
from api.middlewares.security import require_admin_city_policy, require_roles_with_admin_city_policy

router = APIRouter(prefix="/api/companias", tags=["Companias"])


@router.get("", response_model=list[CompaniaResponseDTO])
async def get_all(uow: IUnitOfWork = Depends(get_uow), _usuario=Depends(require_roles_with_admin_city_policy("GET", "ADMIN", "USUARIO"))):
    return await CompaniaService(uow).get_all()


@router.post("/con-empleados", response_model=CompaniaResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_con_empleados(dto: CompaniaConEmpleadosCreateDTO, uow: IUnitOfWork = Depends(get_uow), _usuario=Depends(require_admin_city_policy("POST"))):
    return await CompaniaService(uow).create_con_empleados(dto)


@router.get("/{id}", response_model=CompaniaResponseDTO)
async def get_by_id(id: int, uow: IUnitOfWork = Depends(get_uow), _usuario=Depends(require_roles_with_admin_city_policy("GET", "ADMIN", "USUARIO"))):
    return await CompaniaService(uow).get_by_id(id)


@router.post("", response_model=CompaniaResponseDTO, status_code=status.HTTP_201_CREATED)
async def create(dto: CompaniaCreateDTO, uow: IUnitOfWork = Depends(get_uow), _usuario=Depends(require_roles_with_admin_city_policy("POST", "ADMIN", "USUARIO"))):
    return await CompaniaService(uow).create(dto)


@router.put("/{id}", response_model=CompaniaResponseDTO)
async def update(id: int, dto: CompaniaUpdateDTO, uow: IUnitOfWork = Depends(get_uow), _usuario=Depends(require_roles_with_admin_city_policy("PUT", "ADMIN", "USUARIO"))):
    return await CompaniaService(uow).update(id, dto)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(id: int, uow: IUnitOfWork = Depends(get_uow), _usuario=Depends(require_admin_city_policy("DELETE"))):
    await CompaniaService(uow).delete(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{id}/empleados", response_model=EmpleadoPagedResponseDTO)
async def get_empleados(id: int, pagina: int = 1, tamano: int = 10, uow: IUnitOfWork = Depends(get_uow), _usuario=Depends(require_roles_with_admin_city_policy("GET", "ADMIN", "USUARIO"))):
    return await EmpleadoService(uow).get_paged(pagina=pagina, tamano=tamano, compania_id=id)
