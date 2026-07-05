class NotFoundError(Exception):
    """Excepción base para recursos de dominio que no existen."""


class ClientNotFound(NotFoundError):
    """El cliente solicitado no existe"""


class WorkerNotFound(NotFoundError):
    """El trabajador solicitado no existe :c"""


class ProjectNotFound(NotFoundError):
    """El proyecto solicitado no existe :cc"""


class MaterialNotFound(NotFoundError):
    """El material solicitado no existe """


class WorkerNotAssignedToProject(Exception):
    """El trabajador no está asignado al proyecto"""