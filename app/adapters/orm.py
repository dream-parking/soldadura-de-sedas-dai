"""app/adapters/orm.py"""
from sqlalchemy import Table, Column, String, Float, Date, Integer, ForeignKey
from sqlalchemy.orm import registry, relationship

from app.domain import models

mapper_registry = registry()

# Clientes
clients = Table(
    "clients",
    mapper_registry.metadata,
    Column("client_id", String(50), primary_key=True),
    Column("client_company_name", String(200), nullable=False),
    Column("client_phone", String(30), nullable=False),
    Column("registration_date", Date, nullable=False),
    Column("client_email", String(150), nullable=True),
)

# Cotizaciones
quotes = Table(
    "quotes",
    mapper_registry.metadata,
    Column("quote_id", String(50), primary_key=True),
    Column("client_id", String(50), ForeignKey("clients.client_id"), nullable=False),
    Column("quote_issue_date", Date, nullable=False),
    Column("quote_job_description", String(500), nullable=False),
    Column("quote_estimated_amount", Float, nullable=False),
    Column("quote_status", String(30), nullable=False),
    Column("notes", String(500), nullable=True),
)

# Proyectos
projects = Table(
    "projects",
    mapper_registry.metadata,
    Column("project_id", String(5), primary_key=True),
    Column("client_id", String(50), ForeignKey("clients.client_id"), nullable=False),
    Column("quote_id", String(50), ForeignKey("quotes.quote_id"), nullable=False),
    Column("project_name", String(200), nullable=False),
    Column("project_location", String(200), nullable=False),
    Column("project_start_date", Date, nullable=False),
    Column("project_total_cost", Float, nullable=False),
    Column("project_status", String(30), nullable=False),
    Column("project_estimated_end_date", Date, nullable=True),
)

# Trabajadores
workers = Table(
    "workers",
    mapper_registry.metadata,
    Column("worker_id", String(5), primary_key=True),
    Column("worker_name", String(200), nullable=False),
    Column("worker_role", String(100), nullable=False),
    Column("worker_base_rate", Float, nullable=False),
)

# Asignación del personal
worker_assignments = Table(
    "worker_assignments",
    mapper_registry.metadata,
    Column("assignment_id", String(5), primary_key=True),
    Column("worker_id", String(5), ForeignKey("workers.worker_id"), nullable=False),
    Column("project_id", String(5), ForeignKey("projects.project_id"), nullable=False),
    Column("assignment_date", Date, nullable=False),
)

# Nomina 
payrolls = Table(
    "payrolls",
    mapper_registry.metadata,
    Column("payroll_id", String(5), primary_key=True),
    Column("worker_id", String(5), ForeignKey("workers.worker_id"), nullable=False),
    Column("project_id", String(5), ForeignKey("projects.project_id"), nullable=False),
    Column("payroll_fortnight_period", String(30), nullable=False),
    Column("payroll_payment_date", Date, nullable=False),
    Column("payroll_hours_worked", Float, nullable=True),
    Column("payroll_paid_amount", Float, nullable=True),
)

# Materiales
materials = Table(
    "materials",
    mapper_registry.metadata,
    Column("id", String(5), primary_key=True),
    Column("description", String(300), nullable=False),
    Column("specifications", String(300), nullable=False),
)

# Detalle de uso de materiales por obra
material_usage_details = Table(
    "material_usage_details",
    mapper_registry.metadata,
    Column("project_id", String(5), ForeignKey("projects.project_id"), primary_key=True),
    Column("material_id", String(5), ForeignKey("materials.id"), primary_key=True),
    Column("used_quantity", Float, nullable=False),
    Column("measurement_unit", String(10), nullable=False),
)

# Medición técnica
technical_measurements = Table(
    "technical_measurements",
    mapper_registry.metadata,
    Column("id", String(5), primary_key=True),
    Column("project_id", String(5), ForeignKey("projects.project_id"), nullable=False),
    Column("dimensions", Integer, nullable=False),
    Column("structure_type", String(100), nullable=False),
    Column("payment", Float, nullable=False),
    Column("unit", String(10), nullable=False),
    Column("notes", String(300), nullable=True),
)

# Solicitud quincenal
biweekly_requests = Table(
    "biweekly_requests",
    mapper_registry.metadata,
    Column("id", String(5), primary_key=True),
    Column("project_id", String(5), ForeignKey("projects.project_id"), nullable=False),
    Column("date", String(20), nullable=False),
    Column("status", String(30), nullable=False),
    Column("amount", Float, nullable=False),
    Column("notes", String(300), nullable=True),
)

# Estado de cuenta
account_statements = Table(
    "account_statements",
    mapper_registry.metadata,
    Column("id", String(5), primary_key=True),
    Column("project_id", String(5), ForeignKey("projects.project_id"), nullable=False),
    Column("date", String(20), nullable=False),
    Column("initial_budget", Float, nullable=False),
    Column("amount_paid", Float, nullable=False),
)

def start_mappers():
    mapper_registry.map_imperatively(models.Client, clients)
    mapper_registry.map_imperatively(models.Quote, quotes)
    mapper_registry.map_imperatively(models.Project, projects)

    mapper_registry.map_imperatively(
        models.Worker,
        workers,
        properties={
            "assignments": relationship(models.WorkerAssigment, backref="worker"),
            "payrolls": relationship(models.Payroll, backref="worker"),
        },
    )

    mapper_registry.map_imperatively(models.WorkerAssigment, worker_assignments)
    mapper_registry.map_imperatively(models.Payroll, payrolls)
    mapper_registry.map_imperatively(models.Material, materials)
    mapper_registry.map_imperatively(models.MaterialUsageDetail, material_usage_details)
    mapper_registry.map_imperatively(models.TechnicalMeasurement, technical_measurements)
    mapper_registry.map_imperatively(models.BiweeklyRequest, biweekly_requests)
    mapper_registry.map_imperatively(models.AccountStatement, account_statements)