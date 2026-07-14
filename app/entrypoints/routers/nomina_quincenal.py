""" app/entrypoints/routers/nomica_quincenal.py
"""
from typing import List
from fastapi import APIRouter, Depends, status
from app.adapters.unit_of_work import AbstractUnitOfWork
from app.entrypoints.dependencies import get_unit_of_work
from app.entrypoints.schemas import PayrollBase, PayrollRead,  PayrollUpdate
from app.service_layer import services

router = APIRouter(prefix="/nomina_quincenal", tags=["nomina_quincenal"])

@router.post("", response_model=PayrollRead, status_code=status.HTTP_201_CREATED)
def create_nomina_quincenal(payload: PayrollBase, uow: AbstractUnitOfWork = Depends(get_unit_of_work)) -> PayrollRead:
    with uow:
        nomina_quincenal = services.registrar_nomina_quincenal(
            payroll_id=payload.payroll_id,
            worker_id=payload.worker_id,
            project_id=payload.project_id,
            payroll_fortnight_period=payload.payroll_fortnight_period,
            payroll_payment_date=payload.payroll_payment_date,
            payroll_hours_worked=payload.payroll_hours_worked,
            payroll_paid_amount=payload.payroll_paid_amount,
            payroll_repo=uow.nomina_quincenal
        )
        return PayrollRead.model_validate(nomina_quincenal)

@router.get("", response_model=List[PayrollRead])
def list_nomina_quincenal(uow: AbstractUnitOfWork = Depends(get_unit_of_work)) -> List[PayrollRead]:
    with uow:
        nominas_quincenales = services.listar_nomina_quincenal(uow.nomina_quincenal)
        return [PayrollRead.model_validate(nq) for nq in nominas_quincenales]   

@router.get("/{payroll_id}", response_model=PayrollRead)
def get_nomina_quincenal(payroll_id: str, uow: AbstractUnitOfWork = Depends(get_unit_of_work)) -> PayrollRead:
    with uow:
        nomina_quincenal = services.obtener_nomina_quincenal(payroll_id, uow.nomina_quincenal)
        return PayrollRead.model_validate(nomina_quincenal) 

@router.put("/{payroll_id}", response_model=PayrollRead)
def update_nomina_quincenal(
    payroll_id: str,
    payload: PayrollUpdate,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
) -> PayrollRead:
    with uow:
        nomina_quincenal = services.actualizar_nomina_quincenal(
            worker_id=payload.worker_id,
            project_id=payload.project_id,
            payroll_fortnight_period=payload.payroll_fortnight_period,
            payroll_payment_date=payload.payroll_payment_date,
            payroll_hours_worked=payload.payroll_hours_worked,
            payroll_paid_amount=payload.payroll_paid_amount,
            payroll_repo=uow.nomina_quincenal
        )
        return PayrollRead.model_validate(nomina_quincenal)