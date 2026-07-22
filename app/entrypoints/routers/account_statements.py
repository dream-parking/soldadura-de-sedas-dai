"""
Endpoints de Estados de Cuenta contable por proyecto.
Un Estado de Cuenta siempre está asociado a un Proyecto existente.
"""
from typing import List

from fastapi import APIRouter, Depends, status

from app.adapters.unit_of_work import AbstractUnitOfWork
from app.entrypoints.dependencies import get_unit_of_work
from app.entrypoints.schemas import (
    AccountStatementCreate,
    AccountStatementPaymentUpdate,
    AccountStatementRead,
)
from app.service_layer import services

router = APIRouter(prefix="/account-statements", tags=["account-statements"])


@router.post("", response_model=AccountStatementRead, status_code=status.HTTP_201_CREATED)
def create_account_statement(
    payload: AccountStatementCreate,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
) -> AccountStatementRead:
    with uow:
        statement = services.registrar_estado_de_cuenta(
            statement_id=payload.id,
            project_id=payload.project_id,
            statement_date=payload.date,
            initial_budget=payload.initial_budget,
            amount_paid=payload.amount_paid,
            project_repo=uow.projects,
            statement_repo=uow.account_statements,
        )
        return AccountStatementRead.model_validate(statement)


@router.get("/{statement_id}", response_model=AccountStatementRead)
def get_account_statement(
    statement_id: str, uow: AbstractUnitOfWork = Depends(get_unit_of_work)
) -> AccountStatementRead:
    with uow:
        statement = services.obtener_estado_de_cuenta(statement_id, uow.account_statements)
        return AccountStatementRead.model_validate(statement)


@router.get("/by-project/{project_id}", response_model=List[AccountStatementRead])
def list_account_statements_by_project(
    project_id: str, uow: AbstractUnitOfWork = Depends(get_unit_of_work)
) -> List[AccountStatementRead]:
    with uow:
        statements = services.listar_estados_de_cuenta_por_proyecto(
            project_id, uow.projects, uow.account_statements
        )
        return [AccountStatementRead.model_validate(s) for s in statements]


@router.patch("/{statement_id}/payment", response_model=AccountStatementRead)
def register_account_statement_payment(
    statement_id: str,
    payload: AccountStatementPaymentUpdate,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
) -> AccountStatementRead:
    with uow:
        statement = services.registrar_pago_estado_de_cuenta(
            statement_id, payload.amount_paid, uow.account_statements
        )
        return AccountStatementRead.model_validate(statement)
