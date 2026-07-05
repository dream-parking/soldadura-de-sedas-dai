"""app/entrypoints/routers/clients.py

Endpoints CRUD de Clientes (US-15). El router es delgado: valida con los
esquemas Pydantic y delega toda la lógica al service layer, que a su vez
opera sobre el Unit of Work inyectado.
"""
from typing import List

from fastapi import APIRouter, Depends, status

from app.adapters.unit_of_work import AbstractUnitOfWork
from app.entrypoints.dependencies import get_unit_of_work
from app.entrypoints.schemas import ClientCreate, ClientRead, ClientUpdate
from app.service_layer import services

router = APIRouter(prefix="/clients", tags=["clients"])


@router.post("", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
def create_client(
    payload: ClientCreate, uow: AbstractUnitOfWork = Depends(get_unit_of_work)
) -> ClientRead:
    with uow:
        client = services.registrar_cliente(
            client_id=payload.client_id,
            client_company_name=payload.client_company_name,
            client_phone=payload.client_phone,
            registration_date=payload.registration_date,
            client_repo=uow.clients,
            client_email=payload.client_email,
        )
        return ClientRead.model_validate(client)


@router.get("", response_model=List[ClientRead])
def list_clients(uow: AbstractUnitOfWork = Depends(get_unit_of_work)) -> List[ClientRead]:
    with uow:
        clients = services.listar_clientes(uow.clients)
        return [ClientRead.model_validate(c) for c in clients]


@router.get("/{client_id}", response_model=ClientRead)
def get_client(
    client_id: str, uow: AbstractUnitOfWork = Depends(get_unit_of_work)
) -> ClientRead:
    with uow:
        client = services.obtener_cliente(client_id, uow.clients)
        return ClientRead.model_validate(client)


@router.put("/{client_id}", response_model=ClientRead)
def update_client(
    client_id: str,
    payload: ClientUpdate,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
) -> ClientRead:
    with uow:
        client = services.actualizar_cliente(
            client_id=client_id,
            client_company_name=payload.client_company_name,
            client_phone=payload.client_phone,
            registration_date=payload.registration_date,
            client_repo=uow.clients,
            client_email=payload.client_email,
        )
        return ClientRead.model_validate(client)
