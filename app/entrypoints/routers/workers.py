"""app/entrypoints/routers/workers.py

Endpoints CRUD de Trabajadores y sus Asignaciones a Proyectos (US-18).
"""
from typing import List

from fastapi import APIRouter, Depends, status

from app.adapters.unit_of_work import AbstractUnitOfWork
from app.entrypoints.dependencies import get_unit_of_work
from app.entrypoints.schemas import (
    WorkerCreate,
    WorkerRead,
    WorkerAssignmentCreate,
    WorkerAssignmentRead,
)
from app.service_layer import services

router = APIRouter(prefix="/workers", tags=["workers"])


@router.post("", response_model=WorkerRead, status_code=status.HTTP_201_CREATED)
def create_worker(
    payload: WorkerCreate, uow: AbstractUnitOfWork = Depends(get_unit_of_work)
) -> WorkerRead:
    with uow:
        worker = services.registrar_trabajador(
            worker_id=payload.worker_id,
            worker_name=payload.worker_name,
            worker_role=payload.worker_role,
            worker_base_rate=payload.worker_base_rate,
            worker_repo=uow.workers,
        )
        return WorkerRead.model_validate(worker)


@router.get("", response_model=List[WorkerRead])
def list_workers(uow: AbstractUnitOfWork = Depends(get_unit_of_work)) -> List[WorkerRead]:
    with uow:
        workers = services.listar_trabajadores(uow.workers)
        return [WorkerRead.model_validate(w) for w in workers]


@router.get("/{worker_id}", response_model=WorkerRead)
def get_worker(
    worker_id: str, uow: AbstractUnitOfWork = Depends(get_unit_of_work)
) -> WorkerRead:
    with uow:
        worker = services.obtener_trabajador(worker_id, uow.workers)
        return WorkerRead.model_validate(worker)


@router.post(
    "/{worker_id}/assignments",
    response_model=WorkerAssignmentRead,
    status_code=status.HTTP_201_CREATED,
)
def assign_worker_to_project(
    worker_id: str,
    payload: WorkerAssignmentCreate,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
) -> WorkerAssignmentRead:
    with uow:
        assignment = services.asignar_trabajador_a_proyecto(
            assignment_id=payload.assignment_id,
            worker_id=worker_id,
            project_id=payload.project_id,
            assignment_date=payload.assignment_date,
            worker_repo=uow.workers,
            project_repo=uow.projects,
            assignment_repo=uow.worker_assignments,
        )
        return WorkerAssignmentRead.model_validate(assignment)


@router.get("/{worker_id}/assignments", response_model=List[WorkerAssignmentRead])
def list_assignments_by_worker(
    worker_id: str, uow: AbstractUnitOfWork = Depends(get_unit_of_work)
) -> List[WorkerAssignmentRead]:
    with uow:
        assignments = services.listar_asignaciones_por_trabajador(
            worker_id, uow.workers, uow.worker_assignments
        )
        return [WorkerAssignmentRead.model_validate(a) for a in assignments]