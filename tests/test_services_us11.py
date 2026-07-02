from datetime import date

import pytest

from app.domain.models import Client, Quote, Project
from app.adapters.repository import (
    FakeWorkerRepository,
    FakeWorkerAssignmentRepository,
    FakePayrollRepository,
    FakeMaterialRepository,
    FakeDetalleMaterialesObraRepository,
    FakeTechnicalMeasurementRepository,
    FakeAccountStatementRepository,
    FakeBiweeklyRequestRepository,
    FakeProjectRepository,
)
from app.service_layer import services
from app.service_layer.exceptions import (
    WorkerNotFound,
    ProjectNotFound,
    MaterialNotFound,
)

# helper un proyecto ya existente para usar en varios tests

def _crear_proyecto_de_prueba(project_repo, project_id="P001"):
    project = Project(
        project_id=project_id,
        client_id="C001",
        quote_id="Q001",
        project_name="Techo Bodega Norte",
        project_location="Zona 12",
        project_start_date=date(2026, 1, 1),
        project_total_cost=15000.0,
        project_status="In Progress",
    )
    project_repo.add(project)
    return project


# Registrar trabajador
def test_registrar_trabajador():
    worker_repo = FakeWorkerRepository()

    worker = services.registrar_trabajador(
        worker_id="W001",
        worker_name="Juan Perez",
        worker_role="Soldador",
        worker_base_rate=150.0,
        worker_repo=worker_repo,
    )

    assert worker_repo.get("W001") is worker
    assert worker_repo.get("W001").worker_name == "Juan Perez"


# Asignar trabajador a proyecto
def test_asignar_trabajador_a_proyecto_ok():
    worker_repo = FakeWorkerRepository()
    project_repo = FakeProjectRepository()
    assignment_repo = FakeWorkerAssignmentRepository()

    services.registrar_trabajador("W001", "Juan Perez", "Soldador", 150.0, worker_repo)
    _crear_proyecto_de_prueba(project_repo)

    assignment = services.asignar_trabajador_a_proyecto(
        assignment_id="A001",
        worker_id="W001",
        project_id="P001",
        assignment_date=date(2026, 1, 5),
        worker_repo=worker_repo,
        project_repo=project_repo,
        assignment_repo=assignment_repo,
    )

    assert assignment_repo.get("A001").project_id == "P001"
    assert worker_repo.get("W001").assignments[0].project_id == "P001"


def test_asignar_trabajador_a_proyecto_worker_inexistente():
    worker_repo = FakeWorkerRepository()
    project_repo = FakeProjectRepository()
    assignment_repo = FakeWorkerAssignmentRepository()

    _crear_proyecto_de_prueba(project_repo)

    with pytest.raises(WorkerNotFound):
        services.asignar_trabajador_a_proyecto(
            "A001", "W999", "P001", date(2026, 1, 5),
            worker_repo, project_repo, assignment_repo,
        )


def test_asignar_trabajador_a_proyecto_proyecto_inexistente():
    worker_repo = FakeWorkerRepository()
    project_repo = FakeProjectRepository()
    assignment_repo = FakeWorkerAssignmentRepository()

    services.registrar_trabajador("W001", "Juan Perez", "Soldador", 150.0, worker_repo)

    with pytest.raises(ProjectNotFound):
        services.asignar_trabajador_a_proyecto(
            "A001", "W001", "P999", date(2026, 1, 5),
            worker_repo, project_repo, assignment_repo,
        )

# Registrar nómina quincenal
def test_registrar_nomina_quincenal_ok():
    worker_repo = FakeWorkerRepository()
    project_repo = FakeProjectRepository()
    assignment_repo = FakeWorkerAssignmentRepository()
    payroll_repo = FakePayrollRepository()

    services.registrar_trabajador("W001", "Juan Perez", "Soldador", 150.0, worker_repo)
    _crear_proyecto_de_prueba(project_repo)
    services.asignar_trabajador_a_proyecto(
        "A001", "W001", "P001", date(2026, 1, 5),
        worker_repo, project_repo, assignment_repo,
    )

    payroll = services.registrar_nomina_quincenal(
        payroll_id="N001",
        worker_id="W001",
        project_id="P001",
        payroll_fortnight_period="2026-Q1",
        payroll_payment_date=date(2026, 1, 15),
        worker_repo=worker_repo,
        project_repo=project_repo,
        payroll_repo=payroll_repo,
        payroll_hours_worked=80.0,
        payroll_paid_amount=1200.0,
    )

    assert payroll_repo.get("N001").payroll_paid_amount == 1200.0


def test_registrar_nomina_quincenal_sin_asignacion_previa_falla():
    """
    Verifica que el invariante de negocio definido en Worker.add_payroll
    (no puede haber nómina sin asignación previa al proyecto) se respete
    también cuando se invoca a través de la capa de servicios.
    """
    worker_repo = FakeWorkerRepository()
    project_repo = FakeProjectRepository()
    payroll_repo = FakePayrollRepository()

    services.registrar_trabajador("W001", "Juan Perez", "Soldador", 150.0, worker_repo)
    _crear_proyecto_de_prueba(project_repo)
    # Nota: NO se asigna el trabajador al proyecto antes de la nómina

    with pytest.raises(ValueError):
        services.registrar_nomina_quincenal(
            "N001", "W001", "P001", "2026-Q1", date(2026, 1, 15),
            worker_repo, project_repo, payroll_repo,
        )


