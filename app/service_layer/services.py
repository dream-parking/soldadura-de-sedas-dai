from datetime import date
from typing import Optional
 
from app.domain.models import (
    Client,
    Worker,
    WorkerAssigment,
    Payroll,
    Material,
    MaterialUsageDetail,
    TechnicalMeasurement,
    AccountStatement,
    BiweeklyRequest,
    Quote,
    Project
)
from app.service_layer.exceptions import (
    ClientNotFound,
    WorkerNotFound,
    ProjectNotFound,
    MaterialNotFound,
    QuoteNotFound,
    QuoteNotApproved,
    AccountStatementNotFound,
    BiweeklyRequestNotFound,
)
 
 
# Helpers de validación reutilizables
 
def _get_worker_or_raise(worker_id: str, worker_repo) -> Worker:
    worker = worker_repo.get(worker_id)
    if worker is None:
        raise WorkerNotFound(f"No existe un trabajador con id '{worker_id}'")
    return worker
 
 
def _get_client_or_raise(client_id: str, client_repo) -> Client:
    client = client_repo.get(client_id)
    if client is None:
        raise ClientNotFound(f"No existe un cliente con id '{client_id}'")
    return client
 
 
def _assert_project_exists(project_id: str, project_repo) -> None:
    if project_repo.get(project_id) is None:
        raise ProjectNotFound(f"No existe un proyecto con id '{project_id}'")
 
 
def _assert_material_exists(material_id, material_repo) -> None:
    if material_repo.get(material_id) is None:
        raise MaterialNotFound(f"No existe un material con id '{material_id}'")
 
 
def _get_quote_or_raise(quote_id: str, quote_repo) -> Quote:
    quote = quote_repo.get(quote_id)
    if quote is None:
        raise QuoteNotFound(f"No existe una cotización con id '{quote_id}'")
    return quote
 
 
def _get_account_statement_or_raise(statement_id: str, statement_repo) -> AccountStatement:
    statement = statement_repo.get(statement_id)
    if statement is None:
        raise AccountStatementNotFound(
            f"No existe un estado de cuenta con id '{statement_id}'"
        )
    return statement
 
 
def _get_biweekly_request_or_raise(request_id: str, request_repo) -> BiweeklyRequest:
    request = request_repo.get(request_id)
    if request is None:
        raise BiweeklyRequestNotFound(
            f"No existe una solicitud quincenal con id '{request_id}'"
        )
    return request
 
 
# Registrar trabajador
def registrar_trabajador(
    worker_id: str,
    worker_name: str,
    worker_role: str,
    worker_base_rate: float,
    worker_repo,
) -> Worker:
    worker = Worker(
        worker_id=worker_id,
        worker_name=worker_name,
        worker_role=worker_role,
        worker_base_rate=worker_base_rate,
    )
    worker_repo.add(worker)
    return worker
 
 
# Asignar trabajador a proyecto
def asignar_trabajador_a_proyecto(
    assignment_id: str,
    worker_id: str,
    project_id: str,
    assignment_date: date,
    worker_repo,
    project_repo,
    assignment_repo,
) -> WorkerAssigment:
    worker = _get_worker_or_raise(worker_id, worker_repo)
    _assert_project_exists(project_id, project_repo)
 
    assignment = WorkerAssigment(
        assignment_id=assignment_id,
        worker_id=worker_id,
        project_id=project_id,
        assignment_date=assignment_date,
    )
 
    # Mantiene el objeto de dominio Worker consistente con su propia lista de asignaciones
    worker.assign_to_project(assignment)
 
    assignment_repo.add(assignment)
    return assignment
 
 
#  Registrar nómina quincenal
 
