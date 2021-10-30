from decimal import Decimal

import pytest

from app.adapters.sql.tx import SQLTransactionManager
from app.entities.user import UserDoesNotExist
from app.entities.wallet import WalletDoesNotExist
from app.repositories.users import UserRepository
from app.repositories.wallet import WalletRepository
from app.repositories.wallet_operations import WalletOperationRepository
from app.usecases.wallet import WalletUsecase


@pytest.mark.asyncio
async def test_success_wallet_enroll_usecase(test_db, user_factory, wallet_factory):
    """Test success wallet enroll usecase."""

    user = user_factory.create()
    wallet = wallet_factory.create(user=user)
    old_balance = wallet.balance

    tx_manager = SQLTransactionManager(db=test_db)
    user_repo = UserRepository(db=test_db)
    wallet_repo = WalletRepository(db=test_db)
    wallet_operation_repo = WalletOperationRepository(db=test_db)

    usecase = WalletUsecase(
        tx_manager=tx_manager,
        user_repo=user_repo,
        wallet_repo=wallet_repo,
        wallet_operation_repo=wallet_operation_repo,
    )
    new_user = await usecase.enroll(user_id=user.id, amount=Decimal("10.0"))
    assert new_user.balance == old_balance + Decimal("10.0")


@pytest.mark.asyncio
async def test_failed_wallet_enroll_usecase_get_user(
    test_db, user_factory, wallet_factory, user_repository_mock
):
    """Test failed wallet enroll usecase (user does not exist)"""

    user = user_factory.create()
    wallet_factory.create(user=user)

    tx_manager = SQLTransactionManager(db=test_db)
    user_repository_mock.get_by_id.return_value = None
    wallet_repo = WalletRepository(db=test_db)
    wallet_operation_repo = WalletOperationRepository(db=test_db)

    usecase = WalletUsecase(
        tx_manager=tx_manager,
        user_repo=user_repository_mock,
        wallet_repo=wallet_repo,
        wallet_operation_repo=wallet_operation_repo,
    )
    with pytest.raises(UserDoesNotExist):
        await usecase.enroll(user_id=user.id, amount=Decimal("10.0"))


@pytest.mark.asyncio
async def test_failed_wallet_enroll_usecase_get_user_response(
    test_db, user_factory, wallet_factory, user_repository_mock
):
    """Test failed wallet enroll usecase (user was deleted)"""

    base_user = user_factory.create()
    wallet_factory.create(user=base_user)

    tx_manager = SQLTransactionManager(db=test_db)
    user_repo = UserRepository(db=test_db)
    user = await user_repo.get_by_id(user_id=base_user.id)
    user_repository_mock.get_by_id.side_effect = [user, None]
    wallet_repo = WalletRepository(db=test_db)
    wallet_operation_repo = WalletOperationRepository(db=test_db)

    usecase = WalletUsecase(
        tx_manager=tx_manager,
        user_repo=user_repository_mock,
        wallet_repo=wallet_repo,
        wallet_operation_repo=wallet_operation_repo,
    )
    with pytest.raises(UserDoesNotExist):
        await usecase.enroll(user_id=user.id, amount=Decimal("10.0"))


@pytest.mark.asyncio
async def test_failed_wallet_enroll_usecase(
    test_db, user_factory, wallet_factory, wallet_repository_mock
):
    """Test failed wallet enroll usecase. (enroll error)"""

    base_user = user_factory.create()
    wallet_factory.create(user=base_user)

    wallet_repository_mock.enroll.side_effect = [ValueError]

    tx_manager = SQLTransactionManager(db=test_db)
    user_repo = UserRepository(db=test_db)
    user = await user_repo.get_by_id(user_id=base_user.id)
    # wallet_repo = WalletRepository(db=test_db)
    wallet_operation_repo = WalletOperationRepository(db=test_db)

    usecase = WalletUsecase(
        tx_manager=tx_manager,
        user_repo=user_repo,
        wallet_repo=wallet_repository_mock,
        wallet_operation_repo=wallet_operation_repo,
    )
    with pytest.raises(ValueError):
        await usecase.enroll(user_id=user.id, amount=Decimal("10.0"))

    new_user = await user_repo.get_by_id(user_id=user.id)
    assert new_user.balance == user.balance


