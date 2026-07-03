"""app/adapters/repository.py"""
from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.models import (
    Client,
    Quote,
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


class AbstractRepository(ABC):
    """Interfaz para entidades (un solo ID)."""

    @abstractmethod
    def add(self, entity):
        raise NotImplementedError

    @abstractmethod
    def get(self, id: str):
        raise NotImplementedError

    @abstractmethod
    def list(self) -> List:
        raise NotImplementedError

    @abstractmethod
    def update(self, entity):
        raise NotImplementedError


class AbstractDetalleMaterialesObraRepository(ABC):
    """
    Interfaz separada ya  DetalleMaterialesObra no tiene un ID único
    <su identidad es la combinación (project_id, material_id)>>>:9
    """

    @abstractmethod
    def add(self, entity: DetalleMaterialesObra):
        raise NotImplementedError

    @abstractmethod
    def get(self, project_id: str, material_id: str):
        raise NotImplementedError

    @abstractmethod
    def list(self) -> List[DetalleMaterialesObra]:
        raise NotImplementedError

    @abstractmethod
    def update(self, entity: DetalleMaterialesObra):
        raise NotImplementedError


# Clientes

class SqlAlchemyClientRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, client: Client):
        self.session.add(client)

    def get(self, id: str) -> Optional[Client]:
        return self.session.query(Client).filter_by(client_id=id).first()

    def list(self) -> List[Client]:
        return self.session.query(Client).all()

    def update(self, client: Client):
        self.session.merge(client)


class FakeClientRepository(AbstractRepository):
    def __init__(self, clients: Optional[List[Client]] = None):
        self._clients = list(clients) if clients else []

    def add(self, client: Client):
        self._clients.append(client)

    def get(self, id: str) -> Optional[Client]:
        return next((c for c in self._clients if c.client_id == id), None)

    def list(self) -> List[Client]:
        return list(self._clients)

    def update(self, client: Client):
        for i, c in enumerate(self._clients):
            if c.client_id == client.client_id:
                self._clients[i] = client
                return
        self._clients.append(client)

# Cotizaciones 
class SqlAlchemyQuoteRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, quote: Quote):
        self.session.add(quote)

    def get(self, id: str) -> Optional[Quote]:
        return self.session.query(Quote).filter_by(quote_id=id).first()

    def list(self) -> List[Quote]:
        return self.session.query(Quote).all()

    def update(self, quote: Quote):
        self.session.merge(quote)


class FakeQuoteRepository(AbstractRepository):
    def __init__(self, quotes: Optional[List[Quote]] = None):
        self._quotes = list(quotes) if quotes else []

    def add(self, quote: Quote):
        self._quotes.append(quote)

    def get(self, id: str) -> Optional[Quote]:
        return next((q for q in self._quotes if q.quote_id == id), None)

    def list(self) -> List[Quote]:
        return list(self._quotes)

    def update(self, quote: Quote):
        for i, q in enumerate(self._quotes):
            if q.quote_id == quote.quote_id:
                self._quotes[i] = quote
                return
        self._quotes.append(quote)


# Proyectos
class SqlAlchemyProjectRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, project: Project):
        self.session.add(project)

    def get(self, id: str) -> Optional[Project]:
        return self.session.query(Project).filter_by(project_id=id).first()

    def list(self) -> List[Project]:
        return self.session.query(Project).all()

    def update(self, project: Project):
        self.session.merge(project)


class FakeProjectRepository(AbstractRepository):
    def __init__(self, projects: Optional[List[Project]] = None):
        self._projects = list(projects) if projects else []

    def add(self, project: Project):
        self._projects.append(project)

    def get(self, id: str) -> Optional[Project]:
        return next((p for p in self._projects if p.project_id == id), None)

    def list(self) -> List[Project]:
        return list(self._projects)

    def update(self, project: Project):
        for i, p in enumerate(self._projects):
            if p.project_id == project.project_id:
                self._projects[i] = project
                return
        self._projects.append(project)


# Trabajadores
class SqlAlchemyWorkerRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, worker: Worker):
        self.session.add(worker)

    def get(self, id: str) -> Optional[Worker]:
        return self.session.query(Worker).filter_by(worker_id=id).first()

    def list(self) -> List[Worker]:
        return self.session.query(Worker).all()

    def update(self, worker: Worker):
        self.session.merge(worker)


