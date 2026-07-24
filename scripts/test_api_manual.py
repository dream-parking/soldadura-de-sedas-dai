
"""scripts/test_api_manual.py
 
Script de pruebas manuales con la librería `requests` (Python Crash Course,
Cap. Proyectos: consumo práctico de APIs REST).
 
Recorre el flujo completo de negocio: Cliente -> Cotización -> Proyecto ->
Trabajador -> Estado de Cuenta -> Solicitud Quincenal. 
 
Requiere que la API esté corriendo localmente (por ejemplo con `uvicorn`)
y que la base de datos esté vacía o que los IDs usados aquí no existan
todavía (si ya existen, la API va a responder 409/400 por duplicados).
 
Uso:
    python scripts/test_api_manual.py
"""
import random
import string
import sys
 
import requests
 
BASE_URL = "http://localhost:8000/api"
 
 
def _print_step(title: str) -> None:
    print(f"\n{'=' * 60}\n{title}\n{'=' * 60}")
 
 
def _random_suffix(length: int) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))
 
 
def _check(response: requests.Response, expected_status: int) -> dict:
    """Imprime el resultado de la petición y corta el script si algo falla."""
    print(f"{response.request.method} {response.request.url} -> {response.status_code}")
    try:
        body = response.json()
    except ValueError:
        body = {}
    print(body)
 
    if response.status_code != expected_status:
        print(f"\nSe esperaba {expected_status} y llegó {response.status_code}. Deteniendo el script.")
        sys.exit(1)
 
    return body
 
 
def _create_with_unique_id(
    path: str,
    base_payload: dict,
    id_field: str,
    prefix: str,
    suffix_length: int,
    max_attempts: int = 5,
) -> tuple:
    """
    Crea un recurso vía POST probando un ID aleatorio distinto cada vez que
    el servidor responde que el ID ya existe (409 o 500 por duplicado).
    Devuelve (cuerpo_de_la_respuesta, id_usado).
    """
    response = None
    for attempt in range(1, max_attempts + 1):
        candidate_id = f"{prefix}{_random_suffix(suffix_length)}"
        payload = {**base_payload, id_field: candidate_id}
        response = requests.post(f"{BASE_URL}{path}", json=payload)
        print(f"{response.request.method} {response.request.url} -> {response.status_code} (intento {attempt})")
 
        if response.status_code == 201:
            print(response.json())
            return response.json(), candidate_id
 
        # Si no fue éxito, revisamos si es por ID duplicado para reintentar,
        # o si es otro tipo de error (ahí sí detenemos el script).
        try:
            body = response.json()
        except ValueError:
            body = {}
 
        is_duplicate = response.status_code in (409, 500)
        if not is_duplicate:
            print(body)
            print(f"\nSe esperaba 201 y llegó {response.status_code}. Deteniendo el script.")
            sys.exit(1)
 
        print(f"ID '{candidate_id}' no disponible, probando con otro...")
 
    print(f"\nNo se pudo crear el recurso en '{path}' tras {max_attempts} intentos.")
    sys.exit(1)
 
 
