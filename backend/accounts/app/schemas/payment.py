from pydantic import BaseModel
from pydantic.utils import to_lower_camel


class PublishableKeyResponseSchema(BaseModel):
    publishable_key: str

    class Config:
        alias_generator = to_lower_camel
        allow_population_by_field_name = True
        by_alias = True


class DepositRequestSchema(BaseModel):
    amount: int


class DepositResponseSchema(BaseModel):
    client_secret: str
    publishable_key: str

    class Config:
        alias_generator = to_lower_camel
        allow_population_by_field_name = True
        by_alias = True


class WebHookSchema(BaseModel):
    data: dict
    type: str
