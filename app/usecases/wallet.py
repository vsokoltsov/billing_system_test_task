from abc import ABC, abstractmethod
from decimal import Decimal

from app.adapters.sql.tx import AbstractTransactionManager, IsolationLevels, LockID
from app.entities.user import User, UserDoesNotExist
from app.entities.wallet import WalletDoesNotExist
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

    @abstractmethod
    async def transfer(
        self, source_wallet_id: int, destination_wallet_id: int, amount: Decimal
    ) -> User:
        """
        Transferfunds between wallets

        :param source_wallet_id: ID of source wallet
        :param destination_wallet_id: ID of destination wallet
        :returns: User entity
        """
        ...


class WalletUsecase(AbstractWalletUsecase):
    """Implementation of wallet usecase."""

    def __init__(
        self,
        *,
        tx_manager: AbstractTransactionManager,
        user_repo: AbstractUserRepository,
        wallet_repo: AbstractWalletRepository,
        wallet_operation_repo: AbstractWalletOperationRepository,
    ):
        self.tx_manager = tx_manager
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

        async with self.tx_manager.advisory_lock(
            lock_id=LockID.WALLET_ENROLL,
            isolation_level=IsolationLevels.SERIALIZABLE,
        ):
            # Find user
            user = await self.user_repo.get_by_id(user_id=user_id)
            if not user:
                raise UserDoesNotExist("User does not exists")

            # Enroll user's wallet
            wallet_id = await self.wallet_repo.enroll(wallet_id=user.wallet_id, amount=amount)

            # Create wallet operation for 'debit'
            await self.wallet_operation_repo.create(
                operation=Operations.DEPOSIT,
                wallet_from=None,
                wallet_to=wallet_id,
                amount=amount,
            )

            # Find user
            user = await self.user_repo.get_by_id(user_id=user_id)
            if not user:
                raise UserDoesNotExist("User does not exists")
            return user

    async def transfer(
        self, source_wallet_id: int, destination_wallet_id: int, amount: Decimal
    ) -> User:
        """
        Transferfunds between wallets

        :param source_wallet_id: ID of source wallet
        :param destination_wallet_id: ID of destination wallet
        :returns: User entity
        """

        async with self.tx_manager.advisory_lock(
            lock_id=LockID.WALLET_TRANSFER,
            isolation_level=IsolationLevels.SERIALIZABLE,
        ):
            if amount <= 0:
                raise ValueError("Insufficient amount")

            source_wallet = await self.wallet_repo.get_by_id(wallet_id=source_wallet_id)
            if not source_wallet:
                raise WalletDoesNotExist("Source wallet does not exists")

            destination_wallet = await self.wallet_repo.get_by_id(wallet_id=destination_wallet_id)
            if not destination_wallet:
                raise WalletDoesNotExist("Source wallet does not exists")

            source_wallet_id = await self.wallet_repo.transfer(
                source_wallet_id=source_wallet_id,
                destination_wallet_id=destination_wallet_id,
                amount=amount,
            )

            await self.wallet_operation_repo.create(
                operation=Operations.WITHDRAWAL,
                wallet_from=source_wallet_id,
                wallet_to=destination_wallet_id,
                amount=amount,
            )
            await self.wallet_operation_repo.create(
                operation=Operations.DEPOSIT,
                wallet_from=destination_wallet_id,
                wallet_to=source_wallet_id,
                amount=amount,
            )

            user = await self.user_repo.get_by_wallet_id(wallet_id=source_wallet_id)
            if not user:
                raise UserDoesNotExist("User does not exist")

            return user
