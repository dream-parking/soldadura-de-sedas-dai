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


class QuoteNotFound(NotFoundError):
    """La cotización solicitada no existe"""
    
    
class AccountStatementNotFound(NotFoundError):
    """El estado de cuenta solicitado no existe"""


class BiweeklyRequestNotFound(NotFoundError):
    """La solicitud quincenal solicitada no existe"""


class QuoteNotApproved(Exception):
    """La cotización no está en estado Aprobado; no se puede crear el proyecto."""


class WorkerNotAssignedToProject(Exception):
    """El trabajador no está asignado al proyecto"""