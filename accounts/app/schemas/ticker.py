from pydantic import BaseModel


class TickerBase(BaseModel):
    name: str


class TickerCreate(TickerBase):
    volume: float


class Ticker(TickerBase):
    id: str
    ticker_name: str
    user_id: int

    class Config:
        orm_mode = True
