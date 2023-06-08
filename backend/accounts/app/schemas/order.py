from datetime import datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, Field, condecimal
from pydantic.utils import to_lower_camel


class OrderSchema(BaseModel):
    id: str = Field(..., alias="_id")
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

    class Config:
        alias_generator = to_lower_camel
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            Decimal: lambda d: str(d),
        }
