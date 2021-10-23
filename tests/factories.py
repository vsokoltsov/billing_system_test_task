from decimal import Decimal
import factory
import inspect
from app.adapters.sql.models import users, wallets
from app.adapters.sql.db import get_db
from app.entities.currency import CurrencyEnum
from app.entities.wallet import WalletEntity
from app.entities.user import BaseUser
from pydantic import BaseModel

class SQLAlchemyCoreFactory(factory.Factory):
    
    class Meta:
        abstract = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        async def create_coro(*args, **kwargs):
            _db = get_db()
            schema = kwargs.pop('schema', None)
            for key in kwargs.keys():
                if inspect.iscoroutine(kwargs[key]):
                    kwargs[key] = await kwargs[key]
                if issubclass(kwargs[key].__class__, BaseModel):
                    kwargs[key] = kwargs[key].id

            object_id = await _db.execute(
                query=model_class.insert().returning(model_class.c.id),
                values=kwargs
            )
            if schema:
                obj_raw = await _db.fetch_one(
                    model_class.select()
                    .where(model_class.c.id==object_id)
                )
                return schema(**obj_raw)
            return object_id

        return create_coro(*args, **kwargs)

class UserFactory(SQLAlchemyCoreFactory):
    schema = BaseUser
    class Meta:
        model = users

    id = factory.Sequence(lambda i: i + 1)
    email = factory.LazyAttribute(lambda o: '%s@example.com' % o.id)

class WalletFactory(SQLAlchemyCoreFactory):
    schema = WalletEntity
    class Meta:
        model = wallets

    id = factory.Sequence(lambda n: n+1)
    user_id = factory.SubFactory(UserFactory)
    balance = Decimal('100.00')
    currency = CurrencyEnum.USD.value
