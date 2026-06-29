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