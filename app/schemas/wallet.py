from pydantic import BaseModel, validator
from decimal import Decimal

class WalletEnrollParams(BaseModel):
    amount: Decimal

    @validator('amount')
    def non_zero_amount(cls, v):
        if v == 0:
            raise ValueError('must be non-zero value')
        return v