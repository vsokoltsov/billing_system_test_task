from abc import ABC, abstractmethod
from decimal import Decimal

from databases import Database

from app.entities.user import User, UserDoesNotExist
from app.entities.wallet_operation import Operations
from app.repositories.users import AbstractUserRepository
from app.repositories.wallet import AbstractWalletRepository
from app.repositories.wallet_operations import AbstractWalletOperationRepository


class AbstractWalletUsecase(ABC):
    """Interface for wallet usecases"""

    @abstractmethod
    async def enroll(self, user_id: int, amount: Decimal) -> User:
        """
        Enroll user's wallet.

        :param user_id: ID of user
        :param amount: Funds for enrollment
        :returns: User entity
        """
        ...


class WalletUsecase(AbstractWalletUsecase):
    """Implementation of wallet usecase."""

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

    async def enroll(self, user_id: int, amount: Decimal) -> User:
        """
        Enroll user's wallet.

        :param user_id: ID of user
        :param amount: Funds for enrollment
        :returns: User entity
        """

        async with self._db.connection() as connection:
            async with connection.transaction():
                # Find user
                user = await self.user_repo.get_by_id(user_id=user_id)
                if not user:
                    raise UserDoesNotExist("User does not exists")

                # Enroll user's wallet
                wallet_id = await self.wallet_repo.enroll(
                    wallet_id=user.wallet_id, amount=amount
                )

                # Create wallet operation for 'debit'
                await self.wallet_operation_repo.create(
                    operation=Operations.deposit,
                    wallet_from=None,
                    wallet_to=wallet_id,
                    amount=amount,
                )

                # Find user
                user = await self.user_repo.get_by_id(user_id=user_id)
                if not user:
                    raise UserDoesNotExist("User does not exists")
                return user
