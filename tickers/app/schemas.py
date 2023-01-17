from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel, Field


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema: dict):
        field_schema.update(type="string")


class TickerBase(BaseModel):
    name: str
    price: float
    volume: float
    datetime: datetime

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }


class Ticker(TickerBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    class Config:
        schema_extra = {
            "example": {
                "name": "AAPL",
                "price": 123.45,
                "volume": 100000,
                "datetime": "2021-01-01T00:00:00"
            }
        }


class TickerInDB(TickerBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    class Config:
        schema_extra = {
            "example": {
                "name": "AAPL",
                "price": 123.45,
                "volume": 100000,
                "datetime": "2021-01-01T00:00:00"
            }
        }


class TickerRequest(BaseModel):
    name: str
    price: float
    volume: float
    datetime: datetime

    class Config:
        schema_extra = {
            "example": {
                "name": "AAPL",
                "price": 123.45,
                "volume": 100000,
                "datetime": "2021-01-01T00:00:00"
            }
        }


class TickerResponse(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    price: float
    volume: float
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
                "datetime": "2021-01-01T00:00:00"
            }
        }
