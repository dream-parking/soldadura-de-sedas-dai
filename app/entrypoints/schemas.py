"""app/entrypoints/schemas.py

Esquemas Pydantic (Request/Response) para las entidades del dominio.
Validan tipos, longitudes y formatos antes de que los datos lleguen al service layer
(Architecture Patterns with Python, Cap. 4 — la capa de presentación no debe confiar
en datos sin validar).

Los límites de longitud reflejan las columnas definidas en app/adapters/orm.py.
Cada entidad expone:
  - <Entidad>Base: campos comunes.
  - <Entidad>Create: esquema de entrada (request body) para crear el recurso.
  - <Entidad>Read: esquema de salida (response), construible desde el objeto de
    dominio vía `model_validate(obj)` gracias a `from_attributes=True`.

Nota: `Material.id` se tipa como `str` (no `int`) porque así lo espera la columna
real en app/adapters/orm.py (String(5)) y el resto de identificadores del dominio.
"""
from datetime import date
from typing import List, Literal, Optional

from app.adapters.unit_of_work import AbstractUnitOfWork
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# Clientes

class ClientBase(BaseModel):
    client_id: str = Field(..., min_length=1, max_length=50)
    client_company_name: str = Field(..., min_length=1, max_length=200)
    client_phone: str = Field(..., min_length=1, max_length=30)
    registration_date: date
    client_email: Optional[EmailStr] = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    """Body para actualizar un cliente existente; el client_id viene de la URL."""

    client_company_name: str = Field(..., min_length=1, max_length=200)
    client_phone: str = Field(..., min_length=1, max_length=30)
    registration_date: date
    client_email: Optional[EmailStr] = None


class ClientRead(ClientBase):
    model_config = ConfigDict(from_attributes=True)


# Cotizaciones

class QuoteBase(BaseModel):
    quote_id: str = Field(..., min_length=1, max_length=50)
    client_id: str = Field(..., min_length=1, max_length=50)
    quote_issue_date: date
    quote_job_description: str = Field(..., min_length=1, max_length=500)
    quote_estimated_amount: float = Field(..., ge=0)
    quote_status: Literal["Pendiente", "Aprobado", "Rechazado"]
    notes: Optional[str] = Field(default=None, max_length=500)


class QuoteCreate(BaseModel):
    """Body para crear una cotización; el estado inicial siempre es 'Pendiente'
    y lo asigna el service layer, por lo que no se solicita aquí."""

    quote_id: str = Field(..., min_length=1, max_length=50)
    client_id: str = Field(..., min_length=1, max_length=50)
    quote_issue_date: date
    quote_job_description: str = Field(..., min_length=1, max_length=500)
    quote_estimated_amount: float = Field(..., ge=0)
    notes: Optional[str] = Field(default=None, max_length=500)


class QuoteRead(QuoteBase):
    model_config = ConfigDict(from_attributes=True)


class QuoteStatusUpdate(BaseModel):
    """Body para cambiar el estado de una cotización."""

    quote_status: Literal["Pendiente", "Aprobado", "Rechazado"]


# Proyectos

class ProjectBase(BaseModel):
    project_id: str = Field(..., min_length=1, max_length=5)
    client_id: str = Field(..., min_length=1, max_length=50)
    quote_id: str = Field(..., min_length=1, max_length=50)
    project_name: str = Field(..., min_length=1, max_length=200)
    project_location: str = Field(..., min_length=1, max_length=200)
    project_start_date: date
    project_total_cost: float = Field(..., ge=0)
    project_status: Literal["In Progress", "Completed"]
    project_estimated_end_date: Optional[date] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectCreateFromQuote(BaseModel):
    """Body para crear un proyecto a partir de una cotización aprobada.
    client_id y project_total_cost se derivan de la cotización, por lo
    que no se solicitan aquí."""

    project_id: str = Field(..., min_length=1, max_length=5)
    quote_id: str = Field(..., min_length=1, max_length=50)
    project_name: str = Field(..., min_length=1, max_length=200)
    project_location: str = Field(..., min_length=1, max_length=200)
    project_start_date: date
    project_estimated_end_date: Optional[date] = None


class ProjectStatusUpdate(BaseModel):
    """Body para cambiar el estado de un proyecto."""

    project_status: Literal["In Progress", "Completed"]


class ProjectRead(ProjectBase):
    model_config = ConfigDict(from_attributes=True)


# Trabajadores

class WorkerBase(BaseModel):
    worker_id: str = Field(..., min_length=1, max_length=5)
    worker_name: str = Field(..., min_length=1, max_length=200)
    worker_role: str = Field(..., min_length=1, max_length=100)
    worker_base_rate: float = Field(..., ge=0)


