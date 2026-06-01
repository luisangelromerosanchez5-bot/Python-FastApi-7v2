import re
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator

PHONE_REGEX = r"^\d{7,15}$"

class EmpleadoSinCompaniaDTO(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    apellido: str = Field(min_length=1, max_length=100)
    correo: str
    cargo: str = Field(min_length=1, max_length=100)
    salario: float = Field(gt=0)

    @field_validator("correo")
    @classmethod
    def validate_correo(cls, v: str) -> str:
        regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(regex, v):
            raise ValueError("Formato de correo electrónico no válido")
        return v

    model_config = ConfigDict(from_attributes=True)

class CompaniaCreateDTO(BaseModel):
    nombre: str = Field(min_length=3, max_length=100)
    direccion: str = Field(min_length=3, max_length=300)
    telefono: str

    @field_validator("telefono")
    @classmethod
    def validate_telefono(cls, v: str) -> str:
        if not re.match(PHONE_REGEX, v):
            raise ValueError("El teléfono debe tener solo dígitos y entre 7 y 15 caracteres")
        return v

class CompaniaUpdateDTO(BaseModel):
    nombre: str | None = Field(None, min_length=3, max_length=100)
    direccion: str | None = Field(None, min_length=3, max_length=300)
    telefono: str | None = None

    @field_validator("telefono")
    @classmethod
    def validate_telefono(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not re.match(PHONE_REGEX, v):
            raise ValueError("El teléfono debe tener solo dígitos y entre 7 y 15 caracteres")
        return v

class CompaniaResponseDTO(BaseModel):
    id: int
    nombre: str
    direccion: str
    telefono: str
    fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)

class CompaniaConEmpleadosCreateDTO(BaseModel):
    nombre: str
    direccion: str
    telefono: str
    empleados: list[EmpleadoSinCompaniaDTO]
