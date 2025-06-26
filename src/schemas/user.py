from uuid import UUID
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr
    first_name: str
    last_name: str

# Where we add the optional phone_number


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    id: int


class UserResponse(UserBase):
    id: UUID

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"  # Forward reference if UserResponse not defined yet
