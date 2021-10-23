from pydantic import BaseModel, EmailStr, condecimal

from .currency import CurrencyEnum


class BaseUser(BaseModel):
    """Baseentity for User."""

    id: int
    email: EmailStr


class User(BaseUser):
    """Entity for representing User information."""

    wallet_id: int
    balance: condecimal(ge=0)  # type: ignore
    currency: CurrencyEnum
