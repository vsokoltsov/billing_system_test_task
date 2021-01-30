import sqlalchemy as sa
from decimal import Decimal

from databases.backends.postgres import Record

from app.db import db, metadata

wallets = sa.Table(
    "wallets",
    metadata,
    sa.Column('id', sa.Integer, primary_key=True, nullable=False),
    sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete="cascade"), nullable=False, unique=True),
    sa.Column('balance', sa.Numeric(10, 2, asdecimal=True), nullable=False, server_default='0'),
)

class Wallet:

    @classmethod
    async def create(cls, user_id: int) -> Record:
        """ Creates new wallet instance. """

        wallet_query = wallets.insert().values({'user_id': user_id})
        return await db.execute(wallet_query)