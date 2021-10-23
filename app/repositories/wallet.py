from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional
from databases import Database
from app.adapters.sql.models import wallets
from app.entities.wallet import WalletEntity
from .base import BaseRepository

class AbstractWalletRepository(ABC):
    """Represents interface for wallet repository"""

    @abstractmethod
    async def get_by_id(self, wallet_id: int) -> Optional[WalletEntity]:
        """
        Retrieve wallet record by wallet id.

        :param wallet_id: ID of use
        :returns: Wallet schema
        """
        ...

    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> Optional[WalletEntity]:
        """
        Retrieve wallet record by user id.

        :param user_id: ID of use
        :returns: Wallet schema
        """
        ...

    @abstractmethod
    async def create(self, user_id: int) -> int:
        """
        Create new wallet with user ID

        :param user_id: ID of user
        :returns: ID of new wallet
        """
        ...

    @abstractmethod
    async def enroll(self, wallet_id: int, amount: Decimal) -> int:
        """
        Put given funds on wallet

        :param wallet_id: ID of wallet
        :param amount: Initial funds
        :returns: ID of updated wallet
        """
        ...

    @abstractmethod
    async def transfer(self, source_wallet_id: int, destination_wallet_id: int, amount: Decimal) -> int:
        """
        Transfer amount of currency between wallets.

        :param source_wallet_id: ID of source wallet
        :param destination_wallet_id: ID of wallet recepients
        :param amount: Amount of currency
        :returns: Source wallet id
        """
        ...


class WalletRepository(BaseRepository, AbstractWalletRepository):
    """Implementation of wallet repository."""

    async def get_by_id(self, wallet_id: int) -> WalletEntity:
        """
        Retrieve wallet record by wallet id.

        :param wallet_id: ID of use
        :returns: Wallet schema
        """
        wallet_query = wallets.select().where(wallets.c.id == wallet_id)
        wallet = await self._db.fetch_one(wallet_query)
        if wallet:
            return WalletEntity(**wallet)

    async def get_by_user_id(self, user_id: int) -> Optional[WalletEntity]:
        """
        Retrieve wallet record by user id.

        :param user_id: ID of use
        :returns: Wallet schema
        """
        wallet_query = wallets.select().where(wallets.c.user_id == user_id)
        wallet = await self._db.fetch_one(wallet_query)
        if wallet:
            return WalletEntity(**wallet)

    async def create(self, user_id: int) -> int:
        """
        Create new wallet with user ID

        :param user_id: ID of user
        :returns: ID of new wallet
        """

        wallet_query = wallets.insert().values({"user_id": user_id})
        return await self._db.execute(wallet_query)

    async def enroll(self, wallet_id: int, amount: Decimal) -> int:
        """
        Put given funds on wallet

        :param wallet_id: ID of wallet
        :param amount: Initial funds
        :returns: ID of updated wallet
        """

        query = (
            wallets.update()
            .where(wallets.c.id == wallet_id)
            .values({"balance": wallets.c.balance + amount})
            .returning(wallets.c.id)
        )
        return await self._db.execute(query)

    async def transfer(self, source_wallet_id: int, destination_wallet_id: int, amount: Decimal) -> int:
        """
        Transfer amount of currency between wallets.

        :param source_wallet_id: ID of source wallet
        :param destination_wallet_id: ID of wallet recepients
        :param amount: Amount of currency
        :returns: Source wallet id
        """

        source_query = (
            wallets.update()
            .where(wallets.c.id == source_wallet_id)
            .values({"balance": wallets.c.balance - amount})
            .returning(wallets.c.id)
        )
        target_query = (
            wallets.update()
            .where(wallets.c.id == destination_wallet_id)
            .values({"balance": wallets.c.balance + amount})
        )
        wallet_id = await self._db.execute(source_query)
        if not wallet_id:
            raise ValueError("Source wallet id does not exist")
        await self._db.execute(target_query)
        return wallet_id
