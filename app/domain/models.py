from dataclasses import dataclass
from typing import Optional
from datetime import date


@dataclass
class Client:
    client_id: str
    client_company_name: str
    client_phone: str
    registration_date: date
    client_email: Optional[str] = None #Can be Null
    
    
@dataclass
class Quote:
    quote_id: str
    client_id: str #FK
    quote_issue_date: date
    quote_job_description: str
    quote_estimated_amount: float
    quote_status: str #Pending / Approved / Rejected
    notes: Optional[str] = None #Can be Null
    
    
@dataclass
class Project:
    project_id: str
    client_id: str #FK
    quote_id: str #FK
    project_name: str
    project_location: str
    project_start_date: date
    project_total_cost: float
    project_status: str #In Progress / Completed
    project_estimated_end_date: Optional[date] = None #Can be Null