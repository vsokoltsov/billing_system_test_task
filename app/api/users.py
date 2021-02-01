from typing import Any, Dict

import asyncpg
from fastapi import APIRouter, HTTPException, status

from app.models.user import User
from app.models.wallet import Wallet
from app.schemas.user import CreateUser, UserResponse
from app.schemas.wallet import WalletEnrollParams

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(params: CreateUser) -> Dict[str, Any]:
    """
    Creates new user and its wallet.

    :param params: Parameters for user's creation.
    """

    try:
        data = await User.create(params.email)
        if not data:
            raise HTTPException(status_code=400, detail="User create error.")
        return UserResponse(**data).dict()
    except asyncpg.exceptions.UniqueViolationError as unique_exception:
        raise HTTPException(
            status_code=400, detail="User with this email already exists."
        ) from unique_exception
    except asyncpg.exceptions.NotNullViolationError as not_null_exception:
        raise (
            HTTPException(status_code=400, detail="Error of wallet's creation.")
        ) from not_null_exception


@router.put(
    "/{user_id}/enroll", response_model=UserResponse, status_code=status.HTTP_200_OK
)
async def enroll(user_id: int, params: WalletEnrollParams):
    """
    API handler for enrollment of wallet.

    :param user_id: ID of user
    :param params: Parameters for enroll operation
    """

    row = await User.get(user_id)
    if not row:
        raise HTTPException(status_code=404, detail="User does not exists")

    if not row.get("wallet_id"):
        raise HTTPException(status_code=400, detail="Wallet for user does not exists")

    try:
        wallet_id = int(row["wallet_id"])
    except ValueError as value_err:
        raise HTTPException(
            status_code=400, detail="Wallet id is not integer"
        ) from value_err

    try:
        balance = await Wallet.enroll(wallet_id, params.amount)
        if balance is None:
            raise HTTPException(status_code=400, detail="Balance was not updated")
    except AssertionError as assert_err:
        raise HTTPException(
            status_code=400, detail="Balance was not updated"
        ) from assert_err

    user = dict(row)
    user["balance"] = balance
    return UserResponse(**user).dict()
