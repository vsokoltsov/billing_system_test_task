import os
import pytest
import warnings
import asyncio

import alembic
from alembic.config import Config
from asgi_lifespan import LifespanManager
from httpx import AsyncClient
from databases import Database

from fastapi import FastAPI
from app import app
from app.db import db


# @pytest.fixture(scope='session')
# def event_loop():
#     loop = asyncio.get_event_loop()
#     yield loop
#     loop.close()

@pytest.fixture(autouse=True)
async def connect_to_db():
    await db.connect()
    yield
    await db.disconnect()

@pytest.fixture(scope="session", autouse=True)
def tests_setup_and_teardown():
    old_environ = dict(os.environ)
    os.environ['APP_ENV'] = 'test'
    yield
    os.environ.clear()
    os.environ.update(old_environ)


@pytest.fixture(scope="session")
def apply_migrations():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    prev_app_env = os.environ['APP_ENV']
    os.environ['APP_ENV'] = 'test'

    path = os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    )
    config = Config(os.path.join(path, "alembic/alembic.ini"))
    alembic.command.upgrade(config, "head")
    yield
    alembic.command.downgrade(config, "base")
    os.environ['APP_ENV'] = prev_app_env

# @pytest.fixture
# def application(apply_migrations: None) -> FastAPI:
#     return  app

@pytest.fixture
def test_db() -> Database:
    return db


@pytest.fixture
async def client(apply_migrations: None) -> AsyncClient:
    async with AsyncClient(
        app=app,
        base_url="http://testserver",
        headers={"Content-Type": "application/json"}
    ) as client:
        yield client