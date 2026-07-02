from datetime import date

from app.domain.models import Client
from app.adapters.repository import FakeClientRepository


def test_fake_repository_add_and_get():
    repo = FakeClientRepository()
    cliente = Client(
        client_id="C001",
        client_company_name="Constructora Acme",
        client_phone="7777-7777",
        registration_date=date(2026, 1, 1),
    )

    repo.add(cliente)

    resultado = repo.get("C001")
    assert resultado.client_company_name == "Constructora Acme"


def test_fake_repository_list():
    repo = FakeClientRepository()
    repo.add(Client("C001", "Empresa A", "1111", date(2026, 1, 1)))
    repo.add(Client("C002", "Empresa B", "2222", date(2026, 1, 2)))

    assert len(repo.list()) == 2


def test_fake_repository_update():
    repo = FakeClientRepository()
    cliente = Client("C001", "Empresa A", "1111", date(2026, 1, 1))
    repo.add(cliente)

    cliente_actualizado = Client("C001", "Empresa A Renovada", "1111", date(2026, 1, 1))
    repo.update(cliente_actualizado)

    assert repo.get("C001").client_company_name == "Empresa A Renovada"