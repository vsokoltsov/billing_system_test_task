from fastapi import APIRouter

from app.models.user import User
from app.schemas.user import CreateUser, UserResponse

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/", response_model=UserResponse)
async def create_user(params: CreateUser) -> UserResponse:
    """ Creates new user and its wallet. """

    data = await User.create(params.email)
    return UserResponse(**data).dict()

@router.post("/enroll")
async def enroll():
    return {
        "message": "Transfer was applied"
    }