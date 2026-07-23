from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.adapters.unit_of_work import AbstractUnitOfWork
from app.entrypoints.dependencies import get_unit_of_work
from app.entrypoints.schemas import (
    TechnicalMeasurementCreate,
    TechnicalMeasurementRead,
    create_technical_measurement,
    get_technical_measurement_by_id,
    get_technical_measurements,
    update_technical_measurement,
    delete_technical_measurement
)
from app.service_layer import services


# Esquema auxiliar para actualizaciones parciales
class TechnicalMeasurementUpdate(BaseModel):
    project_id: str | None = Field(None, min_length=1, max_length=5)
    dimensions: int | None = Field(None, gt=0)
    structure_type: str | None = Field(None, min_length=1, max_length=100)
    payment: float | None = Field(None, ge=0)
    unit: str | None = Field(None, min_length=1, max_length=10)
    notes: str | None = Field(None, min_length=1, max_length=300)


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
        measurement = services.create_technical_measurement(schema=schema, uow=uow)
        uow.commit()
    return measurement


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
        measurements = services.get_technical_measurements(
            skip=skip, limit=limit, uow=uow
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
        measurement = services.get_technical_measurement_by_id(
            measurement_id=measurement_id, uow=uow
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
        measurement = services.update_technical_measurement(
            measurement_id=measurement_id, schema=schema, uow=uow
        )
        if not measurement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Medición técnica con ID '{measurement_id}' no encontrada",
            )
        uow.commit()
    return measurement


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
            measurement_id=measurement_id, uow=uow
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Medición técnica con ID '{measurement_id}' no encontrada",
            )
        uow.commit()
    return None