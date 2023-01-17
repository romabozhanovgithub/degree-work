from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field


class OrderBase(BaseModel):
    ticker: str
    price: Decimal
    volume: float
    type: str


class OrderCreate(OrderBase):
    pass


class OrderResponse(OrderBase):
    id: str
    datetime: datetime
    is_active: bool

    class Config:
        orm_mode = True


class OrderLast(BaseModel):
    price: Decimal
    volume: float


class OrdersLast(BaseModel):
    """
    ```python
    >>> return {
        "buy": [
            {
                "price": Decimal,
                "volume": float,
            },
        ],
        "sell": [
            {
                "price": Decimal,
                "volume": float,
            },
        ],
    }
    ```
    """

    buy: list[OrderLast]
    sell: list[OrderLast]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "buy": [
                    {
                        "price": 100.0,
                        "volume": 10.0,
                    },
                ],
                "sell": [
                    {
                        "price": 100.0,
                        "volume": 10.0,
                    },
                ],
            },
        }
