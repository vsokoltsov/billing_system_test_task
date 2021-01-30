import factory
from pytest_factoryboy import register

@register
class UserFactory(factory.Factory):
    email = factory.Sequence(lambda n: f'example{n}@gmail.com')