from typing import List
 
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
 
from app.adapters.unit_of_work import AbstractUnitOfWork
from app.entrypoints.dependencies import get_unit_of_work
from app.entrypoints.schemas import (
    TechnicalMeasurementCreate,
    TechnicalMeasurementRead,
    TechnicalMeasurementUpdate,
)
from app.service_layer import services
 
 
router = APIRouter(
    prefix="/technical-measurements",
    tags=["Technical Measurements"],
)
 
 
@router.post(
    "/",
    response_model=TechnicalMeasurementRead,
    status_code=status.HTTP_201_CREATED,
)
def create_technical_measurement(
    schema: TechnicalMeasurementCreate,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
):
    """
    Crea un nuevo registro de medición técnica.
    """
    with uow:
        measurement = services.registrar_medida_tecnica(
            measurement_id=schema.id,
            project_id=schema.project_id,
            dimensions=schema.dimensions,
            structure_type=schema.structure_type,
            payment=schema.payment,
            unit=schema.unit,
            notes=schema.notes,
            project_repo=uow.projects,
            measurement_repo=uow.technical_measurements,
        )
<<<<<<< HEAD
        return TechnicalMeasurementRead.model_validate(measurement)
=======
        uow.commit()
        return measurement
>>>>>>> 8bb0fe2c1eedd99884111581a69bc3a2301a9d12
 
 
@router.get(
    "/",
    response_model=List[TechnicalMeasurementRead],
    status_code=status.HTTP_200_OK,
)
def list_technical_measurements(
    skip: int = 0,
    limit: int = 100,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
):
    """
    Obtiene el listado de mediciones técnicas con paginación básica.
    """
    with uow:
        measurements = services.listar_medidas_tecnicas(
            measurement_repo=uow.technical_measurements
        )
        return measurements
 
 
@router.get(
    "/{measurement_id}",
    response_model=TechnicalMeasurementRead,
    status_code=status.HTTP_200_OK,
)
def get_technical_measurement(
    measurement_id: str,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
):
    """
    Obtiene una medición técnica por su identificador (ID alfanumérico).
    """
    with uow:
        measurement = services.obtener_medida_tecnica(
            measurement_id=measurement_id,
            measurement_repo=uow.technical_measurements,
        )
        if not measurement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Medición técnica con ID '{measurement_id}' no encontrada",
            )
        return measurement
 
 
@router.patch(
    "/{measurement_id}",
    response_model=TechnicalMeasurementRead,
    status_code=status.HTTP_200_OK,
)
def update_technical_measurement(
    measurement_id: str,
    schema: TechnicalMeasurementUpdate,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
):
    """
    Actualiza parcialmente una medición técnica existente.
    """
    with uow:
        measurement = services.actualizar_medida_tecnica(
            measurement_id=measurement_id,
            project_id=schema.project_id,
            dimensions=schema.dimensions,
            structure_type=schema.structure_type,
            payment=schema.payment,
            unit=schema.unit,
            notes=schema.notes,
            measurement_repo=uow.technical_measurements,
        )
        if not measurement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Medición técnica con ID '{measurement_id}' no encontrada",
            )
<<<<<<< HEAD
        return TechnicalMeasurementRead.model_validate(measurement)
=======
        uow.commit()
        return measurement
>>>>>>> 8bb0fe2c1eedd99884111581a69bc3a2301a9d12
 
 
@router.delete(
    "/{measurement_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_technical_measurement(
    measurement_id: str,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
):
    """
    Elimina un registro de medición técnica por su ID.
    """
    with uow:
        success = services.delete_technical_measurement(
            measurement_id=measurement_id,
            measurement_repo=uow.technical_measurements,
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Medición técnica con ID '{measurement_id}' no encontrada",
            )
        uow.commit()
    return None