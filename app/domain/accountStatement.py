from dataclasses import dataclass

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
