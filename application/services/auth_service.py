from fastapi import HTTPException, status
from application.dtos.auth_dto import UsuarioLoginDTO, UsuarioRegistroDTO, UsuarioResponseDTO, TokenResponseDTO
from domain.entities.usuario import Usuario
from domain.interfaces.unit_of_work import IUnitOfWork
from infrastructure.security.jwt_service import JwtService
from infrastructure.security.password_hasher import PasswordHasher


class AuthService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow
        self.password_hasher = PasswordHasher()
        self.jwt_service = JwtService()

    async def registrar(self, dto: UsuarioRegistroDTO) -> UsuarioResponseDTO:
        async with self.uow:
            if await self.uow.usuarios.get_by_correo(dto.correo):
                raise HTTPException(status_code=400, detail="El correo ya esta registrado")
            if dto.compania_id is not None and not await self.uow.companias.get_by_id(dto.compania_id):
                raise HTTPException(status_code=404, detail="Compania no encontrada")
            if dto.rol.value == "ADMIN" and not dto.ciudad:
                raise HTTPException(status_code=400, detail="La ciudad es obligatoria para usuarios ADMIN")

            usuario = Usuario(
                nombre=dto.nombre,
                correo=dto.correo,
                contrasena_hash=self.password_hasher.hash(dto.contrasena),
                rol=dto.rol.value,
                ciudad=dto.ciudad,
                compania_id=dto.compania_id,
            )
            await self.uow.usuarios.create(usuario)
            await self.uow.commit()
            return UsuarioResponseDTO.model_validate(usuario)

    async def login(self, dto: UsuarioLoginDTO) -> TokenResponseDTO:
        async with self.uow:
            usuario = await self.uow.usuarios.get_by_correo(dto.correo)
            if not usuario or not self.password_hasher.verify(dto.contrasena, usuario.contrasena_hash):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales invalidas")

            usuario_dto = UsuarioResponseDTO.model_validate(usuario)
            token = self.jwt_service.create_token(
                {
                    "sub": str(usuario.id),
                    "correo": usuario.correo,
                    "rol": usuario.rol,
                    "ciudad": usuario.ciudad,
                    "compania_id": usuario.compania_id,
                    "permisos": ["empleados:eliminar"] if usuario.rol == "ADMIN" else [],
                }
            )
            return TokenResponseDTO(access_token=token, usuario=usuario_dto)
