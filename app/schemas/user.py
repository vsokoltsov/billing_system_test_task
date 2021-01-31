from decimal import Decimal

from pydantic import BaseModel
from pydantic import EmailStr

class CreateUser(BaseModel):
    email: EmailStr

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    wallet_id: int
    balance: Decimal
