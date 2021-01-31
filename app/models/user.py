import sqlalchemy as sa
from sqlalchemy.sql import select

from databases.backends.postgres import Record

from app.db import db, metadata
from app.models.wallet import wallets, Wallet
from app.models.wallet_operations import WalletOperation

users = sa.Table(
    "users",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True, nullable=False),
    sa.Column('email', sa.String, nullable=False),
    sa.UniqueConstraint("email", name="unique_email"),
)

class User:

    @classmethod
    async def get(cls, user_id: int) -> Record:
        """ Return user record. """

        # async with db.transaction():
        j = users.join(wallets, users.c.id == wallets.c.user_id, isouter=True)
        query = select([
            users.c.id,
            users.c.email,
            wallets.c.id.label('wallet_id'),
            wallets.c.balance,
        ]).select_from(j).where(users.c.id == user_id)
        user = await db.fetch_one(query)
        # await WalletOperation.create(
        #     WalletOperation.RETRIEVE,
        #     user.get('balance'),
        #     user.get('wallet_id'),
        # )
        return user

    @classmethod
    async def get_by_wallet_id(cls, wallet_id: int) -> Record:
        """
        Return user record based on wallet id.

        :params user_id: ID of wallet
        :returns: SQL row record
        """

        j = users.join(wallets, users.c.id == wallets.c.user_id, isouter=True)
        query = select([
            users.c.id,
            users.c.email,
            wallets.c.id.label('wallet_id'),
            wallets.c.balance,
        ]).select_from(j).where(wallets.c.id == wallet_id)
        user = await db.fetch_one(query)
        return user



    @classmethod
    async def create(cls, email: str) -> Record:
        """ Creates new user. """

        assert email != ''

        async with db.transaction() as tr:
            user_query = users.insert().values({ 'email': email })
            user_id = await db.execute(user_query)
            await Wallet.create(user_id)
            user = await cls.get(user_id)

            # If user does not exists - rollback transaction
            if not user:
                await tr.rollback()
            return user