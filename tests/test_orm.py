from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, clear_mappers

from app.adapters import orm
from app.domain import models
from app.domain.models import Material, MaterialUsageDetail

@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    orm.start_mappers()
    orm.mapper_registry.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    clear_mappers()


def test_client_round_trip(session):
    client = models.Client(
        client_id="c1",
        client_company_name="Soldaduras de Sedas",
        client_phone="555-1234",
        registration_date=date(2026, 1, 1),
    )
    session.add(client)
    session.commit()

    retrieved = session.get(models.Client, "c1")
    assert retrieved is client
    assert retrieved.client_company_name == "Soldaduras de Sedas"


def test_worker_assignments_relationship(session):
    worker = models.Worker(worker_id="w1", worker_name="Juan", worker_role="Soldador", worker_base_rate=10.0)
    session.add(worker)
    session.commit()

    assignment = models.WorkerAssigment(
        assignment_id="a1", worker_id="w1", project_id="p1", assignment_date=date(2026, 1, 2)
    )
    worker.assign_to_project(assignment)
    session.add(assignment)
    session.commit()

    retrieved = session.get(models.Worker, "w1")
    assert [a.assignment_id for a in retrieved.assignments] == ["a1"]


def test_material_usage_detail_round_trip(session):
    material = Material(id="m1", description="Varilla", specifications="1/2 pulgada")
    usage_detail = MaterialUsageDetail(
        project_id="p1", material_id="m1", used_quantity=10, measurement_unit="unidad"
    )
    session.add(material)
    session.add(usage_detail)
    session.commit()

    retrieved = session.get(MaterialUsageDetail, ("p1", "m1"))
    assert retrieved.used_quantity == 10
    assert retrieved.measurement_unit == "unidad"