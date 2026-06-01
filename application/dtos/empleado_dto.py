import re
from pydantic import BaseModel, ConfigDict, Field, field_validator

class EmpleadoCreateDTO(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    apellido: str = Field(min_length=1, max_length=100)
    correo: str
    cargo: str = Field(min_length=1, max_length=100)
    salario: float = Field(gt=0)
    compania_id: int = Field(gt=0)

    @field_validator("correo")
    @classmethod
    def validate_correo(cls, v: str) -> str:
        regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(regex, v):
            raise ValueError("Formato de correo electrónico no válido")
        return v

class EmpleadoUpdateDTO(BaseModel):
    nombre: str | None = Field(None, min_length=1, max_length=100)
    apellido: str | None = Field(None, min_length=1, max_length=100)
    correo: str | None = None
    cargo: str | None = Field(None, min_length=1, max_length=100)
    salario: float | None = Field(None, gt=0)

    @field_validator("correo")
    @classmethod
    def validate_correo(cls, v: str | None) -> str | None:
        if v is None:
            return v
        regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(regex, v):
            raise ValueError("Formato de correo electrónico no válido")
        return v

class EmpleadoResponseDTO(BaseModel):
    id: int
    nombre: str
    apellido: str
    correo: str
    cargo: str
    salario: float
    compania_id: int = Field(exclude=True)

    model_config = ConfigDict(from_attributes=True)

class EmpleadoBulkCreateDTO(BaseModel):
    empleados: list[EmpleadoCreateDTO] = Field(min_length=1)

class EmpleadoDeleteRangeDTO(BaseModel):
    ids: list[int] = Field(min_length=1)

class EmpleadoPagedResponseDTO(BaseModel):
    datos: list[EmpleadoResponseDTO]
    pagina: int
    tamano: int
    total: int
    totalPaginas: int
