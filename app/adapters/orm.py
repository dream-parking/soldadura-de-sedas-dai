"""
Mapeo clásico (Classical Mapping) de SQLAlchemy.

Principio de inversión de dependencias (Architecture Patterns with Python,
Cap. 2): este módulo importa el dominio y lo mapea a tablas. El dominio
(app/domain/*) nunca importa SQLAlchemy.
"""
from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String, Table
from sqlalchemy.orm import registry, relationship

from app.domain import models
from app.domain.BiweeklyRequest import BiweeklyRequest
from app.domain.TechnicalMeasurement import TechnicalMeasurement
from app.domain.accountStatement import AccountStatement
from app.domain.materials import Material, MaterialProjectDetail

mapper_registry = registry()
metadata = mapper_registry.metadata

clients = Table(
    "clients",
    metadata,
    Column("client_id", String(36), primary_key=True),
    Column("client_company_name", String(255), nullable=False),
    Column("client_phone", String(50), nullable=False),
    Column("registration_date", Date, nullable=False),
    Column("client_email", String(255), nullable=True),
)

quotes = Table(
    "quotes",
    metadata,
    Column("quote_id", String(36), primary_key=True),
    Column("client_id", String(36), ForeignKey("clients.client_id"), nullable=False),
    Column("quote_issue_date", Date, nullable=False),
    Column("quote_job_description", String(500), nullable=False),
    Column("quote_estimated_amount", Float, nullable=False),
    Column("quote_status", String(20), nullable=False),
    Column("notes", String(500), nullable=True),
)

projects = Table(
    "projects",
    metadata,
    Column("project_id", String(36), primary_key=True),
    Column("client_id", String(36), ForeignKey("clients.client_id"), nullable=False),
    Column("quote_id", String(36), ForeignKey("quotes.quote_id"), nullable=False),
    Column("project_name", String(255), nullable=False),
    Column("project_location", String(255), nullable=False),
    Column("project_start_date", Date, nullable=False),
    Column("project_total_cost", Float, nullable=False),
    Column("project_status", String(20), nullable=False),
    Column("project_estimated_end_date", Date, nullable=True),
)

workers = Table(
    "workers",
    metadata,
    Column("worker_id", String(36), primary_key=True),
    Column("worker_name", String(255), nullable=False),
    Column("worker_role", String(100), nullable=False),
    Column("worker_base_rate", Float, nullable=False),
)

worker_assignments = Table(
    "worker_assignments",
    metadata,
    Column("assignment_id", String(36), primary_key=True),
    Column("worker_id", String(36), ForeignKey("workers.worker_id"), nullable=False),
    Column("project_id", String(36), ForeignKey("projects.project_id"), nullable=False),
    Column("assignment_date", Date, nullable=False),
)

payrolls = Table(
    "payrolls",
    metadata,
    Column("payroll_id", String(36), primary_key=True),
    Column("worker_id", String(36), ForeignKey("workers.worker_id"), nullable=False),
    Column("project_id", String(36), ForeignKey("projects.project_id"), nullable=False),
    Column("payroll_fortnight_period", String(50), nullable=False),
    Column("payroll_payment_date", Date, nullable=False),
    Column("payroll_hours_worked", Float, nullable=True),
    Column("payroll_paid_amount", Float, nullable=True),
)

materials = Table(
    "materials",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("description", String(255), nullable=False),
    Column("specifications", String(500), nullable=False),
)

material_project_details = Table(
    "material_project_details",
    metadata,
    Column("id", String(36), primary_key=True),
    Column("project_id", String(36), ForeignKey("projects.project_id"), nullable=False),
    Column("material_id", Integer, ForeignKey("materials.id"), nullable=False),
    Column("quantity_used", Float, nullable=False),
    Column("unit", String(20), nullable=False),
    Column("unit_cost", Float, nullable=False),
)

technical_measurements = Table(
    "technical_measurements",
    metadata,
    Column("id", String(36), primary_key=True),
    Column("project_id", String(36), ForeignKey("projects.project_id"), nullable=False),
    Column("dimensions", Integer, nullable=False),
    Column("structure_type", String(100), nullable=False),
    Column("payment", Float, nullable=False),
    Column("unit", String(20), nullable=False),
    Column("notes", String(500), nullable=True),
)

account_statements = Table(
    "account_statements",
    metadata,
    Column("id", String(36), primary_key=True),
    Column("project_id", String(36), ForeignKey("projects.project_id"), nullable=False),
    Column("date", String(20), nullable=False),
    Column("initial_budget", Float, nullable=False),
    Column("amount_paid", Float, nullable=False),
)

biweekly_requests = Table(
    "biweekly_requests",
    metadata,
    Column("id", String(36), primary_key=True),
    Column("project_id", String(36), ForeignKey("projects.project_id"), nullable=False),
    Column("date", String(20), nullable=False),
    Column("status", String(20), nullable=False),
    Column("amount", Float, nullable=False),
    Column("notes", String(500), nullable=True),
)


def start_mappers():
    """Registra el mapeo clásico. Debe llamarse una sola vez al iniciar la app."""
    mapper_registry.map_imperatively(models.Client, clients)
    mapper_registry.map_imperatively(models.Quote, quotes)
    mapper_registry.map_imperatively(models.Project, projects)
    mapper_registry.map_imperatively(models.WorkerAssigment, worker_assignments)
    mapper_registry.map_imperatively(models.Payroll, payrolls)
    mapper_registry.map_imperatively(
        models.Worker,
        workers,
        properties={
            "assignments": relationship(models.WorkerAssigment),
            "payrolls": relationship(models.Payroll),
        },
    )
    mapper_registry.map_imperatively(Material, materials)
    mapper_registry.map_imperatively(MaterialProjectDetail, material_project_details)
    mapper_registry.map_imperatively(TechnicalMeasurement, technical_measurements)
    mapper_registry.map_imperatively(AccountStatement, account_statements)
    mapper_registry.map_imperatively(BiweeklyRequest, biweekly_requests)
