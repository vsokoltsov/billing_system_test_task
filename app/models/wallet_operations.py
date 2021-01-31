import sqlalchemy as sa
from decimal import Decimal

from app.db import db, metadata

wallet_operations = sa.Table(
    "wallet_operations",
    metadata,
    sa.Column('id', sa.Integer, primary_key=True, nullable=False),
    sa.Column('operation', sa.String),
    sa.Column('wallet_from', sa.Integer, nullable=True, unique=True),
    sa.Column('wallet_to', sa.Integer, nullable=True, unique=True),
    sa.Column('amount', sa.Numeric(10, 2, decimal_return_scale=2, asdecimal=True), nullable=False, server_default='0'),
)

class WalletOperation:
    RETRIEVE = 'retrieve'
    CREATE = 'create'
    RECEIPT = 'receipt'
    DEBIT = 'debit'


    @classmethod
    async def create(cls, operation: str, amount: Decimal = 0, wallet_from: int = None, wallet_to: int = None,):
        operations_query = wallet_operations.insert().values({
            'operation': operation,
            'wallet_from': wallet_from,
            'wallet_to': wallet_to,
            'amount': amount,
        })
        return await db.execute(operations_query)