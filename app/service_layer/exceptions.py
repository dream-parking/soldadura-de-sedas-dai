class WorkerNotFound(Exception):
    """El trabajador solicitado no existe :c"""


class ProjectNotFound(Exception):
    """El proyecto solicitado no existe :cc"""


class MaterialNotFound(Exception):
    """El material solicitado no existe """


class WorkerNotAssignedToProject(Exception):
    """El trabajador no está asignado al proyecto"""