@pytest.mark.asyncio
async def test_failed_wallet_enroll_usecase_wallet_operation(
    test_db, user_factory, wallet_factory, wallet_operation_repository_mock
):
    """Test failed wallet enroll usecase (wallet operation create error)."""

    base_user = user_factory.create()
    wallet = wallet_factory.create(user=base_user)

    tx_manager = SQLTransactionManager(db=test_db)
    wallet_operation_repository_mock.create.side_effect = [ValueError]
    user_repo = UserRepository(db=test_db)
    user = await user_repo.get_by_id(user_id=base_user.id)
    wallet_repo = WalletRepository(db=test_db)

    usecase = WalletUsecase(
        tx_manager=tx_manager,
        user_repo=user_repo,
        wallet_repo=wallet_repo,
        wallet_operation_repo=wallet_operation_repository_mock,
    )

    with pytest.raises(ValueError):
        await usecase.enroll(user_id=user.id, amount=Decimal("10.0"))
    new_user = await user_repo.get_by_id(user_id=user.id)
    assert new_user.balance == wallet.balance


@pytest.mark.asyncio
async def test_success_wallet_transfer_usecase(test_db, user_factory, wallet_factory):
    """Test success wallet enroll usecase."""

    base_user_1 = user_factory.create()
    wallet_1 = wallet_factory.create(user=base_user_1)

    base_user_2 = user_factory.create()
    wallet_2 = wallet_factory.create(user=base_user_2)

    tx_manager = SQLTransactionManager(db=test_db)
    user_repo = UserRepository(db=test_db)
    wallet_repo = WalletRepository(db=test_db)
    wallet_operation_repo = WalletOperationRepository(db=test_db)

    wo_count = await test_db.execute("select count(*) from wallet_operations;")

    usecase = WalletUsecase(
        tx_manager=tx_manager,
        user_repo=user_repo,
        wallet_repo=wallet_repo,
        wallet_operation_repo=wallet_operation_repo,
    )
    new_user = await usecase.transfer(
        source_wallet_id=wallet_1.id,
        destination_wallet_id=wallet_2.id,
        amount=Decimal("10.0"),
    )
    new_wo_count = await test_db.execute("select count(*) from wallet_operations;")
    new_wallet_2 = await wallet_repo.get_by_id(wallet_id=wallet_2.id)
    assert new_user.balance == wallet_1.balance - Decimal("10.0")
    assert new_wallet_2.balance == wallet_2.balance + Decimal("10.0")
    assert new_wo_count == wo_count + 2


@pytest.mark.asyncio
async def test_failed_wallet_transfer_usecas_amount(test_db, user_factory, wallet_factory):
    """Test failed wallet enroll usecase (amount not sufficient)"""

    base_user_1 = user_factory.create()
    wallet_1 = wallet_factory.create(user=base_user_1)

    base_user_2 = user_factory.create()
    wallet_2 = wallet_factory.create(user=base_user_2)

    tx_manager = SQLTransactionManager(db=test_db)
    user_repo = UserRepository(db=test_db)
    wallet_repo = WalletRepository(db=test_db)
    wallet_operation_repo = WalletOperationRepository(db=test_db)

    usecase = WalletUsecase(
        tx_manager=tx_manager,
        user_repo=user_repo,
        wallet_repo=wallet_repo,
        wallet_operation_repo=wallet_operation_repo,
    )
    with pytest.raises(ValueError):
        await usecase.transfer(
            source_wallet_id=wallet_1.id,
            destination_wallet_id=wallet_2.id,
            amount=Decimal("0.0"),
        )
    new_user = await user_repo.get_by_id(base_user_1.id)
    new_wallet_2 = await wallet_repo.get_by_id(wallet_id=wallet_2.id)
    assert new_user.balance == wallet_1.balance
    assert new_wallet_2.balance == wallet_2.balance


@pytest.mark.asyncio
async def test_failed_wallet_transfer_usecase_source_wallet_none(
    test_db, user_factory, wallet_factory, wallet_repository_mock
):
    """Test failed wallet enroll usecase (source wallet does not exists)"""

    wallet_repository_mock.get_by_id.return_value = None

    base_user_1 = user_factory.create()
    wallet_1 = wallet_factory.create(user=base_user_1)

    base_user_2 = user_factory.create()
    wallet_2 = wallet_factory.create(user=base_user_2)

    tx_manager = SQLTransactionManager(db=test_db)
    user_repo = UserRepository(db=test_db)
    wallet_repo = WalletRepository(db=test_db)
    wallet_operation_repo = WalletOperationRepository(db=test_db)

    usecase = WalletUsecase(
        tx_manager=tx_manager,
        user_repo=user_repo,
        wallet_repo=wallet_repository_mock,
        wallet_operation_repo=wallet_operation_repo,
    )
    with pytest.raises(WalletDoesNotExist):
        await usecase.transfer(
            source_wallet_id=wallet_1.id,
            destination_wallet_id=wallet_2.id,
            amount=Decimal("10.0"),
        )
    new_user = await user_repo.get_by_id(base_user_1.id)
    new_wallet_2 = await wallet_repo.get_by_id(wallet_id=wallet_2.id)
    assert new_user.balance == wallet_1.balance
    assert new_wallet_2.balance == wallet_2.balance


