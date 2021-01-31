from decimal import Decimal

import sqlalchemy as sa

from app.db import db, metadata

wallet_operations = sa.Table(
    "wallet_operations",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True, nullable=False),
    sa.Column("operation", sa.String),
    sa.Column("wallet_from", sa.Integer, nullable=True, unique=True),
    sa.Column("wallet_to", sa.Integer, nullable=True, unique=True),
    sa.Column(
        "amount",
        sa.Numeric(10, 2, decimal_return_scale=2, asdecimal=True),
        nullable=False,
        server_default="0",
    ),
)


class WalletOperation:
    """ Represents logging information about wallet operations. """

    RETRIEVE = "retrieve"
    CREATE = "create"
    RECEIPT = "receipt"
    DEBIT = "debit"

    @classmethod
    async def create(
        cls,
        operation: str,
        amount: Decimal = 0,
        wallet_from: int = None,
        wallet_to: int = None,
    ) -> int:
        """
        Creates new wallet operation instance.

        :param operation: Name of operation
        :param amount: Funds value
        :param wallet_from: ID of source wallet
        :param wallet_to: ID of target wallet
        :returns: ID of new SQL row
        """

        operations_query = wallet_operations.insert(None).values(
            {
                "operation": operation,
                "wallet_from": wallet_from,
                "wallet_to": wallet_to,
                "amount": amount,
            }
        )
        return await db.execute(operations_query)
