from datetime import date
from typing import Optional

from app.domain.models import (
    Worker,
    WorkerAssigment,
    Payroll,
    Material,
    DetalleMaterialesObra,
    TechnicalMeasurement,
    AccountStatement,
    BiweeklyRequest,
)
from app.service_layer.exceptions import (
    WorkerNotFound,
    ProjectNotFound,
    MaterialNotFound,
)


# Helpers de validación reutilizables

def _get_worker_or_raise(worker_id: str, worker_repo) -> Worker:
    worker = worker_repo.get(worker_id)
    if worker is None:
        raise WorkerNotFound(f"No existe un trabajador con id '{worker_id}'")
    return worker


def _assert_project_exists(project_id: str, project_repo) -> None:
    if project_repo.get(project_id) is None:
        raise ProjectNotFound(f"No existe un proyecto con id '{project_id}'")


def _assert_material_exists(material_id, material_repo) -> None:
    if material_repo.get(material_id) is None:
        raise MaterialNotFound(f"No existe un material con id '{material_id}'")


# Registrar trabajador
def registrar_trabajador(
    worker_id: str,
    worker_name: str,
    worker_role: str,
    worker_base_rate: float,
    worker_repo,
) -> Worker:
    worker = Worker(
        worker_id=worker_id,
        worker_name=worker_name,
        worker_role=worker_role,
        worker_base_rate=worker_base_rate,
    )
    worker_repo.add(worker)
    return worker


# Asignar trabajador a proyecto
def asignar_trabajador_a_proyecto(
    assignment_id: str,
    worker_id: str,
    project_id: str,
    assignment_date: date,
    worker_repo,
    project_repo,
    assignment_repo,
) -> WorkerAssigment:
    worker = _get_worker_or_raise(worker_id, worker_repo)
    _assert_project_exists(project_id, project_repo)

    assignment = WorkerAssigment(
        assignment_id=assignment_id,
        worker_id=worker_id,
        project_id=project_id,
        assignment_date=assignment_date,
    )

    # Mantiene el objeto de dominio Worker consistente con su propia lista de asignaciones
    worker.assign_to_project(assignment)

    assignment_repo.add(assignment)
    return assignment


#  Registrar nómina quincenal

def registrar_nomina_quincenal(
    payroll_id: str,
    worker_id: str,
    project_id: str,
    payroll_fortnight_period: str,
    payroll_payment_date: date,
    worker_repo,
    project_repo,
    payroll_repo,
    payroll_hours_worked: Optional[float] = None,
    payroll_paid_amount: Optional[float] = None,
) -> Payroll:
    worker = _get_worker_or_raise(worker_id, worker_repo)
    _assert_project_exists(project_id, project_repo)

    payroll = Payroll(
        payroll_id=payroll_id,
        worker_id=worker_id,
        project_id=project_id,
        payroll_fortnight_period=payroll_fortnight_period,
        payroll_payment_date=payroll_payment_date,
        payroll_hours_worked=payroll_hours_worked,
        payroll_paid_amount=payroll_paid_amount,
    )

    worker.add_payroll(payroll)

    payroll_repo.add(payroll)
    return payroll


# Agregar material
def agregar_material(
    material_id,
    description: str,
    specifications: str,
    material_repo,
) -> Material:
    material = Material(
        id=material_id,
        description=description,
        specifications=specifications,
    )
    material_repo.add(material)
    return material


# 5. Registrar uso de material en obra

def registrar_uso_material_en_obra(
    project_id: str,
    material_id,
    used_quantity: float,
    measurement_unit: str,
    project_repo,
    material_repo,
    detalle_repo,
) -> DetalleMaterialesObra:
    _assert_project_exists(project_id, project_repo)
    _assert_material_exists(material_id, material_repo)

    detalle = DetalleMaterialesObra(
        project_id=project_id,
        material_id=material_id,
        used_quantity=used_quantity,
        measurement_unit=measurement_unit,
    )
    detalle_repo.add(detalle)
    return detalle


# 6. Registrar medida técnica
def registrar_medida_tecnica(
    measurement_id: str,
    project_id: str,
    dimensions: int,
    structure_type: str,
    payment: float,
    unit: str,
    notes: str,
    project_repo,
    measurement_repo,
) -> TechnicalMeasurement:
    _assert_project_exists(project_id, project_repo)

    measurement = TechnicalMeasurement(
        id=measurement_id,
        project_id=project_id,
        dimensions=dimensions,
        structure_type=structure_type,
        payment=payment,
        unit=unit,
        notes=notes,
    )
    measurement_repo.add(measurement)
    return measurement


# 7. Registrar estado de cuenta
def registrar_estado_de_cuenta(
    statement_id: str,
    project_id: str,
    statement_date: str,
    initial_budget: float,
    amount_paid: float,
    project_repo,
    statement_repo,
) -> AccountStatement:
    _assert_project_exists(project_id, project_repo)

    statement = AccountStatement(
        id=statement_id,
        project_id=project_id,
        date=statement_date,
        initial_budget=initial_budget,
        amount_paid=amount_paid,
    )
    statement_repo.add(statement)
    return statement


# 8. Registrar solicitud quincenal
def registrar_solicitud_quincenal(
    request_id: str,
    project_id: str,
    request_date: str,
    status: str,
    amount: float,
    notes: str,
    project_repo,
    request_repo,
) -> BiweeklyRequest:
    _assert_project_exists(project_id, project_repo)

    request = BiweeklyRequest(
        id=request_id,
        project_id=project_id,
        date=request_date,
        status=status,
        amount=amount,
        notes=notes,
    )
    request_repo.add(request)
    return request