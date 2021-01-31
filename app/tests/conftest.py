import asyncio
import os
import warnings

import pytest
from databases import Database
from httpx import AsyncClient

import alembic

# pylint: disable=no-name-in-module
from alembic.config import Config
from app import app
from app.db import db


@pytest.fixture(scope="module")
def event_loop():
    """ Redefine event_loop for tests. """

    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module", autouse=True)
async def connect_to_db():
    """ Establish connection before tests and disconnect after test. """

    await db.connect()
    yield
    await db.disconnect()


@pytest.fixture(scope="module", autouse=True)
def apply_migrations_module():
    """ Apply migrations for separate modules """

    warnings.filterwarnings("ignore", category=DeprecationWarning)
    prev_app_env = os.environ["APP_ENV"]
    os.environ["APP_ENV"] = "test"

    path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    cfg = Config(os.path.join(path, "alembic/alembic.ini"))
    # pylint: disable=no-member
    alembic.command.upgrade(cfg, "head")
    yield
    # pylint: disable=no-member
    alembic.command.downgrade(cfg, "base")
    os.environ["APP_ENV"] = prev_app_env


@pytest.fixture(scope="function", autouse=True)
def apply_migrations_every_test():
    """ Apply migrations for each test. """

    warnings.filterwarnings("ignore", category=DeprecationWarning)
    prev_app_env = os.environ["APP_ENV"]
    os.environ["APP_ENV"] = "test"

    path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    cfg = Config(os.path.join(path, "alembic/alembic.ini"))
    # pylint: disable=no-member
    alembic.command.upgrade(cfg, "head")
    yield
    # pylint: disable=no-member
    alembic.command.downgrade(cfg, "base")
    os.environ["APP_ENV"] = prev_app_env


@pytest.fixture(scope="session")
def apply_migrations():
    """ Apply migrations for session scope. """

    warnings.filterwarnings("ignore", category=DeprecationWarning)
    prev_app_env = os.environ["APP_ENV"]
    os.environ["APP_ENV"] = "test"

    path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    cfg = Config(os.path.join(path, "alembic/alembic.ini"))
    # pylint: disable=no-member
    alembic.command.upgrade(cfg, "head")
    yield
    # pylint: disable=no-member
    alembic.command.downgrade(cfg, "base")
    os.environ["APP_ENV"] = prev_app_env


@pytest.fixture
def test_db() -> Database:
    """ Retrieve instance of test database. """

    return db


@pytest.fixture
async def client() -> AsyncClient:
    """ Cleint fixture for API tests. """

    async with AsyncClient(
        app=app,
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
    ) as client_data:
        yield client_data
