"""
Endpoints de Solicitudes de desembolso quincenal por proyecto.
Una Solicitud Quincenal siempre está asociada a un Proyecto existente.
"""
from typing import List

from fastapi import APIRouter, Depends, status

from app.adapters.unit_of_work import AbstractUnitOfWork
from app.entrypoints.dependencies import get_unit_of_work
from app.entrypoints.schemas import (
    BiweeklyRequestCreate,
    BiweeklyRequestRead,
    BiweeklyRequestStatusUpdate,
)
from app.service_layer import services

router = APIRouter(prefix="/biweekly-requests", tags=["biweekly-requests"])


@router.post("", response_model=BiweeklyRequestRead, status_code=status.HTTP_201_CREATED)
def create_biweekly_request(
    payload: BiweeklyRequestCreate,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
) -> BiweeklyRequestRead:
    with uow:
        request = services.registrar_solicitud_quincenal(
            request_id=payload.id,
            project_id=payload.project_id,
            request_date=payload.date,
            status=payload.status,
            amount=payload.amount,
            notes=payload.notes,
            project_repo=uow.projects,
            request_repo=uow.biweekly_requests,
        )
        return BiweeklyRequestRead.model_validate(request)


@router.get("/{request_id}", response_model=BiweeklyRequestRead)
def get_biweekly_request(
    request_id: str, uow: AbstractUnitOfWork = Depends(get_unit_of_work)
) -> BiweeklyRequestRead:
    with uow:
        request = services.obtener_solicitud_quincenal(request_id, uow.biweekly_requests)
        return BiweeklyRequestRead.model_validate(request)


@router.get("/by-project/{project_id}", response_model=List[BiweeklyRequestRead])
def list_biweekly_requests_by_project(
    project_id: str, uow: AbstractUnitOfWork = Depends(get_unit_of_work)
) -> List[BiweeklyRequestRead]:
    with uow:
        requests = services.listar_solicitudes_por_proyecto(
            project_id, uow.projects, uow.biweekly_requests
        )
        return [BiweeklyRequestRead.model_validate(r) for r in requests]


@router.patch("/{request_id}/status", response_model=BiweeklyRequestRead)
def update_biweekly_request_status(
    request_id: str,
    payload: BiweeklyRequestStatusUpdate,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
) -> BiweeklyRequestRead:
    with uow:
        request = services.actualizar_estado_solicitud_quincenal(
            request_id, payload.status, uow.biweekly_requests
        )
        return BiweeklyRequestRead.model_validate(request)
