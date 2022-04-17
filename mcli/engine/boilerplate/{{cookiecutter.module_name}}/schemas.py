from sqlmodel import Field, SQLModel
from mcli.engine.types import *
from {{cookiecutter.root_folder}}.utils import AdaptedModel


class {{cookiecutter.api_class_name_pascal_case}}DataItem(SQLModel, AdaptedModel, table=True):
    __tablename__ = "{{cookiecutter.view_name}}"
{{cookiecutter.fields}}


class {{cookiecutter.api_class_name_pascal_case}}Response(SQLModel, AdaptedModel):
    columns: list[str] = {{cookiecutter.api_class_name_pascal_case}}DataItem.get_field_names()
    data: list[{{cookiecutter.api_class_name_pascal_case}}DataItem]
