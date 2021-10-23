import pytest
from decimal import Decimal
import asyncpg.exceptions as aioexceptions
from app.repositories.wallet import WalletRepository
from app.entities.wallet import WalletEntity


@pytest.mark.asyncio
async def test_success_wallet_creation(test_db, user_factory):
    """Test success wallet creation."""

    user = await user_factory.create()
    wallets_count = await test_db.execute("select count(*) from wallets")
    repository = WalletRepository(db=test_db)
    await repository.create(user_id=user.id)
    new_wallets_count = await test_db.execute("select count(*) from wallets")
    assert new_wallets_count == wallets_count + 1


@pytest.mark.asyncio
async def test_failed_wallet_creation(test_db):
    """Test failed wallet creation (user does not exist)."""

    repository = WalletRepository(db=test_db)
    with pytest.raises(aioexceptions.ForeignKeyViolationError):
        await repository.create(user_id=1)


@pytest.mark.asyncio
async def test_success_receiving_wallet_by_user_id(test_db, wallet_factory):
    """Test success receiving wallet by user id."""

    wallet = await wallet_factory.create()
    repository = WalletRepository(db=test_db)
    wallet: WalletEntity = (
        await repository.get_by_user_id(user_id=wallet.user_id)
    )
    assert wallet is not None
    assert wallet.balance == Decimal('100.0')


@pytest.mark.asyncio
async def test_failed_receiving_wallet_by_user_id(test_db):
    """Test failed receiving wallet by user id. (wallet does not exists)"""

    repository = WalletRepository(db=test_db)
    wallet = await repository.get_by_user_id(user_id=1)
    assert wallet is None


@pytest.mark.asyncio
async def test_success_receiving_wallet_by_id(test_db, wallet_factory):
    """Test success receiving wallet by id."""

    wallet = await wallet_factory.create()
    repository = WalletRepository(db=test_db)
    wallet: WalletEntity = (
        await repository.get_by_id(wallet_id=wallet.id)
    )
    assert wallet is not None
    assert wallet.balance == Decimal('100.0')

@pytest.mark.asyncio
async def test_failed_receiving_wallet_by_id(test_db, wallet_factory):
    """Test failed receiving wallet by wallet id. (wallet does not exists)"""

    wallet = await wallet_factory.create()
    repository = WalletRepository(db=test_db)
    wallet = await repository.get_by_id(wallet_id=1)
    assert wallet is None


@pytest.mark.asyncio
async def test_success_wallet_enroll(test_db, wallet_factory):
    """Test success wallet enroll."""

    wallet = await wallet_factory.create()
    repository = WalletRepository(db=test_db)
    old_wallet = await repository.get_by_user_id(user_id=wallet.user_id)
    await repository.enroll(wallet_id=wallet.id, amount=Decimal('10.0'))
    wallet = await repository.get_by_user_id(user_id=wallet.user_id)
    assert wallet.balance == old_wallet.balance + Decimal('10.0')


@pytest.mark.asyncio
async def test_failed_wallet_enroll(test_db):
    """Test failed wallet enroll (wallet does not exists)"""

    repository = WalletRepository(db=test_db)
    wallet_id = await repository.enroll(wallet_id=1, amount=Decimal('10.0'))
    assert wallet_id is None


@pytest.mark.asyncio
async def test_success_wallet_transfer(test_db, wallet_factory):
    """Test success transfer between wallets function."""

    wallet_1 = await wallet_factory.create()
    wallet_2 = await wallet_factory.create()
    repository = WalletRepository(db=test_db)
    await repository.transfer(
        source_wallet_id=wallet_1.id,
        destination_wallet_id=wallet_2.id,
        amount=Decimal('10')
    )
    refreshed_wallet_1 = await repository.get_by_id(wallet_1.id)
    refreshed_wallet_2 = await repository.get_by_id(wallet_2.id)
    assert refreshed_wallet_1.balance == wallet_1.balance - Decimal('10')
    assert refreshed_wallet_2.balance == wallet_2.balance + Decimal('10')


@pytest.mark.asyncio
async def test_failed_wallet_transfer(test_db, wallet_factory):
    """
    Test failed transfer between wallets function
    (source wallet does not exist).
    """

    wallet_2 = await wallet_factory.create()
    repository = WalletRepository(db=test_db)
    with pytest.raises(ValueError):
        await repository.transfer(
            source_wallet_id=1,
            destination_wallet_id=wallet_2.id,
            amount=Decimal('10')
        )
