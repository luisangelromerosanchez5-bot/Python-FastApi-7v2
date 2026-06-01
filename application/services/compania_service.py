import logging
from fastapi import HTTPException
from domain.interfaces.unit_of_work import IUnitOfWork
from domain.entities.compania import Compania
from domain.entities.empleado import Empleado
from application.dtos.compania_dto import (
    CompaniaCreateDTO,
    CompaniaUpdateDTO,
    CompaniaResponseDTO,
    CompaniaConEmpleadosCreateDTO,
)

logger = logging.getLogger(__name__)


class CompaniaService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def get_all(self) -> list[CompaniaResponseDTO]:
        async with self.uow:
            companias = await self.uow.companias.get_all()
            return [CompaniaResponseDTO.model_validate(c) for c in companias]

    async def get_by_id(self, id: int) -> CompaniaResponseDTO:
        async with self.uow:
            compania = await self.uow.companias.get_by_id(id)
            if not compania:
                raise HTTPException(status_code=404, detail=f"Compania con ID {id} no encontrada")
            return CompaniaResponseDTO.model_validate(compania)

    async def create(self, dto: CompaniaCreateDTO) -> CompaniaResponseDTO:
        async with self.uow:
            compania = Compania(nombre=dto.nombre, direccion=dto.direccion, telefono=dto.telefono)
            await self.uow.companias.create(compania)
            await self.uow.commit()
            return CompaniaResponseDTO.model_validate(compania)

    async def update(self, id: int, dto: CompaniaUpdateDTO) -> CompaniaResponseDTO:
        async with self.uow:
            compania = await self.uow.companias.get_by_id(id)
            if not compania:
                raise HTTPException(status_code=404, detail=f"Compania con ID {id} no encontrada")

            if dto.nombre is not None:
                compania.nombre = dto.nombre
            if dto.direccion is not None:
                compania.direccion = dto.direccion
            if dto.telefono is not None:
                compania.telefono = dto.telefono

            await self.uow.companias.update(compania)
            await self.uow.commit()
            return CompaniaResponseDTO.model_validate(compania)

    async def delete(self, id: int) -> None:
        async with self.uow:
            compania = await self.uow.companias.get_by_id(id)
            if not compania:
                raise HTTPException(status_code=404, detail=f"Compania con ID {id} no encontrada")
            await self.uow.companias.delete(compania)
            await self.uow.commit()

    async def get_con_empleados(self, id: int) -> dict:
        async with self.uow:
            compania = await self.uow.companias.get_with_empleados(id)
            if not compania:
                raise HTTPException(status_code=404, detail=f"Compania con ID {id} no encontrada")
            return {
                "id": compania.id,
                "nombre": compania.nombre,
                "direccion": compania.direccion,
                "telefono": compania.telefono,
                "fecha_creacion": compania.fecha_creacion,
                "empleados": [
                    {
                        "id": emp.id,
                        "nombre": emp.nombre,
                        "apellido": emp.apellido,
                        "correo": emp.correo,
                        "cargo": emp.cargo,
                        "salario": float(emp.salario),
                        "compania_id": emp.compania_id,
                    }
                    for emp in compania.empleados
                ],
            }

    async def create_con_empleados(self, dto: CompaniaConEmpleadosCreateDTO) -> CompaniaResponseDTO:
        correos = [emp.correo for emp in dto.empleados]
        if len(correos) != len(set(correos)):
            raise HTTPException(status_code=400, detail="La lista contiene correos duplicados")

        async with self.uow:
            compania = Compania(nombre=dto.nombre, direccion=dto.direccion, telefono=dto.telefono)
            await self.uow.companias.create(compania)

            for emp_dto in dto.empleados:
                existing = await self.uow.empleados.find_by_condition(Empleado.correo == emp_dto.correo)
                if existing:
                    raise HTTPException(status_code=400, detail=f"El correo {emp_dto.correo} ya esta registrado")
                empleado = Empleado(
                    nombre=emp_dto.nombre,
                    apellido=emp_dto.apellido,
                    correo=emp_dto.correo,
                    cargo=emp_dto.cargo,
                    salario=emp_dto.salario,
                    compania=compania,
                )
                await self.uow.empleados.create(empleado)

            await self.uow.commit()
            return CompaniaResponseDTO.model_validate(compania)
