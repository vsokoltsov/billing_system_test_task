from pydantic import BaseModel
from pydantic import EmailStr

class CreateUser(BaseModel):
    email: EmailStr

class UserResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True
