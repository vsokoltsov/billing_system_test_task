from enum import Enum

from pydantic import BaseModel, condecimal


class Operations(Enum):
    """Possible operations for wallet operation"""

    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    CREATE = "CREATE"


class WalletOperationEntity(BaseModel):
    """Represents entity for wallet operations"""

    id: int
    operation: Operations
    wallet_from: int
    wallet_to: int
    amount: condecimal(ge=0)  # type: ignore
