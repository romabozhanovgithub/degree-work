from datetime import datetime
from pydantic import BaseModel


class TickerBase(BaseModel):
    name: str


class TickerCreate(TickerBase):
    name: str
    price: float
    volume: float
    datetime: datetime
    type: str


class Ticker(TickerBase):
    id: str
    name: str
    price: float
    volume: float
    user_id: int

    class Config:
        orm_mode = True
