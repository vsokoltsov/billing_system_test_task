from decimal import Decimal

import factory
import sqlalchemy as sa
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import scoped_session, sessionmaker

from app import settings
from app.adapters.sql.models import users, wallets
from app.entities.currency import CurrencyEnum

ENGINE = create_engine(settings.BILLING_DB_DSN)
SESSION = scoped_session(
    sessionmaker(
        bind=ENGINE,
        autocommit=True,
        autoflush=True,
    ),
)


@as_declarative()
class Base:
    """Base ORM class"""


class User(Base):
    """ORM based class for user factory"""

    __table__ = users


class Wallet(Base):
    """ORM based class for wallet factory"""

    __table__ = wallets

    user = sa.orm.relationship("User")


fake_data = Faker()


class UserFactory(SQLAlchemyModelFactory):
    """Factory for users table"""

    class Meta:
        """Meta for users factory"""

        model = User
        sqlalchemy_session = SESSION
        sqlalchemy_session_persistence = "flush"
        sqlalchemy_get_or_create = ("id",)

    id = factory.Sequence(lambda n: n + 1)
    email = factory.LazyAttribute(lambda _: fake_data.email())


class WalletFactory(SQLAlchemyModelFactory):
    """Factory for wallets table"""

    class Meta:
        """Meta for wallets factory"""

        model = Wallet
        sqlalchemy_session = SESSION
        sqlalchemy_session_persistence = "flush"
        sqlalchemy_get_or_create = ("id",)

    id = factory.Sequence(lambda n: n + 1)
    user = factory.SubFactory(UserFactory)
    balance = Decimal("100.00")
    currency = CurrencyEnum.USD.value
