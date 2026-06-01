from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from domain.entities import Base

if TYPE_CHECKING:
    from domain.entities.empleado import Empleado

class Compania(Base):
    __tablename__ = "companias"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    direccion: Mapped[str] = mapped_column(String(300), nullable=False)
    telefono: Mapped[str] = mapped_column(String(20), nullable=False)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    empleados: Mapped[List["Empleado"]] = relationship(
        "Empleado",
        back_populates="compania",
        cascade="all, delete-orphan"
    )
