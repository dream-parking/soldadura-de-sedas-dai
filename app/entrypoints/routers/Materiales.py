""" app/entrypoints/routers/Materiales.py
"""
from typing import List
from fastapi import APIRouter, Depends, status
from app.adapters.unit_of_work import AbstractUnitOfWork
from app.entrypoints.dependencies import get_unit_of_work
from app.entrypoints.schemas import MaterialBase, MaterialRead, MaterialUpdate
from app.service_layer import services

router = APIRouter(prefix="/materiales", tags=["materiales"])

@router.post("", response_model=MaterialRead, status_code=status.HTTP_201_CREATED)
def create_material(payload: MaterialBase, uow: AbstractUnitOfWork = Depends(get_unit_of_work)) -> MaterialRead:
    with uow:
        material = services.agregar_material(
            id=payload.id,
            description=payload.description,
            specifications=payload.specifications,
            material_repo=uow.materiales
        )
        return MaterialRead.model_validate(material)

@router.get("", response_model=List[MaterialRead])
def list_materiales(uow: AbstractUnitOfWork = Depends(get_unit_of_work)) -> List[MaterialRead]:
    with uow:
        materiales = services.listar_materiales(uow.materiales)
        return [MaterialRead.model_validate(m) for m in materiales]

@router.get("/{material_id}", response_model=MaterialRead)
def get_material(material_id:str, uow: AbstractUnitOfWork = Depends(get_unit_of_work)) -> MaterialRead:
    with uow:
        material = services.obtener_material(material_id, uow.materiales)
        return MaterialRead.model_validate(material)
    
@router.put("/{material_id}", response_model=MaterialRead)
def update_material(
    material_id: str,
    payload: MaterialUpdate,
    uow: AbstractUnitOfWork = Depends(get_unit_of_work),
) -> MaterialRead:
    with uow:
        material = services.actualizar_material(
            material_id=material_id,
            description=payload.description,
            specifications=payload.specifications,
            material_repo=uow.materiales
        )
        return MaterialRead.model_validate(material)