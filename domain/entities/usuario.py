from datetime import datetime
from enum import Enum
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from domain.entities import Base


class RolUsuario(str, Enum):
    ADMIN = "ADMIN"
    USUARIO = "USUARIO"


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    correo: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    contrasena_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[str] = mapped_column(String(20), nullable=False, default=RolUsuario.USUARIO.value)
    ciudad: Mapped[str | None] = mapped_column(String(100), nullable=True)
    compania_id: Mapped[int | None] = mapped_column(ForeignKey("companias.id"), nullable=True)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
