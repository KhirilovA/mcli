from fastapi import APIRouter
from fastapi_utils.cbv import cbv
from {{cookiecutter.root_folder}}.{{cookiecutter.module_name}}.aggregators import {{cookiecutter.pascal_name}}Aggregator
from {{cookiecutter.root_folder}}.{{cookiecutter.module_name}}.api_models import (
    {{cookiecutter.pascal_name}}APIModelResponse,
    {{cookiecutter.pascal_name}}QBRequest
)
from {{cookiecutter.root_folder}}.{{cookiecutter.module_name}}.controller import {{cookiecutter.pascal_name}}Controller
from {{cookiecutter.root_folder}}.utils import APIView

router = APIRouter()
url = "{{cookiecutter.url}}"


@cbv(router)
class {{cookiecutter.pascal_name}}(APIView):

    @router.post(url,
                 response_model={{cookiecutter.pascal_name}}APIModelResponse,
                 response_model_exclude_none=True)
    async def get_{{cookiecutter.snake_name}}(self, qb: {{cookiecutter.pascal_name}}QBRequest):
        controller = {{cookiecutter.pascal_name}}Controller(
            qb=qb,
            aggregator={{cookiecutter.pascal_name}}Aggregator(),
            db=self.db,
            userinfo=self.userinfo
        )
        response = {{cookiecutter.pascal_name}}APIModelResponse()

        for item in qb.qb.project:
            raw_data = await controller.execute(
                instance=item,
                project=qb.qb.project.get(item, []))
            response.set_response(item, raw_data)

        return response
