from sqlalchemy import Table, Column, String, Float, Date
from sqlalchemy.orm import registry

from app.domain import models

mapper_registry = registry()
# Tabla de Clientes
clients = Table(
    "clients",
    mapper_registry.metadata,
    Column("client_id", String(50), primary_key=True),
    Column("client_company_name", String(200), nullable=False),
    Column("client_phone", String(30), nullable=False),
    Column("registration_date", Date, nullable=False),
    Column("client_email", String(150), nullable=True),
)

# Tabla de cotizaciones
quotes = Table(
    "quotes",
    mapper_registry.metadata,
    Column("quote_id", String(50), primary_key=True),
    Column("client_id", String(50), nullable=False),  # FK a clients
    Column("quote_issue_date", Date, nullable=False),
    Column("quote_job_description", String(500), nullable=False),
    Column("quote_estimated_amount", Float, nullable=False),
    Column("quote_status", String(30), nullable=False),
    Column("notes", String(500), nullable=True),
)


def start_mappers():
    mapper_registry.map_imperatively(models.Client, clients)
    mapper_registry.map_imperatively(models.Quote, quotes)