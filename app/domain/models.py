from dataclasses import dataclass, field
from typing import List, Optional
from datetime import date


@dataclass
class Client:
    """Entidad que representa a los clientes de la constructora."""
    client_id: str
    client_company_name: str
    client_phone: str
    registration_date: date
    client_email: Optional[str] = None #Puede ser Null
    
    
@dataclass
class Quote:
    """Entidad que representa una cotización emitida a un cliente."""
    quote_id: str
    client_id: str #FK
    quote_issue_date: date
    quote_job_description: str
    quote_estimated_amount: float
    quote_status: str #Pendiente / Aprobado / Rechazado
    notes: Optional[str] = None #Puede ser Null
    
    
@dataclass
class Project:
    """Entidad central del sistema que representa una obra en ejecución."""
    project_id: str
    client_id: str #FK
    quote_id: str #FK
    project_name: str
    project_location: str
    project_start_date: date
    project_total_cost: float
    project_status: str #In Progress / Completed
    project_estimated_end_date: Optional[date] = None #Can be Null
    
    
@dataclass
class WorkerAssigment:
    """Entidad que representa la asignación física de un trabajador a una obra"""
    assignment_id: str
    worker_id: str #FK
    project_id: str #FK
    assignment_date: date
    
    
@dataclass
class Payroll:
    """Entidad que registra el pago quincenal de un trabajador por proyecto"""
    payroll_id: str
    worker_id: str #FK
    project_id: str #FK
    payroll_fortnight_period: str
    payroll_payment_date: date
    payroll_hours_worked: Optional[float] = None
    payroll_paid_amount: Optional[float] = None
    
    
@dataclass
class Worker:
    """
    Entidad para agregar el personal.
    Representa a un trabajador y controla sus asignaciones y nóminas.
    """
    worker_id: str
    worker_name: str 
    worker_role: str
    worker_base_rate: float
    
    assignments: List[WorkerAssigment] = field(default_factory=list)
    payrolls: List[Payroll] = field(default_factory=list)
    
    def assign_to_project(self, assignment: WorkerAssigment):
        """Asignar el empleado a un trabajo en específico"""
        self.assignments.append(assignment)
        
    def add_payroll(self, payroll: Payroll):
        """
        Validación del invariante de negocio:
        Un trabajador NO puede recibir un registro de nómina de un proyecto 
        si no ha sido asignado previamente a esa misma obra
        """
        
        assigned_project_id = [a.project_id for a in self.assignments]
        
        if payroll.project_id not in assigned_project_id:
            raise ValueError(
                f"El trabajador {self.worker_name} ({self.worker_id})"
                f"no puede tener nómina en el projecto {payroll.project_id} porque no esta asignado a él"
            )
        self.payrolls.append(payroll)
