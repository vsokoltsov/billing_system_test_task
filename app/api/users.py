from fastapi import APIRouter, status, HTTPException

import asyncpg

from app.models.user import User
from app.schemas.user import CreateUser, UserResponse

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

@router.post("/enroll")
async def enroll():
    return {
        "message": "Transfer was applied"
    }