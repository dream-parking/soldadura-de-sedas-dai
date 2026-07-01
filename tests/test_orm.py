from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, clear_mappers

from app.adapters import orm
from app.domain import models
from app.domain.materials import Material, MaterialProjectDetail


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    orm.start_mappers()
    orm.metadata.create_all(engine)
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


def test_material_project_detail_round_trip(session):
    material = Material(id=1, description="Varilla", specifications="1/2 pulgada")
    detail = MaterialProjectDetail(
        id="d1", project_id="p1", material_id=1, quantity_used=10, unit="unidad", unit_cost=2.5
    )
    session.add(material)
    session.add(detail)
    session.commit()

    retrieved = session.get(MaterialProjectDetail, "d1")
    assert retrieved.total_cost == 25.0
