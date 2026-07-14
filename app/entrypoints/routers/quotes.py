"""app/entrypoints/routers/quotes.py

Endpoints CRUD de Cotizaciones (US-16). Router delgado: valida con los
esquemas Pydantic y delega la lógica al service layer sobre el Unit of Work.
"""
from typing import List

from fastapi import APIRouter, Depends, status

from app.adapters.unit_of_work import AbstractUnitOfWork
from app.entrypoints.dependencies import get_unit_of_work
from app.entrypoints.schemas import QuoteCreate, QuoteRead, QuoteStatusUpdate
from app.service_layer import services

router = APIRouter(prefix="/quotes", tags=["quotes"])


@router.post("", response_model=QuoteRead, status_code=status.HTTP_201_CREATED)
def create_quote(
    payload: QuoteCreate, uow: AbstractUnitOfWork = Depends(get_unit_of_work)
) -> QuoteRead:
    with uow:
        quote = services.crear_cotizacion(
            quote_id=payload.quote_id,
            client_id=payload.client_id,
            quote_issue_date=payload.quote_issue_date,
            quote_job_description=payload.quote_job_description,
            quote_estimated_amount=payload.quote_estimated_amount,
            client_repo=uow.clients,
            quote_repo=uow.quotes,
            notes=payload.notes,
        )
        return QuoteRead.model_validate(quote)


@router.get("/{quote_id}", response_model=QuoteRead)
def get_quote(
    quote_id: str, uow: AbstractUnitOfWork = Depends(get_unit_of_work)
) -> QuoteRead:
    with uow:
        quote = services.obtener_cotizacion(quote_id, uow.quotes)
        return QuoteRead.model_validate(quote)


@router.get("/by-client/{client_id}", response_model=List[QuoteRead])
def list_quotes_by_client(
    client_id: str, uow: AbstractUnitOfWork = Depends(get_unit_of_work)
) -> List[QuoteRead]:
    with uow:
        quotes = services.listar_cotizaciones_por_cliente(client_id, uow.clients, uow.quotes)
        return [QuoteRead.model_validate(q) for q in quotes]


@router.patch("/{quote_id}/status", response_model=QuoteRead)
def update_quote_status(
    quote_id: str,
    payload: QuoteStatusUpdate,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
) -> QuoteRead:
    with uow:
        quote = services.actualizar_estado_cotizacion(quote_id, payload.quote_status, uow.quotes)
        return QuoteRead.model_validate(quote)


@router.post("/{quote_id}/approve", response_model=QuoteRead)
def approve_quote(
    quote_id: str, uow: AbstractUnitOfWork = Depends(get_unit_of_work)
) -> QuoteRead:
    with uow:
        quote = services.aprobar_cotizacion(quote_id, uow.quotes)
        return QuoteRead.model_validate(quote)


@router.post("/{quote_id}/reject", response_model=QuoteRead)
def reject_quote(
    quote_id: str, uow: AbstractUnitOfWork = Depends(get_unit_of_work)
) -> QuoteRead:
    with uow:
        quote = services.rechazar_cotizacion(quote_id, uow.quotes)
        return QuoteRead.model_validate(quote)