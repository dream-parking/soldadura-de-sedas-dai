from dataclasses import dataclass

@dataclass
class Material:
    id: int
    description: str
    specifications: str

    def __str__(self):
        return f"Material(id={self.id}, description='{self.description}', specifications='{self.specifications}')"


@dataclass
class MaterialProjectDetail:
    """Entidad que representa el detalle de materiales usados en una obra (DetalleMaterialesObra)."""
    id: str
    project_id: str  # FK
    material_id: int  # FK
    quantity_used: float
    unit: str
    unit_cost: float

    @property
    def total_cost(self) -> float:
        return self.quantity_used * self.unit_cost

    def __str__(self):
        return (
            f"MaterialProjectDetail(id={self.id}, project_id='{self.project_id}', "
            f"material_id={self.material_id}, quantity_used={self.quantity_used}, "
            f"unit='{self.unit}', unit_cost={self.unit_cost}, total_cost={self.total_cost})"
        )
