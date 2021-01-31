from fastapi import APIRouter, status, HTTPException

import asyncpg

from app.models.user import User
from app.models.wallet import Wallet
from app.schemas.user import CreateUser, UserResponse
from app.schemas.wallet import WalletEnrollParams

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(params: CreateUser) -> UserResponse:
    """ Creates new user and its wallet. """

    try:
        data = await User.create(params.email)
        return UserResponse(**data).dict()
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(status_code=400, detail="User with this email already exists.")
    except asyncpg.exceptions.NotNullViolationError:
        raise HTTPException(status_code=400, detail="Error of wallet's creation.")

@router.put("/{user_id}/enroll", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def enroll(user_id: int, params: WalletEnrollParams):
    row = await User.get(user_id)
    if not row:
        raise HTTPException(status_code=404, detail="User does not exists")

    try:
        balance = await Wallet.enroll(row.get('wallet_id'), params.amount)
        if balance is None:
            raise HTTPException(status_code=400, detail="Balance was not updated")
    except AssertionError:
        raise HTTPException(status_code=400, detail="Balance was not updated")

    user = dict(row)
    user['balance'] = balance
    return UserResponse(**user).dict()