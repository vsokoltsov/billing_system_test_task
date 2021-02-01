"""create_wallets

Revision ID: 8697d766eeb4
Revises: 7b1f4f065670
Create Date: 2021-01-31 00:27:48.971118

"""
from alembic import op
import sqlalchemy as sa
from decimal import Decimal
from sqlalchemy.dialects import postgresql

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
        sa.Column('balance', sa.Numeric(10, 2, decimal_return_scale=2, asdecimal=True), nullable=False, server_default='0'),
        sa.Column('currency', postgresql.ENUM('USD', name='currency_enum'), server_default='USD', nullable=False),
    )


def downgrade():
    op.drop_table("wallets")
    enum_type = postgresql.ENUM('USD', name='currency_enum')
    enum_type.drop(op.get_bind(), checkfirst=False)
