from dataclasses import dataclass

@dataclass
class Material:
    id: int
    description: str
    specifications: str

    def __str__(self):
        return f"Material(id={self.id}, description='{self.description}', specifications='{self.specifications}')"
