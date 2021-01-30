import sqlalchemy as sa

from databases.backends.postgres import Record

from app.db import db, metadata

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

        query = users.select().where(users.c.id == user_id)
        user = await db.fetch_one(query)
        return user

    @classmethod
    async def create(cls, email: str) -> Record:
        """ Creates new user. """

        assert email != ''

        async with db.transaction():
            query = users.insert().values({ 'email': email })
            user_id = await db.execute(query)
            user = await cls.get(user_id)
            return user