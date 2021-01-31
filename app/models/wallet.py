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
        """
        Creates new wallet instance.

        :params user_id: ID of user
        :returns: SQL row record
        """

        wallet_query = wallets.insert().values({'user_id': user_id})
        return await db.execute(wallet_query)

    @classmethod
    async def enroll(cls, wallet_id: int, amount: Decimal) -> Record:
        """
        Put amount of money to the wallet.

        :param wallet_id: ID of walled
        :param amount: Number that need to be applied for wallet's balance.
        :returns: SQL row record
        """

        assert amount != 0

        async with db.transaction():
            query = (
                wallets
                .update()
                .where(wallets.c.id == wallet_id)
                .values({ 'balance': wallets.c.balance + amount })
                .returning(wallets.c.balance)
            )
            balance = await db.execute(query)
            return balance

    @classmethod
    async def get_by_user_id(cls, user_id: int) -> Record:
        """
        Retrieve wallet row record by user_id value.

        :param user_id: ID of user:
        :returns: SQL row record
        """

        wallet_query = wallets.select().where(wallets.c.user_id == user_id)
        return await db.fetch_one(wallet_query)
            