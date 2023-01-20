from datetime import datetime
from pydantic import BaseModel, condecimal


class OrderBase(BaseModel):
    ticker: str
    price: condecimal(max_digits=10, decimal_places=4, ge=0)
    volume: condecimal(max_digits=10, decimal_places=4, ge=0)
    type: str


class OrderCreate(OrderBase):
    pass


class OrderResponse(OrderBase):
    id: str
    datetime: datetime
    is_active: bool

    class Config:
        orm_mode = True