def registrar_nomina_quincenal(
    payroll_id: str,
    worker_id: str,
    project_id: str,
    payroll_fortnight_period: str,
    payroll_payment_date: date,
    worker_repo,
    project_repo,
    payroll_repo,
    payroll_hours_worked: Optional[float] = None,
    payroll_paid_amount: Optional[float] = None,
) -> Payroll:
    worker = _get_worker_or_raise(worker_id, worker_repo)
    _assert_project_exists(project_id, project_repo)
 
    payroll = Payroll(
        payroll_id=payroll_id,
        worker_id=worker_id,
        project_id=project_id,
        payroll_fortnight_period=payroll_fortnight_period,
        payroll_payment_date=payroll_payment_date,
        payroll_hours_worked=payroll_hours_worked,
        payroll_paid_amount=payroll_paid_amount,
    )
 
    worker.add_payroll(payroll)
 
    payroll_repo.add(payroll)
    return payroll
 
 
def listar_nomina_quincenal(payroll_repo) -> list[Payroll]:
    return payroll_repo.list()
 
 
def obtener_nomina_quincenal(payroll_id: str, payroll_repo):
    return payroll_repo.get(payroll_id)
 
 
def actualizar_nomina_quincenal(
    payroll_id: str,
    worker_id: str,
    project_id: str,
    payroll_fortnight_period: str,
    payroll_payment_date: date,
    worker_repo,
    project_repo,
    payroll_repo,
    payroll_hours_worked: Optional[float] = None,
    payroll_paid_amount: Optional[float] = None,
) -> Payroll | None:
    payroll = payroll_repo.get(payroll_id)
    if payroll is None:
        return None
 
    _get_worker_or_raise(worker_id, worker_repo)
    _assert_project_exists(project_id, project_repo)
 
    payroll.worker_id = worker_id
    payroll.project_id = project_id
    payroll.payroll_fortnight_period = payroll_fortnight_period
    payroll.payroll_payment_date = payroll_payment_date
    payroll.payroll_hours_worked = payroll_hours_worked
    payroll.payroll_paid_amount = payroll_paid_amount
 
    payroll_repo.update(payroll)
    return payroll
 
 
# Agregar material
def agregar_material(
    material_id,
    description: str,
    specifications: str,
    material_repo,
) -> Material:
    material = Material(
        id=material_id,
        description=description,
        specifications=specifications,
    )
    material_repo.add(material)
    return material
 
# Listar materiales
def listar_materiales(material_repo) -> list[Material]:
    return material_repo.list()
 
#obtener material por id
def obtener_material(material_id, material_repo) -> Material:
    material = material_repo.get(material_id)
    if material is None:
        raise MaterialNotFound(f"No existe un material con id '{material_id}'")
    return material
 
# Actualizar material
def actualizar_material(
    material_id,
    description: str,
    specifications: str,
    material_repo,
) -> Material:
    material = obtener_material(material_id, material_repo)
 
    material.description = description
    material.specifications = specifications
 
    material_repo.update(material)
    return material
 
# 5. Registrar uso de material en obra
def registrar_uso_material_en_obra(
    project_id: str,
    material_id,
    used_quantity: float,
    measurement_unit: str,
    project_repo,
    material_repo,
    usage_detail_repo,
) -> MaterialUsageDetail:
    _assert_project_exists(project_id, project_repo)
    _assert_material_exists(material_id, material_repo)
 
    usage_detail = MaterialUsageDetail(
        project_id=project_id,
        material_id=material_id,
        used_quantity=used_quantity,
        measurement_unit=measurement_unit,
    )
    usage_detail_repo.add(usage_detail)
    return usage_detail
 
 
# 6. Registrar medida técnica
def registrar_medida_tecnica(
    measurement_id: str,
    project_id: str,
    dimensions: int,
    structure_type: str,
    payment: float,
    unit: str,
    notes: str,
    project_repo,
    measurement_repo,
) -> TechnicalMeasurement:
    _assert_project_exists(project_id, project_repo)
 
    measurement = TechnicalMeasurement(
        id=measurement_id,
        project_id=project_id,
        dimensions=dimensions,
        structure_type=structure_type,
        payment=payment,
        unit=unit,
        notes=notes,
    )
    measurement_repo.add(measurement)
    return measurement
 
 
