import re
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator
from domain.entities.usuario import RolUsuario


class UsuarioRegistroDTO(BaseModel):
    nombre: str = Field(min_length=3, max_length=100)
    correo: str
    contrasena: str = Field(min_length=6, max_length=100)
    rol: RolUsuario = RolUsuario.USUARIO
    compania_id: int | None = Field(None, gt=0)

    @field_validator("correo")
    @classmethod
    def validate_correo(cls, v: str) -> str:
        regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(regex, v):
            raise ValueError("Formato de correo electrónico no válido")
        return v.lower()


class UsuarioLoginDTO(BaseModel):
    correo: str
    contrasena: str

    @field_validator("correo")
    @classmethod
    def normalize_correo(cls, v: str) -> str:
        return v.lower()


class UsuarioResponseDTO(BaseModel):
    id: int
    nombre: str
    correo: str
    rol: str
    compania_id: int | None
    fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponseDTO(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioResponseDTO
