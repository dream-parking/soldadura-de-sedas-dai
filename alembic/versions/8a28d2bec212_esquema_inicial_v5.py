"""esquema inicial v5

Revision ID: 8a28d2bec212
Revises:
Create Date: 2026-07-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8a28d2bec212'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('clients',
    sa.Column('client_id', sa.String(length=50), nullable=False),
    sa.Column('client_company_name', sa.String(length=200), nullable=False),
    sa.Column('client_phone', sa.String(length=30), nullable=False),
    sa.Column('registration_date', sa.Date(), nullable=False),
    sa.Column('client_email', sa.String(length=150), nullable=True),
    sa.PrimaryKeyConstraint('client_id')
    )
    op.create_table('workers',
    sa.Column('worker_id', sa.String(length=5), nullable=False),
    sa.Column('worker_name', sa.String(length=200), nullable=False),
    sa.Column('worker_role', sa.String(length=100), nullable=False),
    sa.Column('worker_base_rate', sa.Float(), nullable=False),
    sa.PrimaryKeyConstraint('worker_id')
    )
    op.create_table('materials',
    sa.Column('id', sa.String(length=5), nullable=False),
    sa.Column('description', sa.String(length=300), nullable=False),
    sa.Column('specifications', sa.String(length=300), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('quotes',
    sa.Column('quote_id', sa.String(length=50), nullable=False),
    sa.Column('client_id', sa.String(length=50), nullable=False),
    sa.Column('quote_issue_date', sa.Date(), nullable=False),
    sa.Column('quote_job_description', sa.String(length=500), nullable=False),
    sa.Column('quote_estimated_amount', sa.Float(), nullable=False),
    sa.Column('quote_status', sa.String(length=30), nullable=False),
    sa.Column('notes', sa.String(length=500), nullable=True),
    sa.ForeignKeyConstraint(['client_id'], ['clients.client_id'], ),
    sa.PrimaryKeyConstraint('quote_id')
    )
    op.create_table('projects',
    sa.Column('project_id', sa.String(length=5), nullable=False),
    sa.Column('client_id', sa.String(length=50), nullable=False),
    sa.Column('quote_id', sa.String(length=50), nullable=False),
    sa.Column('project_name', sa.String(length=200), nullable=False),
    sa.Column('project_location', sa.String(length=200), nullable=False),
    sa.Column('project_start_date', sa.Date(), nullable=False),
    sa.Column('project_total_cost', sa.Float(), nullable=False),
    sa.Column('project_status', sa.String(length=30), nullable=False),
    sa.Column('project_estimated_end_date', sa.Date(), nullable=True),
    sa.ForeignKeyConstraint(['client_id'], ['clients.client_id'], ),
    sa.ForeignKeyConstraint(['quote_id'], ['quotes.quote_id'], ),
    sa.PrimaryKeyConstraint('project_id')
    )
    op.create_table('worker_assignments',
    sa.Column('assignment_id', sa.String(length=5), nullable=False),
    sa.Column('worker_id', sa.String(length=5), nullable=False),
    sa.Column('project_id', sa.String(length=5), nullable=False),
    sa.Column('assignment_date', sa.Date(), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['projects.project_id'], ),
    sa.ForeignKeyConstraint(['worker_id'], ['workers.worker_id'], ),
    sa.PrimaryKeyConstraint('assignment_id')
    )
    op.create_table('payrolls',
    sa.Column('payroll_id', sa.String(length=5), nullable=False),
    sa.Column('worker_id', sa.String(length=5), nullable=False),
    sa.Column('project_id', sa.String(length=5), nullable=False),
    sa.Column('payroll_fortnight_period', sa.String(length=30), nullable=False),
    sa.Column('payroll_payment_date', sa.Date(), nullable=False),
    sa.Column('payroll_hours_worked', sa.Float(), nullable=True),
    sa.Column('payroll_paid_amount', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['projects.project_id'], ),
    sa.ForeignKeyConstraint(['worker_id'], ['workers.worker_id'], ),
    sa.PrimaryKeyConstraint('payroll_id')
    )
    op.create_table('detalle_materiales_obra',
    sa.Column('project_id', sa.String(length=5), nullable=False),
    sa.Column('material_id', sa.String(length=5), nullable=False),
    sa.Column('used_quantity', sa.Float(), nullable=False),
    sa.Column('measurement_unit', sa.String(length=10), nullable=False),
    sa.ForeignKeyConstraint(['material_id'], ['materials.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['projects.project_id'], ),
    sa.PrimaryKeyConstraint('project_id', 'material_id')
    )
    op.create_table('technical_measurements',
    sa.Column('id', sa.String(length=5), nullable=False),
    sa.Column('project_id', sa.String(length=5), nullable=False),
    sa.Column('dimensions', sa.Integer(), nullable=False),
    sa.Column('structure_type', sa.String(length=100), nullable=False),
    sa.Column('payment', sa.Float(), nullable=False),
    sa.Column('unit', sa.String(length=10), nullable=False),
    sa.Column('notes', sa.String(length=300), nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['projects.project_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('biweekly_requests',
    sa.Column('id', sa.String(length=5), nullable=False),
    sa.Column('project_id', sa.String(length=5), nullable=False),
    sa.Column('date', sa.String(length=20), nullable=False),
    sa.Column('status', sa.String(length=30), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('notes', sa.String(length=300), nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['projects.project_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('account_statements',
    sa.Column('id', sa.String(length=5), nullable=False),
    sa.Column('project_id', sa.String(length=5), nullable=False),
    sa.Column('date', sa.String(length=20), nullable=False),
    sa.Column('initial_budget', sa.Float(), nullable=False),
    sa.Column('amount_paid', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['projects.project_id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('account_statements')
    op.drop_table('biweekly_requests')
    op.drop_table('technical_measurements')
    op.drop_table('detalle_materiales_obra')
    op.drop_table('payrolls')
    op.drop_table('worker_assignments')
    op.drop_table('projects')
    op.drop_table('quotes')
    op.drop_table('materials')
    op.drop_table('workers')
    op.drop_table('clients')
