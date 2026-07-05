from datetime import date

import pytest

from app.adapters.repository import FakeClientRepository
from app.service_layer import services
from app.service_layer.exceptions import ClientNotFound


def _crear_cliente_de_prueba(client_repo, client_id="C001"):
    return services.registrar_cliente(
        client_id=client_id,
        client_company_name="Soldaduras de Sedas",
        client_phone="555-1234",
        registration_date=date(2026, 1, 1),
        client_repo=client_repo,
        client_email="contacto@sedas.com",
    )


def test_registrar_cliente_agrega_el_cliente_al_repositorio():
    client_repo = FakeClientRepository()

    client = _crear_cliente_de_prueba(client_repo)

    assert client.client_id == "C001"
    assert client_repo.get("C001") is client


def test_registrar_cliente_permite_correo_opcional():
    client_repo = FakeClientRepository()

    client = services.registrar_cliente(
        client_id="C002",
        client_company_name="Metales del Norte",
        client_phone="555-9999",
        registration_date=date(2026, 2, 1),
        client_repo=client_repo,
    )

    assert client.client_email is None


def test_obtener_cliente_devuelve_el_cliente_existente():
    client_repo = FakeClientRepository()
    _crear_cliente_de_prueba(client_repo)

    client = services.obtener_cliente("C001", client_repo)

    assert client.client_id == "C001"


def test_obtener_cliente_lanza_client_not_found_si_no_existe():
    client_repo = FakeClientRepository()

    with pytest.raises(ClientNotFound):
        services.obtener_cliente("C999", client_repo)


def test_listar_clientes_devuelve_todos_los_registrados():
    client_repo = FakeClientRepository()
    _crear_cliente_de_prueba(client_repo, client_id="C001")
    _crear_cliente_de_prueba(client_repo, client_id="C002")

    clientes = services.listar_clientes(client_repo)

    assert {c.client_id for c in clientes} == {"C001", "C002"}


def test_listar_clientes_devuelve_lista_vacia_sin_registros():
    client_repo = FakeClientRepository()

    assert services.listar_clientes(client_repo) == []


def test_actualizar_cliente_modifica_los_campos():
    client_repo = FakeClientRepository()
    _crear_cliente_de_prueba(client_repo)

    updated = services.actualizar_cliente(
        client_id="C001",
        client_company_name="Soldaduras de Sedas S.A. de C.V.",
        client_phone="555-0000",
        registration_date=date(2026, 1, 1),
        client_repo=client_repo,
        client_email="nuevo@sedas.com",
    )

    assert updated.client_company_name == "Soldaduras de Sedas S.A. de C.V."
    stored = client_repo.get("C001")
    assert stored.client_phone == "555-0000"
    assert stored.client_email == "nuevo@sedas.com"


def test_actualizar_cliente_lanza_client_not_found_si_no_existe():
    client_repo = FakeClientRepository()

    with pytest.raises(ClientNotFound):
        services.actualizar_cliente(
            client_id="C999",
            client_company_name="No existe",
            client_phone="555-0000",
            registration_date=date(2026, 1, 1),
            client_repo=client_repo,
        )
