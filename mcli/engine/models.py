import datetime
from typing import Optional
from pydantic import BaseModel
from sqlmodel import SQLModel, Field


class ConfigModel(BaseModel):
    db_name: str
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_schema: str
    sql_module: str
    sql_full_path: str
    sql_name: str
    root_folder: str
    view_name: str
    create_index: bool
    index_name: str
    index_column: str
    render_model: bool
    url: str
    module_name: str
    api_class_name_pascal_case: str
    api_class_name_snake_case: str
    db_url: str
    templates_dir: str
    render_templates: bool


class ViewInspectorModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    view_name: str = Field(index=True)
    sql_name: str
    sql_hash: str
    date_created: datetime.datetime
    date_modified: datetime.datetime
