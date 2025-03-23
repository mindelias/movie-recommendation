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
    

class UserResponse(UserBase):
    id: UUID 
    class Config:
         from_attributes = True
