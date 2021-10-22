import os
from contextlib import asynccontextmanager
from enum import Enum

import sqlalchemy
from databases import Database
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app_env = os.environ.get("APP_ENV")
if app_env == "test":
    load_dotenv(os.path.join(BASE_DIR, ".env.test"), verbose=True)
else:
    load_dotenv(os.path.join(BASE_DIR, ".env"))


DATABASE_URL = (
    "postgresql://"
    f'{os.environ.get("POSTGRES_USER")}:{os.environ.get("POSTGRES_PASSWORD")}'
    f'@{os.environ.get("DB_HOST")}:{os.environ.get("DB_PORT")}'
    f'/{os.environ.get("POSTGRES_DB")}'
)
db = Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()


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


@asynccontextmanager
async def advisory_lock(
    database: Database,
    isolation_level: IsolationLevels,
    # lock_id: LockID,
    # record_id: int = None,
):
    """
    Perform postgres advisory locking by some ID.

    :param database:: Instance of Database class
    :param isolation_level: One of the isolation_levels
    :param lock_id: ID of lock
    :param record_id: ID of record
    """

    # if record_id:
    #     lock_query = "select pg_advisory_lock(:lock_id,:record_id)"
    #     unlock_query = "select pg_advisory_unlock(:lock_id, :record_id)"
    #     values = {"lock_id": lock_id.value, "record_id": record_id}
    # else:
    #     lock_query = "select pg_advisory_lock(:lock_id)"
    #     unlock_query = "select pg_advisory_unlock(:lock_id)"
    #     values = {"lock_id": lock_id.value}

    # try:
    # await database.execute(query=lock_query, values=values)
    async with database.transaction(isolation=isolation_level.value) as transaction:
        yield transaction
    # finally:
    # await database.execute(query=unlock_query, values=values)
