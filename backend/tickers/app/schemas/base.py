from decimal import Decimal
import json
from bson import ObjectId
from bson.decimal128 import Decimal128
from pydantic import BaseModel
from pydantic.utils import to_lower_camel


class BaseModelSchema(BaseModel):
    def _check_field_type(self, data: dict, key: str):
        if isinstance(data[key], Decimal):
            data[key] = Decimal128(data[key])

    def to_dict(self, *args, **kwargs):
        data = self.dict(by_alias=True, *args, **kwargs)
        for key in data:
            self._check_field_type(data, key)
        return data

    def to_json(self, *args, **kwargs):
        data = self.json(*args, **kwargs)
        return json.loads(data)

    class Config:
        alias_generator = to_lower_camel
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            Decimal128: Decimal,
        }
        by_alias = True
