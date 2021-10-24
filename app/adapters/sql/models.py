import enum

import sqlalchemy as sa

metadata = sa.MetaData()


class CurrencyEnum(enum.Enum):
    """Enum for currencies."""

    USD = "USD"


users = sa.Table(
    "users",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True, nullable=False),
    sa.Column("email", sa.String, nullable=False),
    sa.UniqueConstraint("email", name="unique_email"),
)

wallets = sa.Table(
    "wallets",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True, nullable=False),
    sa.Column(
        "user_id",
        sa.Integer,
        sa.ForeignKey("users.id", ondelete="cascade"),
        nullable=False,
        unique=True,
    ),
    sa.Column(
        "balance", sa.Numeric(10, 2, asdecimal=True), nullable=False, server_default="0"
    ),
    sa.Column(
        "currency", sa.String, server_default=CurrencyEnum.USD.value, nullable=False
    ),
    sa.CheckConstraint("amount >= 0", name="operations_positive_amount"),
)

wallet_operations = sa.Table(
    "wallet_operations",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True, nullable=False),
    sa.Column("operation", sa.String),
    sa.Column("wallet_from", sa.Integer, nullable=True),
    sa.Column("wallet_to", sa.Integer, nullable=True),
    sa.Column(
        "amount",
        sa.Numeric(10, 2, decimal_return_scale=2, asdecimal=True),
        nullable=False,
        server_default="0",
    ),
    sa.CheckConstraint("balance >= 0", name="wallet_positive_balance"),
)
