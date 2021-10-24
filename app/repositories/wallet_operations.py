from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional

from app.adapters.sql.models import wallet_operations
from app.entities.wallet_operation import Operations

from .base import BaseRepository


class AbstractWalletOperationRepository(ABC):
    """Abstract class for WalletOperations repository"""

    @abstractmethod
    async def create(
        self,
        *,
        operation: Operations,
        amount: Decimal,
        wallet_from: int = None,
        wallet_to: int = None,
    ) -> Optional[int]:
        """
        Creates new wallet operation instance.

        :param operation: Name of operation
        :param amount: Funds value
        :param wallet_from: ID of source wallet
        :param wallet_to: ID of target wallet
        :returns: ID of new SQL row
        """
        ...


class WalletOperationRepository(BaseRepository, AbstractWalletOperationRepository):
    """Implementation of AbstractWalletOperationRepository interface."""

    async def create(
        self,
        *,
        operation: Operations,
        amount: Decimal,
        wallet_from: int = None,
        wallet_to: int = None,
    ) -> int:
        """
        Creates new wallet operation instance.

        :param operation: Name of operation
        :param amount: Funds value
        :param wallet_from: ID of source wallet
        :param wallet_to: ID of target wallet
        :returns: ID of new SQL row
        """

        operations_query = (
            wallet_operations.insert()
            .values(
                {
                    "operation": operation.value,
                    "wallet_from": wallet_from,
                    "wallet_to": wallet_to,
                    "amount": amount,
                }
            )
            .returning(wallet_operations.c.id)
        )
        wallet_operation_id: int = await self._db.execute(operations_query)
        return wallet_operation_id
