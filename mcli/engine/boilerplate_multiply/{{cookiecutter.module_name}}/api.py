from typing import Union
from fastapi import APIRouter
from fastapi_utils.cbv import cbv
from {{cookiecutter.root_folder}}.utils import APIView, QueryBuiderRequest, QueryBuilderCountResponse, get_universal_data
from {{cookiecutter.root_folder}}.{{cookiecutter.module_name}}.schemas import (
    {{cookiecutter.model_classes}}
)

url = "{{cookiecutter.url}}"

router = APIRouter()

@cbv(router)
class {{cookiecutter.api_class_name_pascal_case}}(APIView):

    {{cookiecutter.api_body}}

