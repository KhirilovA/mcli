from fastapi import Depends, HTTPException

from mongosql import MongoQuery
from pydantic import BaseModel
from sqlmodel import SQLModel


def rowdict(data) -> list[dict]:
    """Convert List[SQLModel] -> List[dict]"""
    result = [x._data[0].dict() for x in data]  # noqa
    return result


QBNotImplemented = 'QB Not implemented !!!'


# Adapted model, use how Base model for all models !!!"""
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


# QueryBuiderResponse = dict | int

def rekey(inp_dict, keys_replace):
    """Replace keys names in dict"""
    return {keys_replace.get(k, k): v for k, v in inp_dict.items()}


def rekeylist(list_dict: list, keys_replace: dict):
    """Replace keys names in list[dict]"""
    return [rekey(x, keys_replace) for x in list_dict]


def get_qb(model, qb: str | dict | QueryBuiderItem, **kwargs):
    """Get Query Builder Mongo Query Object from str, dict or QueryBuiderItem model"""
    # convert json str to dict if need
    # j: dict = json_str_obj
    # j: dict | str = json_str_obj

    if type(qb) is str:
        query_object = json.loads(json_str_obj)  # noqa
    elif type(qb) is dict:
        query_object = qb
    elif type(qb) is QueryBuiderItem:
        query_object = qb.dict(exclude_none=True, exclude_defaults=True, skip_defaults=True)
    else:
        raise Exception('Unknown Query Builder input type')

    # print(j)

    # from .models import User  # Your model

    # ssn = Session()

    # Create a MongoQuery, using an initial Query (possibly, with some initial filtering applied)
    # query_object = j

    # mq = MongoQuery(model).from_query(ssn.query(model))
    # TODO: add suport FastAPI standart error exception
    try:
        mq = MongoQuery(model).query(**query_object)
    except Exception as e:
        raise HTTPException(
            status_code=422, detail=str(e)
        )

        # a = 1

    # By calling the `MongoQuery.end()` method, you get an SqlAlchemy `Query`:
    # result = mq.end()  # SqlALchemy Query

    # # Execute the query and fetch results
    # result = q.all()
    # print(q)
    # format_sql(q)
    # pass

    # print(query_object)
    # return result
    return mq.end()
