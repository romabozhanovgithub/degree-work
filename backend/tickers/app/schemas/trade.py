from datetime import datetime
from decimal import Decimal
from bson import ObjectId
from pydantic import Field, condecimal

from app.schemas import PyObjectId, UserTrade
from app.schemas.base import BaseModelSchema


class TradeDB(BaseModelSchema):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    symbol: str
    orders: list[PyObjectId] = Field(
        ..., max_items=2, min_items=2, unique_items=True
    )
    price: condecimal(decimal_places=4, gt=0)
    qty: condecimal(decimal_places=4, gt=0)
    users: list[UserTrade] = Field(max_items=2, min_items=2, unique_items=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TradeResponse(TradeDB):
    class Config(TradeDB.Config):
        json_encoders = {
            ObjectId: str,
            Decimal: str,
        }
        exclude = ("users",)


class TradeListResponse(TradeDB):
    class Config(TradeDB.Config):
        json_encoders = {
            ObjectId: str,
            Decimal: str,
        }
        # exclude users from response
        exclude = ("users",)


class NewTradesList(BaseModelSchema):
    new_trades: list[TradeListResponse]
