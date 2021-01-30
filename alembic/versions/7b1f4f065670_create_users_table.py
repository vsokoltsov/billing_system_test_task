"""create_users_table

Revision ID: 7b1f4f065670
Revises: 
Create Date: 2021-01-30 16:38:42.539268

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7b1f4f065670'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('email', sa.String, nullable=False),
        sa.UniqueConstraint("email", name="unique_email")
    )


def downgrade():
    op.drop_table("users")
