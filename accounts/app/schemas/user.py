from typing import Optional
from pydantic import BaseModel, condecimal


class UserBase(BaseModel):
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: str
    balance: condecimal(max_digits=10, decimal_places=4)
    is_active: bool

    class Config:
        orm_mode = True


class UserInDB(UserBase):
    hashed_password: str
    is_active: bool

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
