from fastapi import Depends, HTTPException
from mongosql import MongoQuery
from pydantic import BaseModel
from sqlmodel import SQLModel

QBNotImplemented = 'QB Not implemented !!!'


class AdaptedModel(SQLModel):
    class Config:
        orm_mode = True

    @classmethod
    def get_field_names(cls, alias=False):
        """Return all fields"""
        return list(cls.schema(alias).get("properties").keys())


class QueryBuiderItem(BaseModel):
    """Query Builder Item model"""
    # If set project (list of fields) - anywat return all fields, but filled default data
    # TODO: not work, need debug !
    # project: list[str] = []

    filter: dict | None = None
    sort: list[str] = []
    skip: int | None = 0
    limit: int | None = 0

    # TODO: response stay now very direfent, how cast to more standart ?
    count: int | None = 0


class QueryBuilderCountResponse(AdaptedModel):
    """Return rows count (ignore offset and limit params), when set count: 1 """
    count: int


class QueryBuiderRequest(AdaptedModel):
    """Standart way provide params for back-end, use only this Model !!!"""
    qb: QueryBuiderItem  # | None = None


def get_qb(model, qb: QueryBuiderItem, **kwargs):
    query_object = qb.dict(exclude_none=True, exclude_defaults=True, skip_defaults=True)

    try:
        mq = MongoQuery(model).query(**query_object)
    except Exception as e:
        raise HTTPException(
            status_code=422, detail=str(e)
        )
    return mq.end()
