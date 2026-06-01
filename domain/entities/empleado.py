from typing import TYPE_CHECKING
from sqlalchemy import String, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from domain.entities import Base

if TYPE_CHECKING:
    from domain.entities.compania import Compania

class Empleado(Base):
    __tablename__ = "empleados"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido: Mapped[str] = mapped_column(String(100), nullable=False)
    correo: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    cargo: Mapped[str] = mapped_column(String(100), nullable=False)
    salario: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    compania_id: Mapped[int] = mapped_column(ForeignKey("companias.id"), nullable=False)

    compania: Mapped["Compania"] = relationship("Compania", back_populates="empleados")
