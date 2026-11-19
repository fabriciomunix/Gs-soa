"""Base dos schemas: JSON em camelCase, aceitando também snake_case na entrada."""
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        str_strip_whitespace=True,
    )


class ErroResposta(CamelModel):
    detail: str
