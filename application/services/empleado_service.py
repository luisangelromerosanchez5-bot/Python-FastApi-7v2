import logging
from fastapi import HTTPException
from domain.interfaces.unit_of_work import IUnitOfWork
from domain.entities.empleado import Empleado
from application.dtos.empleado_dto import (
    EmpleadoCreateDTO,
    EmpleadoUpdateDTO,
    EmpleadoResponseDTO,
    EmpleadoPagedResponseDTO,
)

logger = logging.getLogger(__name__)


class EmpleadoService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def get_all(self) -> list[EmpleadoResponseDTO]:
        async with self.uow:
            empleados = await self.uow.empleados.get_all()
            return [EmpleadoResponseDTO.model_validate(e) for e in empleados]

    async def get_paged(self, pagina: int = 1, tamano: int = 10, orden: str = "id", direccion: str = "asc", buscar: str | None = None, compania_id: int | None = None) -> EmpleadoPagedResponseDTO:
        if pagina < 1:
            raise HTTPException(status_code=400, detail="La pagina debe ser mayor o igual a 1")
        if tamano < 1 or tamano > 100:
            raise HTTPException(status_code=400, detail="El tamano debe estar entre 1 y 100")
        if direccion.lower() not in ("asc", "desc"):
            raise HTTPException(status_code=400, detail="La direccion debe ser asc o desc")

        async with self.uow:
            if compania_id is not None and not await self.uow.companias.get_by_id(compania_id):
                raise HTTPException(status_code=404, detail=f"Compania con ID {compania_id} no encontrada")
            empleados, total = await self.uow.empleados.get_paged(pagina, tamano, orden, direccion, buscar, compania_id)
            total_paginas = (total + tamano - 1) // tamano if total else 0
            return EmpleadoPagedResponseDTO(
                datos=[EmpleadoResponseDTO.model_validate(e) for e in empleados],
                pagina=pagina,
                tamano=tamano,
                total=total,
                totalPaginas=total_paginas,
            )

    async def get_by_id(self, id: int) -> EmpleadoResponseDTO:
        async with self.uow:
            empleado = await self.uow.empleados.get_by_id(id)
            if not empleado:
                raise HTTPException(status_code=404, detail=f"Empleado con ID {id} no encontrado")
            return EmpleadoResponseDTO.model_validate(empleado)

    async def get_by_compania(self, compania_id: int) -> list[EmpleadoResponseDTO]:
        async with self.uow:
            compania = await self.uow.companias.get_by_id(compania_id)
            if not compania:
                raise HTTPException(status_code=404, detail=f"Compania con ID {compania_id} no encontrada")
            empleados = await self.uow.empleados.get_by_compania(compania_id)
            return [EmpleadoResponseDTO.model_validate(e) for e in empleados]

    async def create(self, dto: EmpleadoCreateDTO) -> EmpleadoResponseDTO:
        async with self.uow:
            compania = await self.uow.companias.get_by_id(dto.compania_id)
            if not compania:
                raise HTTPException(status_code=404, detail="Compania no encontrada")

            existing = await self.uow.empleados.find_by_condition(Empleado.correo == dto.correo)
            if existing:
                raise HTTPException(status_code=400, detail="El correo electronico ya esta registrado")

            empleado = Empleado(
                nombre=dto.nombre,
                apellido=dto.apellido,
                correo=dto.correo,
                cargo=dto.cargo,
                salario=dto.salario,
                compania_id=dto.compania_id,
            )
            await self.uow.empleados.create(empleado)
            await self.uow.commit()
            return EmpleadoResponseDTO.model_validate(empleado)

    async def create_range(self, dtos: list[EmpleadoCreateDTO]) -> list[EmpleadoResponseDTO]:
        correos = [dto.correo for dto in dtos]
        if len(correos) != len(set(correos)):
            raise HTTPException(status_code=400, detail="La lista contiene correos duplicados")

        async with self.uow:
            empleados: list[Empleado] = []
            for dto in dtos:
                compania = await self.uow.companias.get_by_id(dto.compania_id)
                if not compania:
                    raise HTTPException(status_code=404, detail=f"Compania con ID {dto.compania_id} no encontrada")
                existing = await self.uow.empleados.find_by_condition(Empleado.correo == dto.correo)
                if existing:
                    raise HTTPException(status_code=400, detail=f"El correo {dto.correo} ya esta registrado")
                empleados.append(
                    Empleado(
                        nombre=dto.nombre,
                        apellido=dto.apellido,
                        correo=dto.correo,
                        cargo=dto.cargo,
                        salario=dto.salario,
                        compania_id=dto.compania_id,
                    )
                )
            await self.uow.empleados.create_range(empleados)
            await self.uow.commit()
            return [EmpleadoResponseDTO.model_validate(e) for e in empleados]

    async def update(self, id: int, dto: EmpleadoUpdateDTO) -> EmpleadoResponseDTO:
        async with self.uow:
            empleado = await self.uow.empleados.get_by_id(id)
            if not empleado:
                raise HTTPException(status_code=404, detail=f"Empleado con ID {id} no encontrado")

            if dto.nombre is not None:
                empleado.nombre = dto.nombre
            if dto.apellido is not None:
                empleado.apellido = dto.apellido
            if dto.cargo is not None:
                empleado.cargo = dto.cargo
            if dto.salario is not None:
                empleado.salario = dto.salario
            if dto.correo is not None and dto.correo != empleado.correo:
                existing = await self.uow.empleados.find_by_condition(Empleado.correo == dto.correo)
                if existing:
                    raise HTTPException(status_code=400, detail="El correo electronico ya esta registrado")
                empleado.correo = dto.correo

            await self.uow.empleados.update(empleado)
            await self.uow.commit()
            return EmpleadoResponseDTO.model_validate(empleado)

    async def patch(self, id: int, dto: EmpleadoUpdateDTO) -> EmpleadoResponseDTO:
        return await self.update(id, dto)

    async def delete(self, id: int) -> None:
        async with self.uow:
            empleado = await self.uow.empleados.get_by_id(id)
            if not empleado:
                raise HTTPException(status_code=404, detail=f"Empleado con ID {id} no encontrado")
            await self.uow.empleados.delete(empleado)
            await self.uow.commit()

    async def delete_range(self, ids: list[int]) -> None:
        if len(ids) != len(set(ids)):
            raise HTTPException(status_code=400, detail="La lista contiene IDs duplicados")

        async with self.uow:
            empleados = []
            for id in ids:
                empleado = await self.uow.empleados.get_by_id(id)
                if not empleado:
                    raise HTTPException(status_code=404, detail=f"Empleado con ID {id} no encontrado")
                empleados.append(empleado)
            await self.uow.empleados.delete_range(empleados)
            await self.uow.commit()
