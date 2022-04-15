from datetime import date
from pydantic import conint, confloat
from sqlmodel import Field
from {{cookiecutter.root_folder}}.utils import AdaptedModel


class {{cookiecutter.api_class_name_pascal_case}}DataItem(AdaptedModel, table=True):
    __tablename__ = "{{cookiecutter.view_name}}"
    {{fields}}

class {{cookiecutter.api_class_name_pascal_case}}rResponse(AdaptedModel):
    columns: list[str] = {{cookiecutter.api_class_name_pascal_case}}DataItem.get_field_names()
    data: list[{{cookiecutter.api_class_name_pascal_case}}Item]
