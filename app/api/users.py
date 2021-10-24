import asyncpg
from fastapi import APIRouter, HTTPException, Request, status
from pydantic.error_wrappers import ValidationError

from app.entities.user import CreateUser, User, UserDoesNotExist
from app.entities.wallet import WalletEnrollParams
from app.usecases.user import UserUsecase
from app.usecases.wallet import WalletUsecase

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(request: Request, params: CreateUser) -> User:
    """Creates new user and its wallet."""

    try:
        usecase: UserUsecase = request.app.state.user_usecase
        user = await usecase.create(params.email)
        if not user:
            raise HTTPException(status_code=400, detail="User create error.")
        return user
    except asyncpg.exceptions.UniqueViolationError as unique_exception:
        raise HTTPException(
            status_code=400, detail="User with this email already exists."
        ) from unique_exception
    except asyncpg.exceptions.NotNullViolationError as not_null_exception:
        raise (
            HTTPException(status_code=400, detail="Error of wallet's creation.")
        ) from not_null_exception


@router.put("/{user_id}/enroll", response_model=User, status_code=status.HTTP_200_OK)
async def enroll(request: Request, user_id: int, params: WalletEnrollParams):
    """API handler for enrollment of wallet."""

    try:
        usecase: WalletUsecase = request.app.state.wallet_usecase
        user = await usecase.enroll(
            user_id=user_id,
            amount=params.amount,
        )
        return user
    except UserDoesNotExist as user_not_exist:
        raise HTTPException(
            status_code=404, detail="User does not exists"
        ) from user_not_exist
    except AssertionError as assert_err:
        raise HTTPException(
            status_code=400, detail="Balance was not updated"
        ) from assert_err
    except ValidationError as validation_err:
        raise HTTPException(
            status_code=400, detail=f"Error of response: {validation_err}"
        ) from validation_err
