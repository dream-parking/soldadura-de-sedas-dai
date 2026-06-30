from dataclasses import dataclass
from typing import Optional
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
    project_status: str #En Progreso / Completado
    project_estimated_end_date: Optional[date] = None #Puede ser Null