@pytest.mark.asyncio
async def test_failed_wallet_transfer_usecase_destination_wallet_none(
    test_db, user_factory, wallet_factory, wallet_repository_mock
):
    """Test failed wallet enroll usecase (destination wallet does not exists)"""

    base_user_1 = user_factory.create()
    wallet_1 = wallet_factory.create(user=base_user_1)

    wallet_repository_mock.get_by_id.side_effect = [wallet_1, None]

    base_user_2 = user_factory.create()
    wallet_2 = wallet_factory.create(user=base_user_2)

    tx_manager = SQLTransactionManager(db=test_db)
    user_repo = UserRepository(db=test_db)
    wallet_repo = WalletRepository(db=test_db)
    wallet_operation_repo = WalletOperationRepository(db=test_db)

    usecase = WalletUsecase(
        tx_manager=tx_manager,
        user_repo=user_repo,
        wallet_repo=wallet_repository_mock,
        wallet_operation_repo=wallet_operation_repo,
    )
    with pytest.raises(WalletDoesNotExist):
        await usecase.transfer(
            source_wallet_id=wallet_1.id,
            destination_wallet_id=wallet_2.id,
            amount=Decimal("10.0"),
        )
    new_user = await user_repo.get_by_id(base_user_1.id)
    new_wallet_2 = await wallet_repo.get_by_id(wallet_id=wallet_2.id)
    assert new_user.balance == wallet_1.balance
    assert new_wallet_2.balance == wallet_2.balance


@pytest.mark.asyncio
async def test_failed_wallet_transfer_usecase_user_none(
    test_db, user_factory, wallet_factory, user_repository_mock
):
    """Test failed wallet enroll usecase. (user is none)"""

    base_user_1 = user_factory.create()
    wallet_1 = wallet_factory.create(user=base_user_1)

    base_user_2 = user_factory.create()
    wallet_2 = wallet_factory.create(user=base_user_2)

    tx_manager = SQLTransactionManager(db=test_db)
    user_repo = UserRepository(db=test_db)
    user_repository_mock.get_by_wallet_id.return_value = None
    wallet_repo = WalletRepository(db=test_db)
    wallet_operation_repo = WalletOperationRepository(db=test_db)

    usecase = WalletUsecase(
        tx_manager=tx_manager,
        user_repo=user_repository_mock,
        wallet_repo=wallet_repo,
        wallet_operation_repo=wallet_operation_repo,
    )
    with pytest.raises(UserDoesNotExist):
        await usecase.transfer(
            source_wallet_id=wallet_1.id,
            destination_wallet_id=wallet_2.id,
            amount=Decimal("10.0"),
        )
    new_user = await user_repo.get_by_id(base_user_1.id)
    new_wallet_2 = await wallet_repo.get_by_id(wallet_id=wallet_2.id)
    assert new_user.balance == wallet_1.balance
    assert new_wallet_2.balance == wallet_2.balance


@pytest.mark.asyncio
async def test_failed_wallet_transfer_usecase_transfer(
    test_db, user_factory, wallet_factory, wallet_repository_mock
):
    """Test failed wallet enroll usecase (transfer error)."""

    base_user_1 = user_factory.create()
    wallet_1 = wallet_factory.create(user=base_user_1)

    base_user_2 = user_factory.create()
    wallet_2 = wallet_factory.create(user=base_user_2)

    tx_manager = SQLTransactionManager(db=test_db)
    user_repo = UserRepository(db=test_db)
    wallet_repo = WalletRepository(db=test_db)
    wallet_repository_mock.get_by_id.side_effect = [wallet_1, wallet_2]
    wallet_repository_mock.transfer.side_effect = [ValueError("Transfer error")]
    wallet_operation_repo = WalletOperationRepository(db=test_db)

    usecase = WalletUsecase(
        tx_manager=tx_manager,
        user_repo=user_repo,
        wallet_repo=wallet_repository_mock,
        wallet_operation_repo=wallet_operation_repo,
    )
    with pytest.raises(ValueError):
        await usecase.transfer(
            source_wallet_id=wallet_1.id,
            destination_wallet_id=wallet_2.id,
            amount=Decimal("10.0"),
        )
    new_user = await user_repo.get_by_id(base_user_1.id)
    new_wallet_2 = await wallet_repo.get_by_id(wallet_id=wallet_2.id)
    assert new_user.balance == wallet_1.balance
    assert new_wallet_2.balance == wallet_2.balance
