from datetime import datetime
from pydantic import BaseModel, EmailStr
from pydantic.utils import to_lower_camel

from app.schemas.balance import BalanceResponseSchema


class UserBaseSchema(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr


class UserResponseSchema(UserBaseSchema):
    id: str
    is_verified: bool
    is_active: bool
    is_superuser: bool
    created_at: datetime

    class Config:
        orm_mode = True
        alias_generator = to_lower_camel
        allow_population_by_field_name = True
        by_alias = True


class UserWithBalaceResponseSchema(UserResponseSchema):
    balances: list[BalanceResponseSchema]


class UserDBSchema(UserResponseSchema):
    password: str

    class Config(UserResponseSchema.Config):
        by_alias = False
