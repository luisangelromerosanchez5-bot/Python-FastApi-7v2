from fastapi import APIRouter, Depends
from application.dtos.auth_dto import TokenResponseDTO, UsuarioLoginDTO, UsuarioRegistroDTO, UsuarioResponseDTO
from application.services.auth_service import AuthService
from api.middlewares.security import get_current_user
from domain.entities.usuario import Usuario
from domain.interfaces.unit_of_work import IUnitOfWork
from infrastructure.unit_of_work.unit_of_work_impl import get_uow

router = APIRouter(prefix="/api/auth", tags=["Autenticacion"])


@router.post("/registro", response_model=UsuarioResponseDTO, status_code=201)
async def registro(dto: UsuarioRegistroDTO, uow: IUnitOfWork = Depends(get_uow)):
    return await AuthService(uow).registrar(dto)


@router.post("/login", response_model=TokenResponseDTO)
async def login(dto: UsuarioLoginDTO, uow: IUnitOfWork = Depends(get_uow)):
    return await AuthService(uow).login(dto)


@router.get("/perfil", response_model=UsuarioResponseDTO)
async def perfil(usuario: Usuario = Depends(get_current_user)):
    return UsuarioResponseDTO.model_validate(usuario)
