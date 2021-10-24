from pydantic import BaseModel, condecimal, root_validator

from .currency import CurrencyEnum


class WalletDoesNotExist(Exception):
    """Exception for wallet does not exist error"""


class WalletEnrollParams(BaseModel):
    """JSON schema for enroll parameters."""

    amount: condecimal(gt=0)  # type: ignore


class WalletTransferParams(BaseModel):
    """JSON schema for wallet transfer parameters."""

    wallet_from: int
    wallet_to: int
    amount: condecimal(ge=0)  # type: ignore

    # pylint: disable=no-self-argument,no-self-use
    @root_validator
    def check_source_and_target_wallets(cls, values):
        """Validate 'wallet_from' and 'wallet_to' fields"""

        wallet_from = values.get("wallet_from")
        wallet_to = values.get("wallet_to")
        if wallet_from == wallet_to:
            raise ValueError("must not be equal")
        return values


class WalletEntity(BaseModel):
    """Representation of wallet entity."""

    id: int
    user_id: int
    balance: condecimal(ge=0)  # type: ignore
    currency: CurrencyEnum
