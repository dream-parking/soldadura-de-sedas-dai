"""app/entrypoints/dependencies.py

Dependencias de FastAPI para inyectar un Unit of Work real (SQLAlchemy + Postgres)
en los endpoints, sin acoplar los routers a los detalles de conexión.

Los tests sobreescriben `get_unit_of_work` (vía app.dependency_overrides) con un
FakeUnitOfWork para no depender de una base de datos real.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.adapters import orm
from app.adapters.unit_of_work import AbstractUnitOfWork, SqlAlchemyUnitOfWork
from app.config import get_postgres_uri

_engine = None
_session_factory = None


def _get_session_factory():
    global _engine, _session_factory

    if not orm.mapper_registry.mappers:
        orm.start_mappers()

    if _session_factory is None:
        _engine = create_engine(get_postgres_uri())
        _session_factory = sessionmaker(bind=_engine)

    return _session_factory


def get_unit_of_work() -> AbstractUnitOfWork:
    """Provee un Unit of Work nuevo (sin abrir sesión) por request.

    El endpoint es responsable de abrirlo con `with uow:`; ahí es donde
    SqlAlchemyUnitOfWork crea la sesión real y hace commit/rollback.
    """
    return SqlAlchemyUnitOfWork(_get_session_factory())
