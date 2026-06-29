from dataclasses import dataclass

@dataclass
class Materiale:
    __id: int
    __descripcion: str
    __especificaciones: str

    def __str__(self):
        return f"Materiale(id={self.__id}, descripcion='{self.__descripcion}', especificaciones='{self.__especificaciones}')"
