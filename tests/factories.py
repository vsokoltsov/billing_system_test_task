import inspect
from decimal import Decimal

import factory
from pydantic import BaseModel

from app.adapters.sql.db import get_db
from app.adapters.sql.models import users, wallets
from app.entities.currency import CurrencyEnum
from app.entities.user import BaseUser
from app.entities.wallet import WalletEntity


class SQLAlchemyCoreFactory(factory.Factory):
    """Implementation of factory for SQLAlchemy core"""

    class Meta:
        """Metaclass for SQLAlchemy core"""

        abstract = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """creates new instance of table"""

        async def create_coro(**kwargs):
            """Create instance for async/await"""

            _db = get_db()
            schema = kwargs.pop("schema", None)
            for key, value in kwargs.items():
                if inspect.iscoroutine(value):
                    kwargs[key] = await kwargs[key]
                if issubclass(kwargs[key].__class__, BaseModel):
                    kwargs[key] = kwargs[key].id

            object_id = await _db.execute(
                query=model_class.insert().returning(model_class.c.id), values=kwargs
            )
            if schema:
                obj_raw = await _db.fetch_one(
                    model_class.select().where(model_class.c.id == object_id)
                )
                return schema(**obj_raw)
            return object_id

        return create_coro(*args, **kwargs)


class UserFactory(SQLAlchemyCoreFactory):
    """Factory for users table"""

    schema = BaseUser

    class Meta:
        """Meta for users factory"""

        model = users

    id = factory.Sequence(lambda i: i + 1)
    email = factory.LazyAttribute(lambda o: f"{o.id}@example.com")


class WalletFactory(SQLAlchemyCoreFactory):
    """Factory for wallets table"""

    schema = WalletEntity

    class Meta:
        """Meta for wallets factory"""

        model = wallets

    id = factory.Sequence(lambda n: n + 1)
    user_id = factory.SubFactory(UserFactory)
    balance = Decimal("100.00")
    currency = CurrencyEnum.USD.value
