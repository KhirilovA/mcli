from enum import auto
from typing import Optional, Any

from pydantic import BaseModel, ValidationError
from fastapi_utils.enums import StrEnum

from {{cookiecutter.root_folder}}.{{cookiecutter.module_name}}.models import (
    {{cookiecutter.model_imports}}
)


from mcli.engine.interfaces.api_models import (
    InstanceOption,
    MultiplyQueryBuilderItem,
    MultiplyQueryBuilderRequest,
    FlatChartMixin,
    StatMixin,
    PostAggregate)


class {{cookiecutter.pascal_name}}Instances(StrEnum):
    {{cookiecutter.instances}}
{{cookiecutter.responses}}
class  {{cookiecutter.pascal_name}}Fields(BaseModel):
    {{cookiecutter.fields}}


class {{cookiecutter.pascal_name}}InstancesOptions(BaseModel):
    """
        Fields and Permissions for Instances
    """
    {{cookiecutter.options}}


class {{cookiecutter.pascal_name}}FiltersModel(BaseModel):
    {{cookiecutter.filters}}


class {{cookiecutter.pascal_name}}SortModel({{cookiecutter.pascal_name}}Fields):

    @property
    def sort(self):
        sort = {}
        for k, v in {{cookiecutter.pascal_name}}SortModel().dict().items():
            sort[k] = [f"{x}+" for x in v]
        return sort


class {{cookiecutter.pascal_name}}QBItem(MultiplyQueryBuilderItem):
    project = {{cookiecutter.pascal_name}}Fields().dict()


class {{cookiecutter.pascal_name}}QBRequest(MultiplyQueryBuilderRequest):
    qb: {{cookiecutter.pascal_name}}QBItem


class {{cookiecutter.pascal_name}}APIModelResponse(BaseModel):
    {{cookiecutter.response_sets}}

    def set_response(self, key, value):
        """set_raw_data"""
        mapping = {
            {{cookiecutter.set_response_mapping}}
        }
        self.__dict__[key] = mapping.get(key)(data=value)
        return self
