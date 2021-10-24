from decimal import Decimal

import pytest
from asyncpg.exceptions import CheckViolationError

from app.entities.wallet_operation import Operations
from app.repositories.wallet_operations import WalletOperationRepository


@pytest.mark.asyncio
async def test_success_wallet_operation_creation(test_db):
    """Test success wallet operation creation."""

    repository = WalletOperationRepository(db=test_db)
    wallet_operation_id = await repository.create(
        operation=Operations.CREATE,
        wallet_from=1,
        wallet_to=2,
        amount=Decimal("100.00"),
    )
    assert wallet_operation_id is not None


@pytest.mark.asyncio
async def test_failed_wallet_operation_creation(test_db):
    """Test failed wallet operation creation (amount is negative)"""

    repository = WalletOperationRepository(db=test_db)
    with pytest.raises(CheckViolationError):
        await repository.create(
            operation=Operations.CREATE,
            wallet_from=1,
            wallet_to=2,
            amount=Decimal("-100.00"),
        )
