# TODO: Need Full Describe class
from pydantic import BaseModel


class QueryBuilderItem(BaseModel):
    """Query Builder Item model"""
    project: list[str] = []

    # TODO: add support extract "not MV-ready" params from filter!
    # Something like: https://pydantic-docs.helpmanual.io/usage/model_config/  extra=Extra.forbid ???
    filter: dict | None = None
    sort: list[str] = []
    skip: int | None = 0
    limit: int | None = 0

    # TODO: response stay now very direfent, how cast to more standart ?
    count: int | None = 0


class AdaptedModel(BaseModel):
    class Config:
        orm_mode = True

    @classmethod
    def get_field_names(cls, alias=False, exclude: list[str] = None):
        """Return all fields"""
        response = list(cls.schema(alias).get("properties").keys())
        if exclude is not None:
            return [x for x in response if x not in exclude]
        return response
