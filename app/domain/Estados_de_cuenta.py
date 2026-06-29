from dataclasses import dataclass

@dataclass
class EstadoCuenta:
    id: str
    id_proyecto: str
    fecha: str
    prosupuesto_inicial: float
    cantidad_pagada: float
    
    #propiedad de los estados
    @property
    def cantidad_restante(self) -> float:
        return self.prosupuesto_inicial - self.cantidad_pagada
    
    #Visualización de entidad
    def __str__(self):
        return f"EstadoCuenta(id={self.id}, id_proyecto='{self.id_proyecto}', fecha='{self.fecha}', prosupuesto_inicial={self.prosupuesto_inicial}, cantidad_pagada={self.cantidad_pagada}, cantidad_restante={self.cantidad_restante})"
