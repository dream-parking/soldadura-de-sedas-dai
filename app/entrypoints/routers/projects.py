"""app/entrypoints/routers/projects.py

Endpoints CRUD de Proyectos (US-17) y de sus asignaciones de personal (US-18).
Un Proyecto solo puede crearse a partir de una Cotización en estado Aprobado.
"""
from typing import List

from fastapi import APIRouter, Depends, status

from app.adapters.unit_of_work import AbstractUnitOfWork
from app.entrypoints.dependencies import get_unit_of_work
from app.entrypoints.schemas import (
    ProjectCreateFromQuote,
    ProjectRead,
    ProjectStatusUpdate,
    WorkerAssignmentRead,
)
from app.service_layer import services

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project_from_quote(
    payload: ProjectCreateFromQuote,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
) -> ProjectRead:
    with uow:
        project = services.crear_proyecto_desde_cotizacion(
            project_id=payload.project_id,
            quote_id=payload.quote_id,
            project_name=payload.project_name,
            project_location=payload.project_location,
            project_start_date=payload.project_start_date,
            quote_repo=uow.quotes,
            project_repo=uow.projects,
            project_estimated_end_date=payload.project_estimated_end_date,
        )
        return ProjectRead.model_validate(project)


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: str, uow: AbstractUnitOfWork = Depends(get_unit_of_work)
) -> ProjectRead:
    with uow:
        project = services.obtener_proyecto(project_id, uow.projects)
        return ProjectRead.model_validate(project)


@router.get("/by-client/{client_id}", response_model=List[ProjectRead])
def list_projects_by_client(
    client_id: str, uow: AbstractUnitOfWork = Depends(get_unit_of_work)
) -> List[ProjectRead]:
    with uow:
        projects = services.listar_proyectos_por_cliente(client_id, uow.clients, uow.projects)
        return [ProjectRead.model_validate(p) for p in projects]


@router.patch("/{project_id}/status", response_model=ProjectRead)
def update_project_status(
    project_id: str,
    payload: ProjectStatusUpdate,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
) -> ProjectRead:
    with uow:
        project = services.actualizar_estado_proyecto(
            project_id, payload.project_status, uow.projects
        )
        return ProjectRead.model_validate(project)


@router.get("/{project_id}/assignments", response_model=List[WorkerAssignmentRead])
def list_assignments_by_project(
    project_id: str, uow: AbstractUnitOfWork = Depends(get_unit_of_work)
) -> List[WorkerAssignmentRead]:
    with uow:
        assignments = services.listar_asignaciones_por_proyecto(
            project_id, uow.projects, uow.worker_assignments
        )
        return [WorkerAssignmentRead.model_validate(a) for a in assignments]