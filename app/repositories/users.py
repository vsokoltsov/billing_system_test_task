from abc import ABC, abstractmethod
from typing import Optional

from databases import Database
from sqlalchemy.sql import select

from app.adapters.sql.models import users, wallets
from app.entities.user import User


class AbstractUserRepository(ABC):
    """Represents interface for communication with users"""

    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Receive User entity by its id
        :param user_id: ID of user
        :returns: User entity
        """
        ...

    @abstractmethod
    async def create(self, email: str) -> int:
        """
        Create user instance.

        :param email: New user email
        :returns: Base user schema entity
        """
        ...

    @abstractmethod
    async def get_by_wallet_id(self, wallet_id: int) -> Optional[User]:
        """
        Receive User entity by its wallet id

        :param wallet_id: ID of user's wallet
        :returns: User entity
        """
        ...


class UserRepository(AbstractUserRepository):
    """Implementation of user repository"""

    def __init__(self, db: Database):
        self._db = db

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Receive User entity by its id
        :param user_id: ID of user
        :returns: User entity
        """

        j = users.join(wallets, users.c.id == wallets.c.user_id, isouter=True)
        query = (
            select(
                [
                    users.c.id,
                    users.c.email,
                    wallets.c.id.label("wallet_id"),
                    wallets.c.balance,
                    wallets.c.currency,
                ]
            )
            .select_from(j)
            .where(users.c.id == user_id)
        )
        user = await self._db.fetch_one(query)
        if user:
            return User(**user)

        return None

    async def get_by_wallet_id(self, wallet_id: int) -> Optional[User]:
        """
        Receive User entity by its wallet id

        :param wallet_id: ID of user's wallet
        :returns: User entity
        """
        j = users.join(wallets, users.c.id == wallets.c.user_id, isouter=True)
        query = (
            select(
                [
                    users.c.id,
                    users.c.email,
                    wallets.c.id.label("wallet_id"),
                    wallets.c.balance,
                    wallets.c.currency,
                ]
            )
            .select_from(j)
            .where(wallets.c.id == wallet_id)
        )
        user = await self._db.fetch_one(query)
        if user:
            return User(**user)

        return None

    async def create(self, email: str) -> int:
        """
        Create user instance.

        :param email: New user email
        :returns: Base user schema entity
        """

        if not email:
            raise ValueError("email is empty")
        user_id = await self._db.execute(users.insert(), values={"email": email})
        return user_id
