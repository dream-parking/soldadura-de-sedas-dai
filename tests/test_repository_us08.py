from datetime import date

from app.domain.models import (
    Project,
    Worker,
    WorkerAssigment,
    Payroll,
    Material,
    DetalleMaterialesObra,
    TechnicalMeasurement,
    BiweeklyRequest,
    AccountStatement,
)
from app.adapters.repository import (
    FakeProjectRepository,
    FakeWorkerRepository,
    FakeWorkerAssignmentRepository,
    FakePayrollRepository,
    FakeMaterialRepository,
    FakeDetalleMaterialesObraRepository,
    FakeTechnicalMeasurementRepository,
    FakeBiweeklyRequestRepository,
    FakeAccountStatementRepository,
)


# Proyectos
def test_project_repository_add_and_get():
    repo = FakeProjectRepository()
    project = Project(
        project_id="P001",
        client_id="C001",
        quote_id="Q001",
        project_name="Techo Bodega Norte",
        project_location="Zona 12",
        project_start_date=date(2026, 1, 1),
        project_total_cost=15000.0,
        project_status="In Progress",
    )
    repo.add(project)
    assert repo.get("P001").project_name == "Techo Bodega Norte"


def test_project_repository_update():
    repo = FakeProjectRepository()
    project = Project("P001", "C001", "Q001", "Techo A", "Zona 1", date(2026, 1, 1), 1000.0, "In Progress")
    repo.add(project)

    actualizado = Project("P001", "C001", "Q001", "Techo A", "Zona 1", date(2026, 1, 1), 1000.0, "Completed")
    repo.update(actualizado)

    assert repo.get("P001").project_status == "Completed"


# Trabajadores
def test_worker_repository_add_and_get():
    repo = FakeWorkerRepository()
    worker = Worker(worker_id="W001", worker_name="Juan Perez", worker_role="Soldador", worker_base_rate=150.0)
    repo.add(worker)
    assert repo.get("W001").worker_name == "Juan Perez"


def test_worker_repository_list():
    repo = FakeWorkerRepository()
    repo.add(Worker("W001", "Juan", "Soldador", 150.0))
    repo.add(Worker("W002", "Maria", "Supervisor", 200.0))
    assert len(repo.list()) == 2


# Asignación de personal
def test_worker_assignment_repository_add_and_get():
    repo = FakeWorkerAssignmentRepository()
    assignment = WorkerAssigment(assignment_id="A001", worker_id="W001", project_id="P001", assignment_date=date(2026, 1, 5))
    repo.add(assignment)
    assert repo.get("A001").project_id == "P001"


# Nómina
def test_payroll_repository_add_and_get():
    repo = FakePayrollRepository()
    payroll = Payroll(
        payroll_id="N001",
        worker_id="W001",
        project_id="P001",
        payroll_fortnight_period="2026-Q1",
        payroll_payment_date=date(2026, 1, 15),
        payroll_hours_worked=80.0,
        payroll_paid_amount=1200.0,
    )
    repo.add(payroll)
    assert repo.get("N001").payroll_paid_amount == 1200.0


# Materiales
def test_material_repository_add_and_get():
    repo = FakeMaterialRepository()
    material = Material(id=1, description="Lamina galvanizada", specifications="Calibre 26")
    repo.add(material)
    assert repo.get(1).description == "Lamina galvanizada"


# Detalle de materiales por obra (PK compuesta)
def test_detalle_materiales_obra_add_and_get():
    repo = FakeDetalleMaterialesObraRepository()
    detalle = DetalleMaterialesObra(
        project_id="P001",
        material_id="M001",
        used_quantity=25.5,
        measurement_unit="metros",
    )
    repo.add(detalle)

    resultado = repo.get("P001", "M001")
    assert resultado.used_quantity == 25.5


def test_detalle_materiales_obra_update():
    repo = FakeDetalleMaterialesObraRepository()
    detalle = DetalleMaterialesObra("P001", "M001", 25.5, "metros")
    repo.add(detalle)

    actualizado = DetalleMaterialesObra("P001", "M001", 30.0, "metros")
    repo.update(actualizado)

    assert repo.get("P001", "M001").used_quantity == 30.0


def test_detalle_materiales_obra_identidad_compuesta():
    """Dos registros con distinto material en el mismo proyecto son entidades distintas."""
    repo = FakeDetalleMaterialesObraRepository()
    repo.add(DetalleMaterialesObra("P001", "M001", 10.0, "unidades"))
    repo.add(DetalleMaterialesObra("P001", "M002", 5.0, "pies"))

    assert len(repo.list()) == 2
    assert repo.get("P001", "M001").used_quantity == 10.0
    assert repo.get("P001", "M002").used_quantity == 5.0


# Medición técnica
def test_technical_measurement_repository_add_and_get():
    repo = FakeTechnicalMeasurementRepository()
    measurement = TechnicalMeasurement(
        id="TM001",
        project_id="P001",
        dimensions=120,
        structure_type="Portico",
        payment=500.0,
        unit="metros",
        notes="Medicion inicial",
    )
    repo.add(measurement)
    assert repo.get("TM001").structure_type == "Portico"


# Solicitud quincenal
def test_biweekly_request_repository_add_and_get():
    repo = FakeBiweeklyRequestRepository()
    request = BiweeklyRequest(
        id="SQ001",
        project_id="P001",
        date="2026-01-15",
        status="Pendiente",
        amount=3000.0,
        notes="Primera quincena",
    )
    repo.add(request)
    assert repo.get("SQ001").status == "Pendiente"


# Estado de cuenta
def test_account_statement_repository_add_and_get():
    repo = FakeAccountStatementRepository()
    statement = AccountStatement(
        id="EC001",
        project_id="P001",
        date="2026-01-31",
        initial_budget=15000.0,
        amount_paid=5000.0,
    )
    repo.add(statement)

    resultado = repo.get("EC001")
    assert resultado.remaining_amount == 10000.0