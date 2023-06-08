from datetime import datetime
from typing import Literal
from pydantic import EmailStr

from app.schemas.base import BaseModelSchema


class UserTrade(BaseModelSchema):
    user_id: str
    side: Literal["buy", "sell"]


class UserSchema(BaseModelSchema):
    id: str
    first_name: str
    last_name: str
    email: EmailStr
    id: str
    is_verified: bool
    is_active: bool
    is_superuser: bool
    created_at: datetime
