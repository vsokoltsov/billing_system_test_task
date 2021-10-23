from decimal import Decimal

from pydantic import BaseModel, EmailStr


class CreateUser(BaseModel):
    """Parameters description for user creation."""

    email: EmailStr


class UserResponse(BaseModel):
    """Fields for user responses."""

    id: int
    email: EmailStr
    wallet_id: int
    balance: Decimal
    currency: str
