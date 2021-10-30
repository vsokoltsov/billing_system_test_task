from databases import Database

from app import settings

_db = Database(settings.BILLING_DB_DSN)  # type: ignore


async def connect_db():
    """Function for estabslishing database connection."""
    if not _db.is_connected:
        await _db.connect()


async def disconnect_db():
    """Function for closing databse connection."""
    if _db.is_connected:
        await _db.connect()


def get_db() -> Database:
    """Return database instance."""

    return _db
