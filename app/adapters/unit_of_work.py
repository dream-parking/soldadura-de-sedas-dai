from abc import ABC, abstractmethod
from typing import Callable, Optional

from app.adapters.repository import (
    AbstractDetalleMaterialesObraRepository,
    AbstractRepository,
    FakeAccountStatementRepository,
    FakeBiweeklyRequestRepository,
    FakeClientRepository,
    FakeDetalleMaterialesObraRepository,
    FakeMaterialRepository,
    FakePayrollRepository,
    FakeProjectRepository,
    FakeQuoteRepository,
    FakeTechnicalMeasurementRepository,
    FakeWorkerAssignmentRepository,
    FakeWorkerRepository,
    SqlAlchemyAccountStatementRepository,
    SqlAlchemyBiweeklyRequestRepository,
    SqlAlchemyClientRepository,
    SqlAlchemyDetalleMaterialesObraRepository,
    SqlAlchemyMaterialRepository,
    SqlAlchemyPayrollRepository,
    SqlAlchemyProjectRepository,
    SqlAlchemyQuoteRepository,
    SqlAlchemyTechnicalMeasurementRepository,
    SqlAlchemyWorkerAssignmentRepository,
    SqlAlchemyWorkerRepository,
)


class AbstractUnitOfWork(ABC):
    """Abstracción de Unit of Work para coordinar repositorios y transacciones."""

    clients: AbstractRepository
    quotes: AbstractRepository
    projects: AbstractRepository
    workers: AbstractRepository
    worker_assignments: AbstractRepository
    payrolls: AbstractRepository
    materials: AbstractRepository
    detalle_materiales: AbstractDetalleMaterialesObraRepository
    technical_measurements: AbstractRepository
    biweekly_requests: AbstractRepository
    account_statements: AbstractRepository

    def __enter__(self) -> "AbstractUnitOfWork":
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_value: Optional[BaseException],
        traceback: Optional[object],
    ) -> Optional[bool]:
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        return False

    @abstractmethod
    def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def rollback(self) -> None:
        raise NotImplementedError


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory: Callable[[], object]):
        self.session_factory = session_factory
        self.session = None
        self.clients = None
        self.quotes = None
        self.projects = None
        self.workers = None
        self.worker_assignments = None
        self.payrolls = None
        self.materials = None
        self.detalle_materiales = None
        self.technical_measurements = None
        self.biweekly_requests = None
        self.account_statements = None

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        self.session = self.session_factory()
        self.clients = SqlAlchemyClientRepository(self.session)
        self.quotes = SqlAlchemyQuoteRepository(self.session)
        self.projects = SqlAlchemyProjectRepository(self.session)
        self.workers = SqlAlchemyWorkerRepository(self.session)
        self.worker_assignments = SqlAlchemyWorkerAssignmentRepository(self.session)
        self.payrolls = SqlAlchemyPayrollRepository(self.session)
        self.materials = SqlAlchemyMaterialRepository(self.session)
        self.detalle_materiales = SqlAlchemyDetalleMaterialesObraRepository(self.session)
        self.technical_measurements = SqlAlchemyTechnicalMeasurementRepository(self.session)
        self.biweekly_requests = SqlAlchemyBiweeklyRequestRepository(self.session)
        self.account_statements = SqlAlchemyAccountStatementRepository(self.session)
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_value: Optional[BaseException],
        traceback: Optional[object],
    ) -> Optional[bool]:
        try:
            return super().__exit__(exc_type, exc_value, traceback)
        finally:
            if self.session is not None:
                self.session.close()
                self.session = None

    def commit(self) -> None:
        if self.session is None:
            raise RuntimeError("No hay sesión activa para confirmar la transacción.")
        self.session.commit()

    def rollback(self) -> None:
        if self.session is None:
            return
        self.session.rollback()


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(
        self,
        clients: Optional[list] = None,
        quotes: Optional[list] = None,
        projects: Optional[list] = None,
        workers: Optional[list] = None,
        assignments: Optional[list] = None,
        payrolls: Optional[list] = None,
        materials: Optional[list] = None,
        detalles: Optional[list] = None,
        measurements: Optional[list] = None,
        biweekly_requests: Optional[list] = None,
        account_statements: Optional[list] = None,
    ):
        self.clients = FakeClientRepository(clients)
        self.quotes = FakeQuoteRepository(quotes)
        self.projects = FakeProjectRepository(projects)
        self.workers = FakeWorkerRepository(workers)
        self.worker_assignments = FakeWorkerAssignmentRepository(assignments)
        self.payrolls = FakePayrollRepository(payrolls)
        self.materials = FakeMaterialRepository(materials)
        self.detalle_materiales = FakeDetalleMaterialesObraRepository(detalles)
        self.technical_measurements = FakeTechnicalMeasurementRepository(measurements)
        self.biweekly_requests = FakeBiweeklyRequestRepository(biweekly_requests)
        self.account_statements = FakeAccountStatementRepository(account_statements)
        self.committed = False
        self.rolled_back = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True

    def __enter__(self) -> "FakeUnitOfWork":
        self.committed = False
        self.rolled_back = False
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_value: Optional[BaseException],
        traceback: Optional[object],
    ) -> Optional[bool]:
        return super().__exit__(exc_type, exc_value, traceback)
