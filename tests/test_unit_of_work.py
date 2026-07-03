import pytest
from datetime import date

from app.adapters.unit_of_work import FakeUnitOfWork
from app.domain.models import Project


def test_fake_unit_of_work_commits_on_exit():
    uow = FakeUnitOfWork(projects=[])
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

    with uow:
        uow.projects.add(project)
        assert uow.projects.get("P001") is project

    assert uow.committed is True
    assert uow.rolled_back is False


def test_fake_unit_of_work_rolls_back_on_exception():
    uow = FakeUnitOfWork(projects=[])
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

    with pytest.raises(ValueError):
        with uow:
            uow.projects.add(project)
            raise ValueError("error simulado")

    assert uow.committed is False
    assert uow.rolled_back is True
