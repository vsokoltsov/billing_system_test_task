from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from enum import Enum
from logging import getLogger
from typing import AsyncGenerator

import sqlalchemy as sa
from databases import Database

logger = getLogger(__name__)


class IsolationLevels(Enum):
    """Represents isolation levels for the database transaction."""

    REPEATABLE_READ = "repeatable_read"
    SERIALIZABLE = "serializable"


class LockID(Enum):
    """Enumeration of possible locks ids."""

    CREATE_USER = 1
    GET_BY_WALLET_ID = 2
    CREATE_WALLET = 3
    WALLET_ENROLL = 4
    WALLET_TRANSFER = 5


class AbstractTransactionManager(ABC):
    """Interface for transaction manager."""

    @abstractmethod
    @asynccontextmanager
    async def advisory_lock(
        self,
        isolation_level: IsolationLevels,
        lock_id: LockID,
    ) -> AsyncGenerator:
        """
        Perform postgres advisory locking by some ID.

        :param database:: Instance of Database class
        :param isolation_level: One of the isolation_levels
        :param lock_id: ID of lock
        :param record_id: ID of record
        """
        yield


class SQLTransactionManager(AbstractTransactionManager):
    """Implementation of TransactionManager interface"""

    def __init__(self, db: Database):
        self._db = db

    @asynccontextmanager
    async def advisory_lock(
        self,
        isolation_level: IsolationLevels,
        lock_id: LockID,
    ) -> AsyncGenerator:
        """
        Perform postgres advisory locking by some ID.

        :param database:: Instance of Database class
        :param isolation_level: One of the isolation_levels
        :param lock_id: ID of lock
        :param record_id: ID of record
        """

        lock_fn = sa.func.pg_try_advisory_lock
        unlock_fn = sa.func.pg_advisory_unlock

        async with self._db.connection() as connection:
            is_obtained = await connection.execute(query=sa.select([lock_fn(lock_id.value, 1)]))
            if is_obtained:
                async with connection.transaction(
                    isolation=isolation_level.value,
                ) as trx:
                    yield trx

            is_released = await connection.execute(query=sa.select([unlock_fn(lock_id.value, 1)]))
            if not is_released:
                logger.warning("Postgres advisory lock %s was not released", lock_id.value)
