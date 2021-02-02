"""create wallet operations

Revision ID: 1af7d2c06855
Revises: 8697d766eeb4
Create Date: 2021-01-31 20:29:13.453079

"""
from alembic import op
import sqlalchemy as sa

from sqlalchemy import CheckConstraint

from sqlalchemy.dialects.postgresql import NUMERIC


# revision identifiers, used by Alembic.
revision = '1af7d2c06855'
down_revision = '8697d766eeb4'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "wallet_operations",
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('operation', sa.String),
        sa.Column('wallet_from', sa.Integer, nullable=True),
        sa.Column('wallet_to', sa.Integer, nullable=True),
        sa.Column('amount', NUMERIC(10, 2), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.current_timestamp()),
        CheckConstraint('amount >= 0', name='operations_positive_amount'),
    )


def downgrade():
    op.drop_table("wallet_operations")