class FakeWorkerRepository(AbstractRepository):
    def __init__(self, workers: Optional[List[Worker]] = None):
        self._workers = list(workers) if workers else []

    def add(self, worker: Worker):
        self._workers.append(worker)

    def get(self, id: str) -> Optional[Worker]:
        return next((w for w in self._workers if w.worker_id == id), None)

    def list(self) -> List[Worker]:
        return list(self._workers)

    def update(self, worker: Worker):
        for i, w in enumerate(self._workers):
            if w.worker_id == worker.worker_id:
                self._workers[i] = worker
                return
        self._workers.append(worker)


# Asignación de personal
class SqlAlchemyWorkerAssignmentRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, assignment: WorkerAssigment):
        self.session.add(assignment)

    def get(self, id: str) -> Optional[WorkerAssigment]:
        return self.session.query(WorkerAssigment).filter_by(assignment_id=id).first()

    def list(self) -> List[WorkerAssigment]:
        return self.session.query(WorkerAssigment).all()

    def update(self, assignment: WorkerAssigment):
        self.session.merge(assignment)


class FakeWorkerAssignmentRepository(AbstractRepository):
    def __init__(self, assignments: Optional[List[WorkerAssigment]] = None):
        self._assignments = list(assignments) if assignments else []

    def add(self, assignment: WorkerAssigment):
        self._assignments.append(assignment)

    def get(self, id: str) -> Optional[WorkerAssigment]:
        return next((a for a in self._assignments if a.assignment_id == id), None)

    def list(self) -> List[WorkerAssigment]:
        return list(self._assignments)

    def update(self, assignment: WorkerAssigment):
        for i, a in enumerate(self._assignments):
            if a.assignment_id == assignment.assignment_id:
                self._assignments[i] = assignment
                return
        self._assignments.append(assignment)


# Nómina
class SqlAlchemyPayrollRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, payroll: Payroll):
        self.session.add(payroll)

    def get(self, id: str) -> Optional[Payroll]:
        return self.session.query(Payroll).filter_by(payroll_id=id).first()

    def list(self) -> List[Payroll]:
        return self.session.query(Payroll).all()

    def update(self, payroll: Payroll):
        self.session.merge(payroll)


class FakePayrollRepository(AbstractRepository):
    def __init__(self, payrolls: Optional[List[Payroll]] = None):
        self._payrolls = list(payrolls) if payrolls else []

    def add(self, payroll: Payroll):
        self._payrolls.append(payroll)

    def get(self, id: str) -> Optional[Payroll]:
        return next((p for p in self._payrolls if p.payroll_id == id), None)

    def list(self) -> List[Payroll]:
        return list(self._payrolls)

    def update(self, payroll: Payroll):
        for i, p in enumerate(self._payrolls):
            if p.payroll_id == payroll.payroll_id:
                self._payrolls[i] = payroll
                return
        self._payrolls.append(payroll)


# Materiales
class SqlAlchemyMaterialRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, material: Material):
        self.session.add(material)

    def get(self, id) -> Optional[Material]:
        return self.session.query(Material).filter_by(id=id).first()

    def list(self) -> List[Material]:
        return self.session.query(Material).all()

    def update(self, material: Material):
        self.session.merge(material)


class FakeMaterialRepository(AbstractRepository):
    def __init__(self, materials: Optional[List[Material]] = None):
        self._materials = list(materials) if materials else []

    def add(self, material: Material):
        self._materials.append(material)

    def get(self, id) -> Optional[Material]:
        return next((m for m in self._materials if m.id == id), None)

    def list(self) -> List[Material]:
        return list(self._materials)

    def update(self, material: Material):
        for i, m in enumerate(self._materials):
            if m.id == material.id:
                self._materials[i] = material
                return
        self._materials.append(material)


# Detalle de materiales por obra
class SqlAlchemyDetalleMaterialesObraRepository(AbstractDetalleMaterialesObraRepository):
    def __init__(self, session):
        self.session = session

    def add(self, detalle: DetalleMaterialesObra):
        self.session.add(detalle)

    def get(self, project_id: str, material_id: str) -> Optional[DetalleMaterialesObra]:
        return (
            self.session.query(DetalleMaterialesObra)
            .filter_by(project_id=project_id, material_id=material_id)
            .first()
        )

    def list(self) -> List[DetalleMaterialesObra]:
        return self.session.query(DetalleMaterialesObra).all()

    def update(self, detalle: DetalleMaterialesObra):
        self.session.merge(detalle)


