from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.adapters.unit_of_work import AbstractUnitOfWork
from app.entrypoints.dependencies import get_unit_of_work
from app.entrypoints.schemas import (
    MaterialUsageDetailCreate,
    MaterialUsageDetailRead,
    MaterialUsageDetailUpdate,
)
from app.service_layer import services

router = APIRouter(
    prefix="/material-usage-details",
    tags=["Material Usage Details"],
)


@router.post(
    "/",
    response_model=MaterialUsageDetailRead,
    status_code=status.HTTP_201_CREATED,
)
def create_material_usage_detail(
    schema: MaterialUsageDetailCreate,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
):
    """
    Registra un nuevo detalle de uso de material en una obra.
    """
    with uow:
        detail = services.create_material_usage_detail(schema=schema, uow=uow)
        uow.commit()
    return detail


@router.get(
    "/",
    response_model=List[MaterialUsageDetailRead],
    status_code=status.HTTP_200_OK,
)
def list_material_usage_details(
    skip: int = 0,
    limit: int = 100,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
):
    """
    Lista los registros de uso de materiales con paginación básica.
    """
    with uow:
        details = services.get_material_usage_details(
            skip=skip, limit=limit, uow=uow
        )
    return details


@router.get(
    "/{detail_id}",
    response_model=MaterialUsageDetailRead,
    status_code=status.HTTP_200_OK,
)
def get_material_usage_detail(
    detail_id: int,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
):
    """
    Obtiene un registro específico de uso de material por su ID.
    """
    with uow:
        detail = services.get_material_usage_detail_by_id(
            detail_id=detail_id, uow=uow
        )
        if not detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Detalle de uso con ID {detail_id} no encontrado",
            )
    return detail


@router.patch(
    "/{detail_id}",
    response_model=MaterialUsageDetailRead,
    status_code=status.HTTP_200_OK,
)
def update_material_usage_detail(
    detail_id: int,
    schema: MaterialUsageDetailUpdate,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
):
    """
    Actualiza parcialmente un registro de uso de material existente.
    """
    with uow:
        detail = services.update_material_usage_detail(
            detail_id=detail_id, schema=schema, uow=uow
        )
        if not detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Detalle de uso con ID {detail_id} no encontrado",
            )
        uow.commit()
    return detail


@router.delete(
    "/{detail_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_material_usage_detail(
    detail_id: int,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
):
    """
    Elimina un registro de uso de material.
    """
    with uow:
        success = services.delete_material_usage_detail(
            detail_id=detail_id, uow=uow
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Detalle de uso con ID {detail_id} no encontrado",
            )
        uow.commit()
    return None