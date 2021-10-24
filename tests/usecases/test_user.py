import pytest

from app.repositories.users import UserRepository
from app.repositories.wallet import WalletRepository
from app.repositories.wallet_operations import WalletOperationRepository
from app.usecases.user import UserUsecase


@pytest.mark.asyncio
async def test_success_user_create_usecase(test_db):
    """Test success user create usecase."""

    user_repo = UserRepository(db=test_db)
    wallet_repo = WalletRepository(db=test_db)
    wallet_operation_repo = WalletOperationRepository(db=test_db)

    usecase = UserUsecase(
        db=test_db,
        user_repo=user_repo,
        wallet_repo=wallet_repo,
        wallet_operation_repo=wallet_operation_repo,
    )

    users_count = await test_db.execute("select count(*) from users")
    wallets_count = await test_db.execute("select count(*) from wallets")
    wo_count = await test_db.execute("select count(*) from wallet_operations")

    user = await usecase.create("example@mail.com")

    new_users_count = await test_db.execute("select count(*) from users")
    new_wallets_count = await test_db.execute("select count(*) from wallets")
    new_wo_count = await test_db.execute("select count(*) from wallet_operations")

    assert new_users_count == users_count + 1
    assert new_wallets_count == wallets_count + 1
    assert new_wo_count == wo_count + 1

    assert user is not None


@pytest.mark.asyncio
async def test_failed_user_create_usecase_user(test_db):
    """Test failed user create usecase. (user was not created)"""

    user_repo = UserRepository(db=test_db)
    wallet_repo = WalletRepository(db=test_db)
    wallet_operation_repo = WalletOperationRepository(db=test_db)

    usecase = UserUsecase(
        db=test_db,
        user_repo=user_repo,
        wallet_repo=wallet_repo,
        wallet_operation_repo=wallet_operation_repo,
    )
    with pytest.raises(ValueError):
        await usecase.create("")


@pytest.mark.asyncio
async def test_failed_user_create_usecase_wallet(test_db, wallet_repository_mock):
    """Test failed user create usecase. (wallet was not created)"""

    wallet_repository_mock.create.side_effect = [ValueError("wallet was not created")]
    user_repo = UserRepository(db=test_db)
    wallet_operation_repo = WalletOperationRepository(db=test_db)

    usecase = UserUsecase(
        db=test_db,
        user_repo=user_repo,
        wallet_repo=wallet_repository_mock,
        wallet_operation_repo=wallet_operation_repo,
    )
    with pytest.raises(ValueError):
        await usecase.create("example@mail.com")


@pytest.mark.asyncio
async def test_failed_user_create_usecase_rollback_previous(
    test_db, wallet_repository_mock
):
    """Test failed user create usecase. (wallet was not created)"""

    wallet_repository_mock.create.side_effect = [ValueError("wallet was not created")]
    user_repo = UserRepository(db=test_db)
    wallet_operation_repo = WalletOperationRepository(db=test_db)

    usecase = UserUsecase(
        db=test_db,
        user_repo=user_repo,
        wallet_repo=wallet_repository_mock,
        wallet_operation_repo=wallet_operation_repo,
    )
    users_count = await test_db.execute("select count(*) from users")
    with pytest.raises(ValueError):
        await usecase.create("example@mail.com")

    new_users_count = await test_db.execute("select count(*) from users")
    assert users_count == new_users_count


@pytest.mark.asyncio
async def test_failed_user_create_usecase_wallet_operation(
    test_db, wallet_operation_repository_mock
):
    """Test failed user create usecase. (wallet operation was not created)"""

    wallet_operation_repository_mock.create.side_effect = [
        ValueError("wallet operation was not created")
    ]
    user_repo = UserRepository(db=test_db)
    wallet_repo = WalletRepository(db=test_db)

    usecase = UserUsecase(
        db=test_db,
        user_repo=user_repo,
        wallet_repo=wallet_repo,
        wallet_operation_repo=wallet_operation_repository_mock,
    )
    users_count = await test_db.execute("select count(*) from users")
    wallets_count = await test_db.execute("select count(*) from wallets")
    with pytest.raises(ValueError):
        await usecase.create("example@mail.com")

    new_users_count = await test_db.execute("select count(*) from users")
    new_wallets_count = await test_db.execute("select count(*) from wallets")
    assert users_count == new_users_count
    assert wallets_count == new_wallets_count


@pytest.mark.asyncio
async def test_failed_user_create_usecase_user_retrieve(
    test_db, user_repository_mock, user_factory
):
    """Test failed user create usecase. (wallet operation was not created)"""

    user = await user_factory.create()
    user_repository_mock.create.return_value = user.id
    user_repository_mock.get_by_id.side_effect = [
        ValueError("Error database connection")
    ]

    wallet_repo = WalletRepository(db=test_db)
    wallet_operation_repo = WalletOperationRepository(db=test_db)

    usecase = UserUsecase(
        db=test_db,
        user_repo=user_repository_mock,
        wallet_repo=wallet_repo,
        wallet_operation_repo=wallet_operation_repo,
    )
    users_count = await test_db.execute("select count(*) from users")
    wallets_count = await test_db.execute("select count(*) from wallets")
    with pytest.raises(ValueError):
        await usecase.create("example@mail.com")

    new_users_count = await test_db.execute("select count(*) from users")
    new_wallets_count = await test_db.execute("select count(*) from wallets")
    assert users_count == new_users_count
    assert wallets_count == new_wallets_count