class WorkerCreate(WorkerBase):
    pass


class WorkerRead(WorkerBase):
    model_config = ConfigDict(from_attributes=True)


# Asignación de personal

class WorkerAssignmentBase(BaseModel):
    assignment_id: str = Field(..., min_length=1, max_length=5)
    worker_id: str = Field(..., min_length=1, max_length=5)
    project_id: str = Field(..., min_length=1, max_length=5)
    assignment_date: date


class WorkerAssignmentCreate(BaseModel):
    """Body para asignar un trabajador a un proyecto; worker_id viene de la
    URL (/workers/{worker_id}/assignments), no se repite en el body."""

    assignment_id: str = Field(..., min_length=1, max_length=5)
    project_id: str = Field(..., min_length=1, max_length=5)
    assignment_date: date


class WorkerAssignmentRead(WorkerAssignmentBase):
    model_config = ConfigDict(from_attributes=True)


# Nómina

class PayrollBase(BaseModel):
    payroll_id: str = Field(..., min_length=1, max_length=5)
    worker_id: str = Field(..., min_length=1, max_length=5)
    project_id: str = Field(..., min_length=1, max_length=5)
    payroll_fortnight_period: str = Field(..., min_length=1, max_length=30)
    payroll_payment_date: date
    payroll_hours_worked: Optional[float] = Field(default=None, ge=0)
    payroll_paid_amount: Optional[float] = Field(default=None, ge=0)


class PayrollCreate(PayrollBase):
    pass


class PayrollRead(PayrollBase):
    model_config = ConfigDict(from_attributes=True)


class PayrollUpdate(BaseModel):
    """Body para actualizar un PayRoll existente; el client_id viene de la URL."""

    worker_id: str = Field(..., min_length=1, max_length=5)
    project_id: str = Field(..., min_length=1, max_length=5)
    payroll_fortnight_period: str = Field(..., min_length=1, max_length=30)
    payroll_payment_date: date
    payroll_hours_worked: Optional[float] = Field(default=None, ge=0)
    payroll_paid_amount: Optional[float] = Field(default=None, ge=0)


# Materiales

class MaterialBase(BaseModel):
    id: str = Field(..., min_length=1, max_length=5)
    description: str = Field(..., min_length=1, max_length=300)
    specifications: str = Field(..., min_length=1, max_length=300)


class MaterialCreate(MaterialBase):
    pass


class MaterialRead(MaterialBase):
    model_config = ConfigDict(from_attributes=True)


# Detalle de uso de materiales por obra

class MaterialUsageDetailBase(BaseModel):
    project_id: str = Field(..., min_length=1, max_length=5)
    material_id: str = Field(..., min_length=1, max_length=5)
    used_quantity: float = Field(..., gt=0)
    measurement_unit: str = Field(..., min_length=1, max_length=10)


class MaterialUsageDetailCreate(MaterialUsageDetailBase):
    pass


class MaterialUsageDetailUpdate(BaseModel):
    project_id: Optional[str] = Field(None, min_length=1, max_length=5)
    material_id: Optional[str] = Field(None, min_length=1, max_length=5)
    used_quantity: Optional[float] = Field(None, gt=0)
    measurement_unit: Optional[str] = Field(None, min_length=1, max_length=10)


class MaterialUsageDetailRead(MaterialUsageDetailBase):
    model_config = ConfigDict(from_attributes=True)


def create_material_usage_detail(
    schema: MaterialUsageDetailCreate, uow: AbstractUnitOfWork
):
    """
    Crea y persiste un nuevo detalle de uso de material.
    """
    usage_detail_data = schema.model_dump()
    new_detail = uow.material_usage_details.add(usage_detail_data)
    return new_detail


def get_material_usage_details(
    skip: int, limit: int, uow: AbstractUnitOfWork
) -> List:
    """
    Recupera una lista paginada de detalles de uso de material.
    """
    return uow.material_usage_details.get_all(skip=skip, limit=limit)


def get_material_usage_detail_by_id(
    detail_id: int, uow: AbstractUnitOfWork
) -> Optional[object]:
    """
    Obtiene un detalle de uso de material por su ID.
    """
    return uow.material_usage_details.get_by_id(detail_id)


def update_material_usage_detail(
    detail_id: int, schema: MaterialUsageDetailUpdate, uow: AbstractUnitOfWork
) -> Optional[object]:
    """
    Actualiza los campos presentes en el esquema de actualización.
    """
    detail = uow.material_usage_details.get_by_id(detail_id)
    if not detail:
        return None

    update_data = schema.model_dump(exclude_unset=True)
    updated_detail = uow.material_usage_details.update(detail_id, update_data)
    return updated_detail


