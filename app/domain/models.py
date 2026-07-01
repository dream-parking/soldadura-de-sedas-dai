from dataclasses import dataclass

@dataclass
class TechnicalMeasurement:
    id: str
    project_id: str
    dimensions: int
    structure_type: str
    payment: float
    unit: str
    notes: str
    
    def __str__(self):
        return f"TechnicalMeasurement(id={self.id}, project_id='{self.project_id}', dimensions={self.dimensions}, structure_type='{self.structure_type}', payment={self.payment}, unit='{self.unit}', notes='{self.notes}')"
    
@dataclass
class Material:
    id: int
    description: str
    specifications: str

    def __str__(self):
        return f"Material(id={self.id}, description='{self.description}', specifications='{self.specifications}')"


@dataclass
class BiweeklyRequest:
    id: str
    project_id: str
    date: str
    status: str
    amount: float
    notes: str

    def __str__(self):
        return f"BiweeklyRequest(id={self.id}, project_id='{self.project_id}', date='{self.date}', status='{self.status}', amount={self.amount}, notes='{self.notes}')"
    
@dataclass
class AccountStatement:
    id: str
    project_id: str
    date: str
    initial_budget: float
    amount_paid: float
    
    # statement property
    @property
    def remaining_amount(self) -> float:
        return self.initial_budget - self.amount_paid
    
    # entity representation
    def __str__(self):
        return f"AccountStatement(id={self.id}, project_id='{self.project_id}', date='{self.date}', initial_budget={self.initial_budget}, amount_paid={self.amount_paid}, remaining_amount={self.remaining_amount})"