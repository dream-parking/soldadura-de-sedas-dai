from dataclasses import dataclass

@dataclass
class MedidaTecnica:
    id: str
    id_proyecto: str
    dimensiones: int
    tipo_estructura: str
    pago: float
    unidad: str
    observaciones: str
    
    def __str__(self):
        return f"MedidaTecnica(id={self.id}, id_proyecto='{self.id_proyecto}', dimensiones={self.dimensiones}, tipo_estructura='{self.tipo_estructura}', pago={self.pago}, unidad='{self.unidad}', observaciones='{self.observaciones}')"