"""create_wallets

Revision ID: 8697d766eeb4
Revises: 7b1f4f065670
Create Date: 2021-01-31 00:27:48.971118

"""
from alembic import op
import sqlalchemy as sa
from decimal import Decimal


# revision identifiers, used by Alembic.
revision = '8697d766eeb4'
down_revision = '7b1f4f065670'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "wallets",
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete="cascade"), nullable=False, unique=True),
        sa.Column('balance', sa.Numeric(10, 2, decimal_return_scale=2, asdecimal=True), nullable=False, server_default='0')
    )
    # op.add_column('users', sa.Column('wallet_id', sa.Integer, nullable=False)),


def downgrade():
    op.drop_table("wallets")
    # op.drop_column("users", "wallet_id")
