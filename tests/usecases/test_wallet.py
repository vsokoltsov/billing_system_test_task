from decimal import Decimal

import pytest

from app.entities.user import UserDoesNotExist
from app.repositories.users import UserRepository
from app.repositories.wallet import WalletRepository
from app.repositories.wallet_operations import WalletOperationRepository
from app.usecases.wallet import WalletUsecase


@pytest.mark.asyncio
async def test_success_wallet_enroll_usecase(test_db, user_factory, wallet_factory):
    """Test success wallet enroll usecase."""

    user = await user_factory.create()
    wallet = await wallet_factory.create(user_id=user.id)

    user_repo = UserRepository(db=test_db)
    wallet_repo = WalletRepository(db=test_db)
    wallet_operation_repo = WalletOperationRepository(db=test_db)

    usecase = WalletUsecase(
        db=test_db,
        user_repo=user_repo,
        wallet_repo=wallet_repo,
        wallet_operation_repo=wallet_operation_repo,
    )
    new_user = await usecase.enroll(user_id=user.id, amount=Decimal("10.0"))
    assert new_user.balance == wallet.balance + Decimal("10.0")


@pytest.mark.asyncio
async def test_failed_wallet_enroll_usecase_get_user(
    test_db, user_factory, wallet_factory, user_repository_mock
):
    """Test failed wallet enroll usecase (user does not exist)"""

    user = await user_factory.create()
    await wallet_factory.create(user_id=user.id)

    user_repository_mock.get_by_id.return_value = None
    wallet_repo = WalletRepository(db=test_db)
    wallet_operation_repo = WalletOperationRepository(db=test_db)

    usecase = WalletUsecase(
        db=test_db,
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

    base_user = await user_factory.create()
    await wallet_factory.create(user_id=base_user.id)

    user_repo = UserRepository(db=test_db)
    user = await user_repo.get_by_id(user_id=base_user.id)
    user_repository_mock.get_by_id.side_effect = [user, None]
    wallet_repo = WalletRepository(db=test_db)
    wallet_operation_repo = WalletOperationRepository(db=test_db)

    usecase = WalletUsecase(
        db=test_db,
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

    base_user = await user_factory.create()
    await wallet_factory.create(user_id=base_user.id)

    wallet_repository_mock.enroll.side_effect = [ValueError]

    user_repo = UserRepository(db=test_db)
    user = await user_repo.get_by_id(user_id=base_user.id)
    # wallet_repo = WalletRepository(db=test_db)
    wallet_operation_repo = WalletOperationRepository(db=test_db)

    usecase = WalletUsecase(
        db=test_db,
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

    base_user = await user_factory.create()
    wallet = await wallet_factory.create(user_id=base_user.id)

    wallet_operation_repository_mock.create.side_effect = [ValueError]
    user_repo = UserRepository(db=test_db)
    user = await user_repo.get_by_id(user_id=base_user.id)
    wallet_repo = WalletRepository(db=test_db)

    usecase = WalletUsecase(
        db=test_db,
        user_repo=user_repo,
        wallet_repo=wallet_repo,
        wallet_operation_repo=wallet_operation_repository_mock,
    )

    with pytest.raises(ValueError):
        await usecase.enroll(user_id=user.id, amount=Decimal("10.0"))
    new_user = await user_repo.get_by_id(user_id=user.id)
    assert new_user.balance == wallet.balance
