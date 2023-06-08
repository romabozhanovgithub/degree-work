from decimal import Decimal
from typing import Optional
from pydantic import BaseModel
from pydantic.utils import to_lower_camel


class BalanceResponseSchema(BaseModel):
    user_id: str
    currency: str
    amount: str

    class Config:
        orm_mode = True
        alias_generator = to_lower_camel
        allow_population_by_field_name = True
        by_alias = True
        json_encoders = {
            Decimal: lambda d: str(d),
        }


class BalanceUpdateSchema(BaseModel):
    user_id: Optional[str] = None
    currency: str
    amount: Decimal

    class Config:
        orm_mode = True
        alias_generator = to_lower_camel
        allow_population_by_field_name = True
        by_alias = True