def listar_medidas_tecnicas(measurement_repo) -> list[TechnicalMeasurement]:
    return measurement_repo.list()
 
 
def obtener_medida_tecnica(measurement_id: str, measurement_repo):
    return measurement_repo.get(measurement_id)
 
 
def actualizar_medida_tecnica(
    measurement_id: str,
    project_id: str | None,
    dimensions: int | None,
    structure_type: str | None,
    payment: float | None,
    unit: str | None,
    notes: str | None,
    measurement_repo,
) -> TechnicalMeasurement | None:
    measurement = measurement_repo.get(measurement_id)
    if not measurement:
        return None
 
    if project_id is not None:
        measurement.project_id = project_id
    if dimensions is not None:
        measurement.dimensions = dimensions
    if structure_type is not None:
        measurement.structure_type = structure_type
    if payment is not None:
        measurement.payment = payment
    if unit is not None:
        measurement.unit = unit
    if notes is not None:
        measurement.notes = notes
 
    measurement_repo.update(measurement)
    return measurement
 
 
def delete_technical_measurement(measurement_id: str, measurement_repo) -> bool:
    measurement = measurement_repo.get(measurement_id)
    if not measurement:
        return False
 
    if hasattr(measurement_repo, "delete"):
        measurement_repo.delete(measurement)
        return True
    raise NotImplementedError("El repositorio de mediciones técnicas no soporta eliminación")
 
 
# 7. Registrar estado de cuenta
def registrar_estado_de_cuenta(
    statement_id: str,
    project_id: str,
    statement_date: str,
    initial_budget: float,
    amount_paid: float,
    project_repo,
    statement_repo,
) -> AccountStatement:
    _assert_project_exists(project_id, project_repo)
 
    statement = AccountStatement(
        id=statement_id,
        project_id=project_id,
        date=statement_date,
        initial_budget=initial_budget,
        amount_paid=amount_paid,
    )
    statement_repo.add(statement)
    return statement
 
 
# 8. Registrar solicitud quincenal
def registrar_solicitud_quincenal(
    request_id: str,
    project_id: str,
    request_date: str,
    status: str,
    amount: float,
    notes: str,
    project_repo,
    request_repo,
) -> BiweeklyRequest:
    _assert_project_exists(project_id, project_repo)
 
    request = BiweeklyRequest(
        id=request_id,
        project_id=project_id,
        date=request_date,
        status=status,
        amount=amount,
        notes=notes,
    )
    request_repo.add(request)
    return request
 
 
# 8b. Consultar solicitud quincenal por id
def obtener_solicitud_quincenal(request_id: str, request_repo) -> BiweeklyRequest:
    return _get_biweekly_request_or_raise(request_id, request_repo)
 
 
# 8c. Listar solicitudes quincenales por proyecto
def listar_solicitudes_por_proyecto(
    project_id: str, project_repo, request_repo
) -> list[BiweeklyRequest]:
    _assert_project_exists(project_id, project_repo)
    return [r for r in request_repo.list() if r.project_id == project_id]
 
 
# 8d. Actualizar el estado de una solicitud quincenal (Pendiente/Aprobada/Rechazada)
def actualizar_estado_solicitud_quincenal(
    request_id: str, new_status: str, request_repo
) -> BiweeklyRequest:
    request = _get_biweekly_request_or_raise(request_id, request_repo)
 
    valid_statuses = {"Pendiente", "Aprobada", "Rechazada"}
    if new_status not in valid_statuses:
        raise ValueError(
            f"Estado '{new_status}' inválido. Debe ser uno de: {valid_statuses}"
        )
 
    request.status = new_status
    request_repo.update(request)
    return request
 
 
# 7b. Consultar estado de cuenta por id
def obtener_estado_de_cuenta(statement_id: str, statement_repo) -> AccountStatement:
    return _get_account_statement_or_raise(statement_id, statement_repo)
 
 
