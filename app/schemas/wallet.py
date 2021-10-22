from decimal import Decimal

from pydantic import BaseModel, root_validator, validator


class WalletEnrollParams(BaseModel):
    """JSON schema for enroll parameters."""

    amount: Decimal

    # pylint: disable=no-self-argument,no-self-use
    @validator("amount")
    def non_zero_amount(cls, value):
        """Validation for amount field."""

        if value == 0:
            raise ValueError("must be non-zero value")
        return value


class WalletTransferParams(BaseModel):
    """JSON schema for wallet transfer parameters."""

    wallet_from: int
    wallet_to: int
    amount: Decimal

    # pylint: disable=no-self-argument,no-self-use
    @root_validator
    def check_source_and_target_wallets(cls, values):
        """Validate 'wallet_from' and 'wallet_to' fields"""

        wallet_from = values.get("wallet_from")
        wallet_to = values.get("wallet_to")
        if wallet_from == wallet_to:
            raise ValueError("must not be equal")
        return values

    # pylint: disable=no-self-argument,no-self-use
    @validator("amount")
    def positive_amount(cls, value):
        """Validation for amount field."""

        if value <= 0:
            raise ValueError("must be positive value")
        return value
