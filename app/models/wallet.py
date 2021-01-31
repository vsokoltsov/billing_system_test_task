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

class InsufficientFundsException(Exception):
    pass

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
    async def enroll(cls, wallet_id: int, amount: Decimal) -> Decimal:
        """
        Put amount of money to the wallet.

        :param wallet_id: ID of walled
        :param amount: Number that need to be applied for wallet's balance.
        :returns: Balance decimal value
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

    @classmethod
    async def transfer(cls, wallet_from: int, wallet_to: int, amount: Decimal) -> Decimal:
        """
        Transfer amount of currency between wallets.

        :param wallet_from: ID of source wallet
        :param wallet_to: ID of wallet recepients
        :param amount: Amount of currency
        :returns: Balance decimal value
        """

        assert amount > 0

        async with db.transaction():
            # Get source wallet data
            get_source_query = wallets.select().where(wallets.c.id == wallet_from)
            source_wallet = await db.fetch_one(get_source_query)
            if source_wallet.get('balance') < amount:
                raise InsufficientFundsException("Source wallet does not have enough funds.")

            # Update wallets information for both source and target
            source_query = (
                wallets
                .update()
                .where(wallets.c.id == wallet_from)
                .values({ 'balance': wallets.c.balance - amount })
                .returning(wallets.c.balance)
            )
            target_query = (
                wallets
                .update()
                .where(wallets.c.id == wallet_to)
                .values({ 'balance': wallets.c.balance + amount })
            )
            balance = await db.execute(source_query)
            await db.execute(target_query)
            return balance
            