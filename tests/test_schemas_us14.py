from datetime import date

import pytest
from pydantic import ValidationError

from app.domain.models import Client, AccountStatement
from app.entrypoints.schemas import (
    ClientCreate,
    ClientRead,
    QuoteCreate,
    ProjectCreate,
    WorkerCreate,
    WorkerAssignmentCreate,
    PayrollCreate,
    MaterialCreate,
    MaterialUsageDetailCreate,
    TechnicalMeasurementCreate,
    BiweeklyRequestCreate,
    AccountStatementCreate,
    AccountStatementRead,
)


def _valid_client_payload(**overrides):
    payload = dict(
        client_id="C001",
        client_company_name="Soldaduras de Sedas",
        client_phone="555-1234",
        registration_date=date(2026, 1, 1),
        client_email="contacto@sedas.com",
    )
    payload.update(overrides)
    return payload


def test_client_create_accepts_valid_payload():
    client = ClientCreate(**_valid_client_payload())
    assert client.client_id == "C001"
    assert client.client_email == "contacto@sedas.com"


def test_client_create_allows_missing_optional_email():
    client = ClientCreate(**_valid_client_payload(client_email=None))
    assert client.client_email is None


def test_client_create_rejects_invalid_email_format():
    with pytest.raises(ValidationError):
        ClientCreate(**_valid_client_payload(client_email="no-es-un-email"))


def test_client_create_rejects_field_too_long():
    with pytest.raises(ValidationError):
        ClientCreate(**_valid_client_payload(client_id="X" * 51))


def test_client_create_rejects_missing_required_field():
    payload = _valid_client_payload()
    del payload["client_phone"]
    with pytest.raises(ValidationError):
        ClientCreate(**payload)


def test_client_read_builds_from_domain_object():
    domain_client = Client(
        client_id="C001",
        client_company_name="Soldaduras de Sedas",
        client_phone="555-1234",
        registration_date=date(2026, 1, 1),
    )
    schema = ClientRead.model_validate(domain_client)
    assert schema.client_id == "C001"
    assert schema.client_email is None


def test_quote_create_rejects_status_outside_allowed_values():
    with pytest.raises(ValidationError):
        QuoteCreate(
            quote_id="Q001",
            client_id="C001",
            quote_issue_date=date(2026, 1, 1),
            quote_job_description="Techo",
            quote_estimated_amount=1000.0,
            quote_status="Cancelada",
        )


def test_quote_create_rejects_negative_amount():
    with pytest.raises(ValidationError):
        QuoteCreate(
            quote_id="Q001",
            client_id="C001",
            quote_issue_date=date(2026, 1, 1),
            quote_job_description="Techo",
            quote_estimated_amount=-1.0,
            quote_status="Pendiente",
        )


def test_project_create_rejects_status_outside_allowed_values():
    with pytest.raises(ValidationError):
        ProjectCreate(
            project_id="P001",
            client_id="C001",
            quote_id="Q001",
            project_name="Techo Bodega Norte",
            project_location="Zona 12",
            project_start_date=date(2026, 1, 1),
            project_total_cost=1000.0,
            project_status="Cancelado",
        )


def test_worker_create_rejects_negative_base_rate():
    with pytest.raises(ValidationError):
        WorkerCreate(worker_id="W001", worker_name="Juan", worker_role="Soldador", worker_base_rate=-5.0)


def test_worker_assignment_create_accepts_valid_payload():
    assignment = WorkerAssignmentCreate(
        assignment_id="A001", worker_id="W001", project_id="P001", assignment_date=date(2026, 1, 2)
    )
    assert assignment.assignment_id == "A001"


def test_payroll_create_allows_omitting_optional_fields():
    payroll = PayrollCreate(
        payroll_id="PR001",
        worker_id="W001",
        project_id="P001",
        payroll_fortnight_period="2026-Q1",
        payroll_payment_date=date(2026, 1, 15),
    )
    assert payroll.payroll_hours_worked is None
    assert payroll.payroll_paid_amount is None


def test_payroll_create_rejects_negative_hours_worked():
    with pytest.raises(ValidationError):
        PayrollCreate(
            payroll_id="PR001",
            worker_id="W001",
            project_id="P001",
            payroll_fortnight_period="2026-Q1",
            payroll_payment_date=date(2026, 1, 15),
            payroll_hours_worked=-10.0,
        )


def test_material_create_rejects_empty_description():
    with pytest.raises(ValidationError):
        MaterialCreate(id="M001", description="", specifications="1/2 pulgada")


def test_material_usage_detail_create_rejects_zero_quantity():
    with pytest.raises(ValidationError):
        MaterialUsageDetailCreate(
            project_id="P001", material_id="M001", used_quantity=0, measurement_unit="unidad"
        )


def test_technical_measurement_create_rejects_zero_dimensions():
    with pytest.raises(ValidationError):
        TechnicalMeasurementCreate(
            id="TM001",
            project_id="P001",
            dimensions=0,
            structure_type="Techo",
            payment=100.0,
            unit="m2",
            notes="ninguna",
        )


def test_biweekly_request_create_accepts_valid_payload():
    request = BiweeklyRequestCreate(
        id="BR001",
        project_id="P001",
        date="2026-01-15",
        status="Pendiente",
        amount=500.0,
        notes="Sin observaciones",
    )
    assert request.id == "BR001"


def test_account_statement_create_accepts_valid_payload():
    statement = AccountStatementCreate(
        id="AS001", project_id="P001", date="2026-01-15", initial_budget=1000.0, amount_paid=400.0
    )
    assert statement.initial_budget == 1000.0


def test_account_statement_read_includes_computed_remaining_amount():
    domain_statement = AccountStatement(
        id="AS001", project_id="P001", date="2026-01-15", initial_budget=1000.0, amount_paid=400.0
    )
    schema = AccountStatementRead.model_validate(domain_statement)
    assert schema.remaining_amount == 600.0