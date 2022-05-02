import datetime
from typing import Optional, Dict
from pydantic import BaseModel, Json
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSON
from sqlmodel import SQLModel, Field


class ViewNameLinked(BaseModel):
    instance_name: str
    view_name: str
    sql_path: str
    pascal_cls_name: str



class ConfigModel(BaseModel):
    db_url: str
    root_folder: str
    url: str
    module_name: str
    pascal_name: str
    view_names_linked: list[ViewNameLinked]


class ViewInspectorModel(SQLModel, table=True):
    class Config:
        arbitrary_types_allowed = True

    id: Optional[int] = Field(default=None, primary_key=True)
    view_name: str = Field(index=True)
    sql_hash: str
    date_created: datetime.datetime
    date_modified: datetime.datetime
    config: Json = Field(default={}, sa_column=Column(JSON))
