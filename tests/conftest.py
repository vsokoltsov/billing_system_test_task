import asyncio
from typing import AsyncGenerator

import pytest
from databases import Database
from httpx import AsyncClient

from app.db import db

# pylint: disable=no-name-in-module
from app.main import app
from app.models.user import users
from app.models.wallet import wallets
from app.models.wallet_operations import wallet_operations


@pytest.fixture(autouse=True)
async def prepare_db():
    """Delete previous records from database"""

    await db.execute(query=users.delete())
    await db.execute(query=wallets.delete())
    await db.execute(query=wallet_operations.delete())
    yield


@pytest.fixture(scope="module")
def event_loop():
    """Redefine event_loop for tests."""

    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module", autouse=True)
async def connect_to_db():
    """Establish connection before tests and disconnect after test."""

    await db.connect()
    yield
    await db.disconnect()


@pytest.fixture
def test_db() -> Database:
    """Retrieve instance of test database."""

    return db


@pytest.fixture
async def client() -> AsyncGenerator:
    """Cleint fixture for API tests."""
    async with AsyncClient(
        app=app,
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
    ) as client_data:
        yield client_data
