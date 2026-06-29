from dataclasses import dataclass

@dataclass
class SolicitudQuincenal:
    id: str
    id_proyecto: str
    fecha: str
    estado: str
    monto:float
    observaciones: str

    def __str__(self):
        return f"SolicitudQuincenal(id={self.id}, id_proyecto='{self.id_proyecto}', fecha='{self.fecha}', estado='{self.estado}', monto={self.monto}, observaciones='{self.observaciones}')"