# 7c. Listar estados de cuenta por proyecto
def listar_estados_de_cuenta_por_proyecto(
    project_id: str, project_repo, statement_repo
) -> list[AccountStatement]:
    _assert_project_exists(project_id, project_repo)
    return [s for s in statement_repo.list() if s.project_id == project_id]
 
 
# 7d. Registrar un pago sobre un estado de cuenta existente
def registrar_pago_estado_de_cuenta(
    statement_id: str, amount_paid: float, statement_repo
) -> AccountStatement:
    statement = _get_account_statement_or_raise(statement_id, statement_repo)
    statement.amount_paid = amount_paid
    statement_repo.update(statement)
    return statement
 
 
#9. Registrar cliente
def registrar_cliente(
    client_id: str,
    client_company_name: str,
    client_phone: str,
    registration_date: date,
    client_repo,
    client_email: Optional[str] = None,
) -> Client:
    client = Client(
        client_id=client_id,
        client_company_name=client_company_name,
        client_phone=client_phone,
        registration_date=registration_date,
        client_email=client_email,
    )
    client_repo.add(client)
    return client
 
 
# 9b. Consultar cliente por id
def obtener_cliente(client_id: str, client_repo) -> Client:
    return _get_client_or_raise(client_id, client_repo)
 
 
# 9c. Listar clientes
def listar_clientes(client_repo) -> list[Client]:
    return client_repo.list()
 
 
# 9d. Actualizar cliente
def actualizar_cliente(
    client_id: str,
    client_company_name: str,
    client_phone: str,
    registration_date: date,
    client_repo,
    client_email: Optional[str] = None,
) -> Client:
    _get_client_or_raise(client_id, client_repo)
 
    client = Client(
        client_id=client_id,
        client_company_name=client_company_name,
        client_phone=client_phone,
        registration_date=registration_date,
        client_email=client_email,
    )
    client_repo.update(client)
    return client
 
 
# 10. Crear cotización
def crear_cotizacion(
    quote_id: str,
    client_id: str,
    quote_issue_date: date,
    quote_job_description: str,
    quote_estimated_amount: float,
    client_repo,
    quote_repo,
    notes: Optional[str] = None,
) -> Quote:
    _get_client_or_raise(client_id, client_repo)
 
    quote = Quote(
        quote_id=quote_id,
        client_id=client_id,
        quote_issue_date=quote_issue_date,
        quote_job_description=quote_job_description,
        quote_estimated_amount=quote_estimated_amount,
        quote_status="Pendiente",
        notes=notes,
    )
    quote_repo.add(quote)
    return quote
 
 
# 10b. Consultar cotización por id
def obtener_cotizacion(quote_id: str, quote_repo) -> Quote:
    return _get_quote_or_raise(quote_id, quote_repo)
 
 
# 10c. Listar cotizaciones por cliente
def listar_cotizaciones_por_cliente(client_id: str, client_repo, quote_repo) -> list[Quote]:
    _get_client_or_raise(client_id, client_repo)
    return [q for q in quote_repo.list() if q.client_id == client_id]
 
 
# 10d. Actualizar estado de cotización (uso general)
def actualizar_estado_cotizacion(quote_id: str, new_status: str, quote_repo) -> Quote:
    quote = _get_quote_or_raise(quote_id, quote_repo)
 
    valid_statuses = {"Pendiente", "Aprobado", "Rechazado"}
    if new_status not in valid_statuses:
        raise ValueError(
            f"Estado '{new_status}' inválido. Debe ser uno de: {valid_statuses}"
        )
 
    quote.quote_status = new_status
    quote_repo.update(quote)
    return quote
 
 
# 10e. Aprobar cotización
def aprobar_cotizacion(quote_id: str, quote_repo) -> Quote:
    return actualizar_estado_cotizacion(quote_id, "Aprobado", quote_repo)
 
 