def main() -> None:
    # 1. Crear cliente
    _print_step("1. Crear cliente")
    _, client_id = _create_with_unique_id(
        "/clients",
        {
            "client_company_name": "Constructora Demo S.A.",
            "client_phone": "22990011",
            "registration_date": "2026-01-10",
            "client_email": "demo@constructora.com",
        },
        id_field="client_id",
        prefix="C",
        suffix_length=3,
    )
 
    # 2. Crear cotización para ese cliente
    _print_step("2. Crear cotización")
    _, quote_id = _create_with_unique_id(
        "/quotes",
        {
            "client_id": client_id,
            "quote_issue_date": "2026-01-15",
            "quote_job_description": "Techo industrial nave demo",
            "quote_estimated_amount": 15000.0,
            "notes": "Cotización generada por el script de pruebas",
        },
        id_field="quote_id",
        prefix="Q",
        suffix_length=3,
    )
 
    # 3. Aprobar la cotización (un proyecto solo se puede crear desde una
    #    cotización Aprobada)
    _print_step("3. Aprobar cotización")
    _check(requests.post(f"{BASE_URL}/quotes/{quote_id}/approve"), 200)
 
    # 4. Crear el proyecto a partir de la cotización aprobada
    _print_step("4. Crear proyecto desde la cotización")
    _, project_id = _create_with_unique_id(
        "/projects",
        {
            "quote_id": quote_id,
            "project_name": "Techo Bodega Demo",
            "project_location": "Zona 12",
            "project_start_date": "2026-02-01",
            "project_estimated_end_date": "2026-04-01",
        },
        id_field="project_id",
        prefix="P",
        suffix_length=3,
    )
 
    # 5. Registrar trabajador y asignarlo al proyecto
    _print_step("5. Registrar trabajador")
    _, worker_id = _create_with_unique_id(
        "/workers",
        {
            "worker_name": "Juan Pérez",
            "worker_role": "Soldador",
            "worker_base_rate": 150.0,
        },
        id_field="worker_id",
        prefix="W",
        suffix_length=3,
    )
 
    _print_step("5b. Asignar trabajador al proyecto")
    _, assignment_id = _create_with_unique_id(
        f"/workers/{worker_id}/assignments",
        {
            "project_id": project_id,
            "assignment_date": "2026-02-05",
        },
        id_field="assignment_id",
        prefix="A",
        suffix_length=3,
    )
 
    # 6. Crear estado de cuenta del proyecto (US-22)
    _print_step("6. Crear estado de cuenta")
    statement, statement_id = _create_with_unique_id(
        "/account-statements",
        {
            "project_id": project_id,
            "date": "2026-02-15",
            "initial_budget": 15000.0,
            "amount_paid": 5000.0,
        },
        id_field="id",
        prefix="AS",
        suffix_length=3,
    )
    print(f"Saldo pendiente: {statement['remaining_amount']}")
 
    _print_step("6b. Registrar un pago adicional")
    _check(
        requests.patch(f"{BASE_URL}/account-statements/{statement_id}/payment", json={"amount_paid": 12000.0}),
        200,
    )
 
    # 7. Crear y aprobar una solicitud quincenal (US-22)
    _print_step("7. Crear solicitud quincenal")
    _, biweekly_id = _create_with_unique_id(
        "/biweekly-requests",
        {
            "project_id": project_id,
            "date": "2026-02-15",
            "status": "Pendiente",
            "amount": 3000.0,
            "notes": "Pago de quincena para mano de obra",
        },
        id_field="id",
        prefix="BR",
        suffix_length=3,
    )
 
    _print_step("7b. Aprobar la solicitud quincenal")
    _check(
        requests.patch(f"{BASE_URL}/biweekly-requests/{biweekly_id}/status", json={"status": "Aprobada"}),
        200,
    )
 
    # 8. Registrar un material y actualizarlo
    _print_step("8. Crear material")
    _, material_id = _create_with_unique_id(
        "/materiales",
        {
            "description": "Lámina galvanizada calibre 26",
            "specifications": "2.44m x 1.10m, acabado zinc",
        },
        id_field="id",
        prefix="MAT",
        suffix_length=2,  # el ID de material tiene un límite de 5 caracteres
    )
 
    _print_step("8b. Actualizar material")
    _check(
        requests.put(
            f"{BASE_URL}/materiales/{material_id}",
            json={
                "description": "Lámina galvanizada calibre 26 (actualizada)",
                "specifications": "2.44m x 1.10m, acabado zinc reforzado",
            },
        ),
        200,
    )
 
    # 9. Registrar nómina quincenal del trabajador ya asignado y actualizarla
    _print_step("9. Registrar nómina quincenal")
    _, payroll_id = _create_with_unique_id(
        "/nomina_quincenal",
        {
            "worker_id": worker_id,
            "project_id": project_id,
            "payroll_fortnight_period": "2026-02-01/2026-02-15",
            "payroll_payment_date": "2026-02-16",
            "payroll_hours_worked": 80,
            "payroll_paid_amount": 3200.0,
        },
        id_field="payroll_id",
        prefix="PR",
        suffix_length=3,
    )
 
    _print_step("9b. Actualizar nómina quincenal")
    _check(
        requests.put(
            f"{BASE_URL}/nomina_quincenal/{payroll_id}",
            json={
                "worker_id": worker_id,
                "project_id": project_id,
                "payroll_fortnight_period": "2026-02-01/2026-02-15",
                "payroll_payment_date": "2026-02-17",
                "payroll_hours_worked": 88,
                "payroll_paid_amount": 3520.0,
            },
        ),
        200,
    )
 
    # 10. Crear, actualizar y eliminar una medición técnica del proyecto
    _print_step("10. Crear medición técnica")
    _, measurement_id = _create_with_unique_id(
        "/technical-measurements/",
        {
            "project_id": project_id,
            "dimensions": 120,
            "structure_type": "Techo a dos aguas",
            "payment": 4500.0,
            "unit": "m2",
            "notes": "Medición inicial de obra",
        },
        id_field="id",
        prefix="TM",
        suffix_length=3,
    )
 
    _print_step("10b. Actualizar medición técnica (parcial)")
    _check(
        requests.patch(
            f"{BASE_URL}/technical-measurements/{measurement_id}",
            json={"payment": 4800.0, "notes": "Medición ajustada tras revisión"},
        ),
        200,
    )
 
    _print_step("10c. Eliminar medición técnica")
    _check(requests.delete(f"{BASE_URL}/technical-measurements/{measurement_id}"), 204)
 
    _print_step("Flujo completo terminado sin errores")
 
 
if __name__ == "__main__":
    main()
