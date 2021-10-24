from enum import Enum

from pydantic import BaseModel, condecimal


class Operations(Enum):
    retrieve = "retrieve"
    create = "create"
    receipt = "receipt"
    debit = "debit"


class WalletOperationEntity(BaseModel):
    """Represents entity for wallet operations"""

    id: int
    operation: Operations
    wallet_from: int
    wallet_to: int
    amount: condecimal(ge=0)