def delete_material_usage_detail(
    detail_id: int, uow: AbstractUnitOfWork
) -> bool:
    """
    Elimina un detalle de uso de material si existe.
    """
    detail = uow.material_usage_details.get_by_id(detail_id)
    if not detail:
        return False

    uow.material_usage_details.delete(detail_id)
    return True


# Medición técnica

class TechnicalMeasurementBase(BaseModel):
    id: str = Field(..., min_length=1, max_length=5)
    project_id: str = Field(..., min_length=1, max_length=5)
    dimensions: int = Field(..., gt=0)
    structure_type: str = Field(..., min_length=1, max_length=100)
    payment: float = Field(..., ge=0)
    unit: str = Field(..., min_length=1, max_length=10)
    notes: str = Field(..., min_length=1, max_length=300)


class TechnicalMeasurementCreate(TechnicalMeasurementBase):
    pass


class TechnicalMeasurementUpdate(BaseModel):
    project_id: Optional[str] = Field(None, min_length=1, max_length=5)
    dimensions: Optional[int] = Field(None, gt=0)
    structure_type: Optional[str] = Field(None, min_length=1, max_length=100)
    payment: Optional[float] = Field(None, ge=0)
    unit: Optional[str] = Field(None, min_length=1, max_length=10)
    notes: Optional[str] = Field(None, min_length=1, max_length=300)


class TechnicalMeasurementRead(TechnicalMeasurementBase):
    model_config = ConfigDict(from_attributes=True)


def create_technical_measurement(
    schema: TechnicalMeasurementCreate, uow: AbstractUnitOfWork
):
    """
    Crea y persiste una nueva medición técnica.
    """
    measurement_data = schema.model_dump()
    new_measurement = uow.technical_measurements.add(measurement_data)
    return new_measurement


def get_technical_measurements(
    skip: int, limit: int, uow: AbstractUnitOfWork
) -> List:
    """
    Recupera una lista paginada de mediciones técnicas.
    """
    return uow.technical_measurements.get_all(skip=skip, limit=limit)


def get_technical_measurement_by_id(
    measurement_id: str, uow: AbstractUnitOfWork
) -> Optional[object]:
    """
    Obtiene una medición técnica por su ID (alfanumérico).
    """
    return uow.technical_measurements.get_by_id(measurement_id)


def update_technical_measurement(
    measurement_id: str,
    schema: TechnicalMeasurementUpdate,
    uow: AbstractUnitOfWork,
) -> Optional[object]:
    """
    Actualiza parcialmente una medición técnica.
    """
    measurement = uow.technical_measurements.get_by_id(measurement_id)
    if not measurement:
        return None

    update_data = schema.model_dump(exclude_unset=True)
    updated_measurement = uow.technical_measurements.update(
        measurement_id, update_data
    )
    return updated_measurement


def delete_technical_measurement(
    measurement_id: str, uow: AbstractUnitOfWork
) -> bool:
    """
    Elimina una medición técnica por su ID alfanumérico.
    """
    measurement = uow.technical_measurements.get_by_id(measurement_id)
    if not measurement:
        return False

    uow.technical_measurements.delete(measurement_id)
    return True


# Solicitud quincenal

class BiweeklyRequestBase(BaseModel):
    id: str = Field(..., min_length=1, max_length=5)
    project_id: str = Field(..., min_length=1, max_length=5)
    date: str = Field(..., min_length=1, max_length=20)
    status: str = Field(..., min_length=1, max_length=30)
    amount: float = Field(..., ge=0)
    notes: str = Field(..., min_length=1, max_length=300)


class BiweeklyRequestCreate(BiweeklyRequestBase):
    pass


class BiweeklyRequestRead(BiweeklyRequestBase):
    model_config = ConfigDict(from_attributes=True)


class BiweeklyRequestStatusUpdate(BaseModel):
    status: Literal["Pendiente", "Aprobada", "Rechazada"]


# Estado de cuenta

class AccountStatementBase(BaseModel):
    id: str = Field(..., min_length=1, max_length=5)
    project_id: str = Field(..., min_length=1, max_length=5)
    date: str = Field(..., min_length=1, max_length=20)
    initial_budget: float = Field(..., ge=0)
    amount_paid: float = Field(..., ge=0)


class AccountStatementCreate(AccountStatementBase):
    pass


class AccountStatementRead(AccountStatementBase):
    model_config = ConfigDict(from_attributes=True)

    remaining_amount: float


class AccountStatementPaymentUpdate(BaseModel):
    amount_paid: float = Field(..., ge=0)
