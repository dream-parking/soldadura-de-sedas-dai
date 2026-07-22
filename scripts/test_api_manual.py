"""

Script de pruebas manuales con la librería `requests` 

Recorre el flujo completo de negocio: Cliente -> Cotización -> Proyecto ->
Trabajador -> Estado de Cuenta -> Solicitud Quincenal. 

Requiere que la API esté corriendo localmente 
y que la base de datos esté vacía o que los IDs usados aquí no existan
todavía (si ya existen, la API va a responder 409/400 por duplicados).

Uso:
    python scripts/test_api_manual.py
"""
import sys

import requests

BASE_URL = "http://localhost:8000/api"


def _print_step(title: str) -> None:
    print(f"\n{'=' * 60}\n{title}\n{'=' * 60}")


def _check(response: requests.Response, expected_status: int) -> dict:
    """Imprime el resultado de la petición y corta el script si algo falla."""
    print(f"{response.request.method} {response.request.url} -> {response.status_code}")
    try:
        body = response.json()
    except ValueError:
        body = {}
    print(body)

    if response.status_code != expected_status:
        print(f"\n⚠️  Se esperaba {expected_status} y llegó {response.status_code}. Deteniendo el script.")
        sys.exit(1)

    return body


def main() -> None:
    # 1. Crear cliente
    _print_step("1. Crear cliente")
    client_payload = {
        "client_id": "C900",
        "client_company_name": "Constructora Demo S.A.",
        "client_phone": "22990011",
        "registration_date": "2026-01-10",
        "client_email": "demo@constructora.com",
    }
    _check(requests.post(f"{BASE_URL}/clients", json=client_payload), 201)

    # 2. Crear cotización para ese cliente
    _print_step("2. Crear cotización")
    quote_payload = {
        "quote_id": "Q900",
        "client_id": "C900",
        "quote_issue_date": "2026-01-15",
        "quote_job_description": "Techo industrial nave demo",
        "quote_estimated_amount": 15000.0,
        "notes": "Cotización generada por el script de pruebas",
    }
    _check(requests.post(f"{BASE_URL}/quotes", json=quote_payload), 201)

    # 3. Aprobar la cotización (un proyecto solo se puede crear desde una
    #    cotización Aprobada)
    _print_step("3. Aprobar cotización")
    _check(requests.post(f"{BASE_URL}/quotes/Q900/approve"), 200)

    # 4. Crear el proyecto a partir de la cotización aprobada
    _print_step("4. Crear proyecto desde la cotización")
    project_payload = {
        "project_id": "P900",
        "quote_id": "Q900",
        "project_name": "Techo Bodega Demo",
        "project_location": "Zona 12",
        "project_start_date": "2026-02-01",
        "project_estimated_end_date": "2026-04-01",
    }
    _check(requests.post(f"{BASE_URL}/projects", json=project_payload), 201)

    # 5. Registrar trabajador y asignarlo al proyecto
    _print_step("5. Registrar trabajador")
    worker_payload = {
        "worker_id": "W900",
        "worker_name": "Juan Pérez",
        "worker_role": "Soldador",
        "worker_base_rate": 150.0,
    }
    _check(requests.post(f"{BASE_URL}/workers", json=worker_payload), 201)

    _print_step("5b. Asignar trabajador al proyecto")
    assignment_payload = {
        "assignment_id": "A900",
        "project_id": "P900",
        "assignment_date": "2026-02-05",
    }
    _check(requests.post(f"{BASE_URL}/workers/W900/assignments", json=assignment_payload), 201)

    # 6. Crear estado de cuenta del proyecto (US-22)
    _print_step("6. Crear estado de cuenta")
    statement_payload = {
        "id": "AS900",
        "project_id": "P900",
        "date": "2026-02-15",
        "initial_budget": 15000.0,
        "amount_paid": 5000.0,
    }
    statement = _check(requests.post(f"{BASE_URL}/account-statements", json=statement_payload), 201)
    print(f"Saldo pendiente: {statement['remaining_amount']}")

    _print_step("6b. Registrar un pago adicional")
    _check(
        requests.patch(f"{BASE_URL}/account-statements/AS900/payment", json={"amount_paid": 12000.0}),
        200,
    )

    # 7. Crear y aprobar una solicitud quincenal (US-22)
    _print_step("7. Crear solicitud quincenal")
    biweekly_payload = {
        "id": "BR900",
        "project_id": "P900",
        "date": "2026-02-15",
        "status": "Pendiente",
        "amount": 3000.0,
        "notes": "Pago de quincena para mano de obra",
    }
    _check(requests.post(f"{BASE_URL}/biweekly-requests", json=biweekly_payload), 201)

    _print_step("7b. Aprobar la solicitud quincenal")
    _check(
        requests.patch(f"{BASE_URL}/biweekly-requests/BR900/status", json={"status": "Aprobada"}),
        200,
    )

    _print_step("Flujo completo terminado sin errores ✅")


if __name__ == "__main__":
    main()
