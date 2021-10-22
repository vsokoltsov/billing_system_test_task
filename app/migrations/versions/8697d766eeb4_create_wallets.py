"""create_wallets

Revision ID: 8697d766eeb4
Revises: 7b1f4f065670
Create Date: 2021-01-31 00:27:48.971118

"""
from decimal import Decimal

import sqlalchemy as sa
from alembic import op
from sqlalchemy import CheckConstraint
from sqlalchemy.dialects.postgresql import NUMERIC

from app.models.wallet import CurrencyEnum

# revision identifiers, used by Alembic.
revision = "8697d766eeb4"
down_revision = "7b1f4f065670"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "wallets",
        sa.Column("id", sa.Integer, primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="cascade"),
            nullable=False,
            unique=True,
        ),
        sa.Column("balance", NUMERIC(10, 2), nullable=False, server_default="0"),
        sa.Column(
            "currency", sa.String, server_default=CurrencyEnum.USD.value, nullable=False
        ),
        CheckConstraint("balance >= 0", name="wallet_positive_balance"),
    )


def downgrade():
    op.drop_table("wallets")
