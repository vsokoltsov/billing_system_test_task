import sqlalchemy as sa
from sqlalchemy.sql import select

from databases.backends.postgres import Record

from app.db import db, metadata
from app.models.wallet import wallets, Wallet

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

        j = users.join(wallets, users.c.id == wallets.c.user_id, isouter=True)
        query = select([
            users.c.id,
            users.c.email,
            wallets.c.id.label('wallet_id'),
            wallets.c.balance,
        ]).select_from(j)
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