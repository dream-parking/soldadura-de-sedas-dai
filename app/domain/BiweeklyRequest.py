from dataclasses import dataclass

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