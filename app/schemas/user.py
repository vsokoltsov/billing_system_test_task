from pydantic import BaseModel

class CreateUser(BaseModel):
    email: str

class UserResponse(BaseModel):
    id: int
    email: str

    class Config:
        orm_mode = True
