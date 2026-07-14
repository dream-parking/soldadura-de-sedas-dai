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
from typing import Literal, Optional

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


class QuoteCreate(QuoteBase):
    pass


class QuoteRead(QuoteBase):
    model_config = ConfigDict(from_attributes=True)


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


class WorkerAssignmentCreate(WorkerAssignmentBase):
    pass


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


class MaterialUsageDetailRead(MaterialUsageDetailBase):
    model_config = ConfigDict(from_attributes=True)


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


class TechnicalMeasurementRead(TechnicalMeasurementBase):
    model_config = ConfigDict(from_attributes=True)


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