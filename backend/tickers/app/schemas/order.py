from datetime import datetime
from decimal import Decimal
from typing import Literal
from bson import ObjectId
from pydantic import Field, condecimal
from pydantic.utils import to_lower_camel

from app.schemas import PyObjectId
from app.schemas.base import BaseModelSchema


class OrderDB(BaseModelSchema):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    symbol: str
    price: condecimal(decimal_places=4, gt=0)
    init_qty: condecimal(decimal_places=4, gt=0)
    executed_qty: condecimal(decimal_places=4, ge=0) = Decimal(0)
    status: Literal["open", "closed", "canceled"] = "open"
    type: Literal["market", "limit"]
    side: Literal["buy", "sell"]
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: datetime | None = None


class OrderCreate(BaseModelSchema):
    symbol: str
    price: condecimal(decimal_places=4, gt=0)
    init_qty: condecimal(decimal_places=4, gt=0)
    type: Literal["market", "limit"]
    side: Literal["buy", "sell"]
    user_id: str

    class Config:
        alias_generator = to_lower_camel
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class OrderCreateRequest(OrderCreate):
    user_id: str | None = None

    class Config(OrderCreate.Config):
        by_alias = True


class OrderUpdate(BaseModelSchema):
    executed_qty: condecimal(decimal_places=4, ge=0) | None = None
    status: Literal["open", "closed", "canceled"] = "open"
    ended_at: datetime | None = None

    class Config:
        alias_generator = to_lower_camel
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class OrderResponseSchema(OrderDB):
    class Config:
        alias_generator = to_lower_camel
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        by_alias = True


class OrderLastResponseSchema(BaseModelSchema):
    buy: list[OrderResponseSchema]
    sell: list[OrderResponseSchema]
