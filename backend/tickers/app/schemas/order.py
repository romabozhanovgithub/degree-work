from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel, Field, condecimal
from app.schemas import PyObjectId


class OrderBase(BaseModel):
    name: str
    price: condecimal(max_digits=10, decimal_places=4, ge=0)
    volume: condecimal(max_digits=10, decimal_places=4, ge=0)
    type: str
    user: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }


class Order(OrderBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    class Config:
        schema_extra = {
            "example": {
                "name": "AAPL",
                "price": 123.45,
                "volume": 100000,
                "datetime": "2021-01-01T00:00:00",
                "type": "BUY"
            }
        }


class OrderRequest(OrderBase):
    class Config:
        schema_extra = {
            "example": {
                "name": "AAPL",
                "price": 123.45,
                "volume": 100000,
                "type": "BUY",
                "user": "c27a9f97-9a6d-4222-8b2c-9ab9e8879038"
            }
        }


class OrderResponse(OrderBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    datetime: datetime

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }
        schema_extra = {
            "example": {
                "_id": "601b1e4d4c7e1f4b4c4b4f5d",
                "name": "AAPL",
                "price": 123.45,
                "volume": 100000,
                "datetime": "2021-01-01T00:00:00",
                "type": "BUY",
                "user": "c27a9f97-9a6d-4222-8b2c-9ab9e8879038"
            }
        }


class OrderLast(BaseModel):
    price: str
    volume: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "price": 123.45,
                "volume": 100000,
            },
        }


class OrdersLast(BaseModel):
    BUY: list[OrderLast]
    SELL: list[OrderLast]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "BUY": [
                    {
                        "price": 100.0,
                        "volume": 10.0,
                    },
                ],
                "SELL": [
                    {
                        "price": 100.0,
                        "volume": 10.0,
                    },
                ],
            },
        }