class FakeDetalleMaterialesObraRepository(AbstractDetalleMaterialesObraRepository):
    def __init__(self, detalles: Optional[List[DetalleMaterialesObra]] = None):
        self._detalles = list(detalles) if detalles else []

    def add(self, detalle: DetalleMaterialesObra):
        self._detalles.append(detalle)

    def get(self, project_id: str, material_id: str) -> Optional[DetalleMaterialesObra]:
        return next(
            (
                d for d in self._detalles
                if d.project_id == project_id and d.material_id == material_id
            ),
            None,
        )

    def list(self) -> List[DetalleMaterialesObra]:
        return list(self._detalles)

    def update(self, detalle: DetalleMaterialesObra):
        for i, d in enumerate(self._detalles):
            if d.project_id == detalle.project_id and d.material_id == detalle.material_id:
                self._detalles[i] = detalle
                return
        self._detalles.append(detalle)


# Medición técnica
class SqlAlchemyTechnicalMeasurementRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, measurement: TechnicalMeasurement):
        self.session.add(measurement)

    def get(self, id: str) -> Optional[TechnicalMeasurement]:
        return self.session.query(TechnicalMeasurement).filter_by(id=id).first()

    def list(self) -> List[TechnicalMeasurement]:
        return self.session.query(TechnicalMeasurement).all()

    def update(self, measurement: TechnicalMeasurement):
        self.session.merge(measurement)


class FakeTechnicalMeasurementRepository(AbstractRepository):
    def __init__(self, measurements: Optional[List[TechnicalMeasurement]] = None):
        self._measurements = list(measurements) if measurements else []

    def add(self, measurement: TechnicalMeasurement):
        self._measurements.append(measurement)

    def get(self, id: str) -> Optional[TechnicalMeasurement]:
        return next((m for m in self._measurements if m.id == id), None)

    def list(self) -> List[TechnicalMeasurement]:
        return list(self._measurements)

    def update(self, measurement: TechnicalMeasurement):
        for i, m in enumerate(self._measurements):
            if m.id == measurement.id:
                self._measurements[i] = measurement
                return
        self._measurements.append(measurement)


# Solicitud quincenal
class SqlAlchemyBiweeklyRequestRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, request: BiweeklyRequest):
        self.session.add(request)

    def get(self, id: str) -> Optional[BiweeklyRequest]:
        return self.session.query(BiweeklyRequest).filter_by(id=id).first()

    def list(self) -> List[BiweeklyRequest]:
        return self.session.query(BiweeklyRequest).all()

    def update(self, request: BiweeklyRequest):
        self.session.merge(request)


class FakeBiweeklyRequestRepository(AbstractRepository):
    def __init__(self, requests: Optional[List[BiweeklyRequest]] = None):
        self._requests = list(requests) if requests else []

    def add(self, request: BiweeklyRequest):
        self._requests.append(request)

    def get(self, id: str) -> Optional[BiweeklyRequest]:
        return next((r for r in self._requests if r.id == id), None)

    def list(self) -> List[BiweeklyRequest]:
        return list(self._requests)

    def update(self, request: BiweeklyRequest):
        for i, r in enumerate(self._requests):
            if r.id == request.id:
                self._requests[i] = request
                return
        self._requests.append(request)


# Estado de cuenta
class SqlAlchemyAccountStatementRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, statement: AccountStatement):
        self.session.add(statement)

    def get(self, id: str) -> Optional[AccountStatement]:
        return self.session.query(AccountStatement).filter_by(id=id).first()

    def list(self) -> List[AccountStatement]:
        return self.session.query(AccountStatement).all()

    def update(self, statement: AccountStatement):
        self.session.merge(statement)


class FakeAccountStatementRepository(AbstractRepository):
    def __init__(self, statements: Optional[List[AccountStatement]] = None):
        self._statements = list(statements) if statements else []

    def add(self, statement: AccountStatement):
        self._statements.append(statement)

    def get(self, id: str) -> Optional[AccountStatement]:
        return next((s for s in self._statements if s.id == id), None)

    def list(self) -> List[AccountStatement]:
        return list(self._statements)

    def update(self, statement: AccountStatement):
        for i, s in enumerate(self._statements):
            if s.id == statement.id:
                self._statements[i] = statement
                return
        self._statements.append(statement)