def test_registrar_nomina_quincenal_worker_inexistente():
    worker_repo = FakeWorkerRepository()
    project_repo = FakeProjectRepository()
    payroll_repo = FakePayrollRepository()

    _crear_proyecto_de_prueba(project_repo)

    with pytest.raises(WorkerNotFound):
        services.registrar_nomina_quincenal(
            "N001", "W999", "P001", "2026-Q1", date(2026, 1, 15),
            worker_repo, project_repo, payroll_repo,
        )


# 4. Agregar material
def test_agregar_material():
    material_repo = FakeMaterialRepository()

    material = services.agregar_material(
        material_id=1,
        description="Lamina galvanizada",
        specifications="Calibre 26",
        material_repo=material_repo,
    )

    assert material_repo.get(1) is material


# 5. Registrar uso de material en obra
def test_registrar_uso_material_en_obra_ok():
    project_repo = FakeProjectRepository()
    material_repo = FakeMaterialRepository()
    detalle_repo = FakeDetalleMaterialesObraRepository()

    _crear_proyecto_de_prueba(project_repo)
    services.agregar_material(1, "Lamina galvanizada", "Calibre 26", material_repo)

    detalle = services.registrar_uso_material_en_obra(
        project_id="P001",
        material_id=1,
        used_quantity=25.5,
        measurement_unit="metros",
        project_repo=project_repo,
        material_repo=material_repo,
        detalle_repo=detalle_repo,
    )

    assert detalle_repo.get("P001", 1).used_quantity == 25.5


def test_registrar_uso_material_en_obra_material_inexistente():
    project_repo = FakeProjectRepository()
    material_repo = FakeMaterialRepository()
    detalle_repo = FakeDetalleMaterialesObraRepository()

    _crear_proyecto_de_prueba(project_repo)

    with pytest.raises(MaterialNotFound):
        services.registrar_uso_material_en_obra(
            "P001", 999, 25.5, "metros",
            project_repo, material_repo, detalle_repo,
        )


def test_registrar_uso_material_en_obra_proyecto_inexistente():
    project_repo = FakeProjectRepository()
    material_repo = FakeMaterialRepository()
    detalle_repo = FakeDetalleMaterialesObraRepository()

    services.agregar_material(1, "Lamina galvanizada", "Calibre 26", material_repo)

    with pytest.raises(ProjectNotFound):
        services.registrar_uso_material_en_obra(
            "P999", 1, 25.5, "metros",
            project_repo, material_repo, detalle_repo,
        )


# 6. Registrar medida técnica
def test_registrar_medida_tecnica_ok():
    project_repo = FakeProjectRepository()
    measurement_repo = FakeTechnicalMeasurementRepository()

    _crear_proyecto_de_prueba(project_repo)

    measurement = services.registrar_medida_tecnica(
        measurement_id="TM001",
        project_id="P001",
        dimensions=120,
        structure_type="Portico",
        payment=500.0,
        unit="metros",
        notes="Medicion inicial",
        project_repo=project_repo,
        measurement_repo=measurement_repo,
    )

    assert measurement_repo.get("TM001").structure_type == "Portico"


def test_registrar_medida_tecnica_proyecto_inexistente():
    project_repo = FakeProjectRepository()
    measurement_repo = FakeTechnicalMeasurementRepository()

    with pytest.raises(ProjectNotFound):
        services.registrar_medida_tecnica(
            "TM001", "P999", 120, "Portico", 500.0, "metros", "notas",
            project_repo, measurement_repo,
        )


# 7. Registrar estado de cuenta
def test_registrar_estado_de_cuenta_ok():
    project_repo = FakeProjectRepository()
    statement_repo = FakeAccountStatementRepository()

    _crear_proyecto_de_prueba(project_repo)

    statement = services.registrar_estado_de_cuenta(
        statement_id="EC001",
        project_id="P001",
        statement_date="2026-01-31",
        initial_budget=15000.0,
        amount_paid=5000.0,
        project_repo=project_repo,
        statement_repo=statement_repo,
    )

    assert statement_repo.get("EC001").remaining_amount == 10000.0


def test_registrar_estado_de_cuenta_proyecto_inexistente():
    project_repo = FakeProjectRepository()
    statement_repo = FakeAccountStatementRepository()

    with pytest.raises(ProjectNotFound):
        services.registrar_estado_de_cuenta(
            "EC001", "P999", "2026-01-31", 15000.0, 5000.0,
            project_repo, statement_repo,
        )


# 8. Registrar solicitud quincenal
def test_registrar_solicitud_quincenal_ok():
    project_repo = FakeProjectRepository()
    request_repo = FakeBiweeklyRequestRepository()

    _crear_proyecto_de_prueba(project_repo)

    request = services.registrar_solicitud_quincenal(
        request_id="SQ001",
        project_id="P001",
        request_date="2026-01-15",
        status="Pendiente",
        amount=3000.0,
        notes="Primera quincena",
        project_repo=project_repo,
        request_repo=request_repo,
    )

    assert request_repo.get("SQ001").status == "Pendiente"


def test_registrar_solicitud_quincenal_proyecto_inexistente():
    project_repo = FakeProjectRepository()
    request_repo = FakeBiweeklyRequestRepository()

    with pytest.raises(ProjectNotFound):
        services.registrar_solicitud_quincenal(
            "SQ001", "P999", "2026-01-15", "Pendiente", 3000.0, "notas",
            project_repo, request_repo,
        )