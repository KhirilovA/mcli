from typing import Union, Literal, TypeAlias
from fastapi import APIRouter
from fastapi_utils.cbv import cbv
from {{cookiecutter.root_folder}}.utils import APIView, QueryBuiderRequest, QueryBuilderCountResponse, get_universal_data
from {{cookiecutter.root_folder}}.{{cookiecutter.module_name}}.schemas import (
    {{cookiecutter.response_model_classes}}
)

url = "{{cookiecutter.url}}"

router = APIRouter()

{{cookiecutter.type_alias_name}}:TypeAlias = Union[{{cookiecutter.response_model_classes}}QueryBuilderCountResponse]

@cbv(router)
class {{cookiecutter.api_class_name_pascal_case}}(APIView):

    @router.post(url, response_model={{cookiecutter.type_alias_name}})
    async def get_{{cookiecutter.api_class_name_snake_case}}(self, instance: Literal[{{cookiecutter.literal_instance_list}}], qb: QueryBuiderRequest):
        match instance:{{cookiecutter.match_block}}
        data, mq = await get_universal_data(self.db, self.userinfo.locale, qb.qb, model)
        if qb.qb.count:
            return QueryBuilderCountResponse(count=data[0]['count_1'])
        result = model(data=data)
        return result

