from abc import ABC, abstractmethod
from decimal import Decimal
from databases import Database
from app.entities.user import User
from app.repositories.users import AbstractUserRepository
from app.repositories.wallet import AbstractWalletRepository
from app.repositories.wallet_operations import AbstractWalletOperationRepository
from app.entities.wallet_operation import Operations


class AbstractUserUsecase(ABC):
    """Represents interface for user usecases"""

    @abstractmethod
    async def create(self, email: str) -> User:
        """
        Creates new user (and wallet).

        :param email: User's email
        :returns: User entity
        """
        ...


class UserUsecase(AbstractUserUsecase):
    """Implementation of user usecases."""

    def __init__(
        self,
        *,
        db: Database,
        user_repo: AbstractUserRepository,
        wallet_repo: AbstractWalletRepository,
        wallet_operation_repo: AbstractWalletOperationRepository
    ):
        self._db = db
        self.user_repo = user_repo
        self.wallet_repo = wallet_repo
        self.wallet_operation_repo = wallet_operation_repo

    async def create(self, email: str) -> User:
        """
        Creates new user (and wallet).

        :param email: User's email
        :returns: User entity
        """

        async with self._db.connection() as connection:
            async with connection.transaction():
                # Creates new user
                user_id = await self.user_repo.create(email=email)
                # Creates wallet for user
                wallet_id = await self.wallet_repo.create(user_id=user_id)
                # Creates wallet operation instance for 'Create' operation
                await self.wallet_operation_repo.create(
                    operation=Operations.create,
                    wallet_from=None,
                    wallet_to=wallet_id,
                    amount=Decimal('0')
                )
                user = await self.user_repo.get_by_id(user_id=user_id)
                return user
