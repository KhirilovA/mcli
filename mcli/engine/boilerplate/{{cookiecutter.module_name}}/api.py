from typing import Union
from fastapi import APIRouter
from fastapi_utils.cbv import cbv


import {{cookiecutter.root_folder}}.{{cookiecutter.module_name}}.db as db_funcs
from {{cookiecutter.root_folder}}.{{cookiecutter.module_name}}.schemas import {{cookiecutter.api_class_name_pascal_case}}Response, {{cookiecutter.api_class_name_pascal_case}}DataItem
from {{cookiecutter.root_folder}}.utils import APIView, QueryBuiderRequest, QueryBuilderCountResponse

url = "{{cookiecutter.url}}"

router = APIRouter()


@cbv(router)
class {{cookiecutter.api_class_name_pascal_case}}(APIView):

    @router.post(url, response_model=Union[{{cookiecutter.api_class_name_pascal_case}}Response | QueryBuilderCountResponse])
    async def get_{{cookiecutter.api_class_name_snake_case}}(self, qb: QueryBuiderRequest):
        data, mq = await db_funcs.get_{{cookiecutter.api_class_name_snake_case}}(self.db, self.userinfo.locale, qb.qb, {{cookiecutter.api_class_name_pascal_case}}DataItem)
        # make magic here
        result = {{cookiecutter.api_class_name_pascal_case}}Response(data=data)
        return result