# 10f. Rechazar cotización
def rechazar_cotizacion(quote_id: str, quote_repo) -> Quote:
    return actualizar_estado_cotizacion(quote_id, "Rechazado", quote_repo)
 
 
# 11. Crear proyecto desde cotización aprobada
def crear_proyecto_desde_cotizacion(
    project_id: str,
    quote_id: str,
    project_name: str,
    project_location: str,
    project_start_date: date,
    quote_repo,
    project_repo,
    project_estimated_end_date: Optional[date] = None,
) -> Project:
    quote = _get_quote_or_raise(quote_id, quote_repo)
 
    if quote.quote_status != "Aprobado":
        raise QuoteNotApproved(
            f"La cotización '{quote_id}' está en estado '{quote.quote_status}'; "
            f"solo se puede crear un proyecto desde una cotización Aprobada."
        )
 
    project = Project(
        project_id=project_id,
        client_id=quote.client_id,
        quote_id=quote_id,
        project_name=project_name,
        project_location=project_location,
        project_start_date=project_start_date,
        project_total_cost=quote.quote_estimated_amount,
        project_status="In Progress",
        project_estimated_end_date=project_estimated_end_date,
    )
    project_repo.add(project)
    return project
 
 
# 11b. Consultar proyecto por id
def obtener_proyecto(project_id: str, project_repo) -> Project:
    project = project_repo.get(project_id)
    if project is None:
        raise ProjectNotFound(f"No existe un proyecto con id '{project_id}'")
    return project
 
 
# 11c. Listar proyectos por cliente
def listar_proyectos_por_cliente(client_id: str, client_repo, project_repo) -> list[Project]:
    _get_client_or_raise(client_id, client_repo)
    return [p for p in project_repo.list() if p.client_id == client_id]
 
 
# 11d. Actualizar estado de proyecto
def actualizar_estado_proyecto(project_id: str, new_status: str, project_repo) -> Project:
    project = obtener_proyecto(project_id, project_repo)
 
    valid_statuses = {"In Progress", "Completed"}
    if new_status not in valid_statuses:
        raise ValueError(
            f"Estado '{new_status}' inválido. Debe ser uno de: {valid_statuses}"
        )
 
    project.project_status = new_status
    project_repo.update(project)
    return project
 
 
# 12. Consultar trabajador por id
def obtener_trabajador(worker_id: str, worker_repo) -> Worker:
    return _get_worker_or_raise(worker_id, worker_repo)
 
 
# 12b. Listar trabajadores
def listar_trabajadores(worker_repo) -> list[Worker]:
    return worker_repo.list()
 
 
# 12c. Listar asignaciones por trabajador
def listar_asignaciones_por_trabajador(worker_id: str, worker_repo, assignment_repo) -> list[WorkerAssigment]:
    _get_worker_or_raise(worker_id, worker_repo)
    return [a for a in assignment_repo.list() if a.worker_id == worker_id]
 
 
# 12d. Listar asignaciones por proyecto
def listar_asignaciones_por_proyecto(project_id: str, project_repo, assignment_repo) -> list[WorkerAssigment]:
    _assert_project_exists(project_id, project_repo)
    return [a for a in assignment_repo.list() if a.project_id == project_id]
 
 
"""Metodos creados para definir atributos de proyecto"""
def definir_nombre_proyecto(
    project_id: str,
    new_name: str,
    project_repo
):
    project = project_repo.get(project_id)
    if project is None:
        raise ValueError(f"No existe un proyecto con id '{project_id}'")
    project.project_name = new_name
    project_repo.update(project)
    return project
 
def definir_ubicacion_proyecto(
    project_id: str,
    new_location: str,
    project_repo
):
    project = project_repo.get(project_id)
    if project is None:
        raise ValueError(f"No existe un proyecto con id '{project_id}'")
    project.project_location = new_location
    project_repo.update(project)
    return project