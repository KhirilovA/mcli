from typing import Optional

from mcli.engine.interfaces.api_models import CountResponse
from {{cookiecutter.root_folder}}.{{cookiecutter.module_name}}.aggregators import {{cookiecutter.pascal_name}}Aggregator
from {{cookiecutter.root_folder}}.{{cookiecutter.module_name}}.models import (
    {{cookiecutter.model_imports}}
)
from mcli.engine.interfaces.api_models import MultiplyQueryBuilderRequest
from mcli.engine.interfaces.controller import BaseController
from {{cookiecutter.root_folder}}.{{cookiecutter.module_name}}.api_models import (
    {{cookiecutter.pascal_name}}Instances,
    {{cookiecutter.pascal_name}}InstancesOptions
)
from {{cookiecutter.root_folder}}.utils import QueryBuilderItem, get_universal_data


class {{cookiecutter.pascal_name}}Controller(BaseController):
    {{cookiecutter.controller_instances_map}}
    def __init__(self,
                 qb: MultiplyQueryBuilderRequest,
                 aggregator: Optional[{{cookiecutter.pascal_name}}Aggregator],
                 db,
                 userinfo
                 ):

        super().__init__(qb, aggregator, db, userinfo)

        self.aggregator = aggregator
        self.qb = qb
        self.options = {{cookiecutter.pascal_name}}InstancesOptions().dict()

    async def execute(self, instance: str, project: list, *args, **kwargs):
        model = self.instances_map.get(instance)
        query = None
        qb_request = QueryBuilderItem(project=self.qb.qb.project.get(instance, []),
                                      filter=self.qb.qb.filter.get(instance, {}),
                                      sort=self.qb.qb.sort.get(instance, []),
                                      skip=self.qb.qb.skip.get(instance, 0),
                                      limit=self.qb.qb.limit.get(instance, 0),
                                      count=self.qb.qb.count.get(instance, 0))
        {{cookiecutter.match_instances_template}}

        if not self.options[instance]['enable_aggregations']:
            query = None
        if not self.options[instance]['enable_filtering']:
            qb_request.filter = []
        data, mq = await get_universal_data(self.db, self.userinfo.locale, qb_request, model, query)
        if qb_request.count:
            return CountResponse(name=instance, data=[
                {"id": 0, "count": data[0]['count_1']}
            ])

        return [self.instances_map[instance](**item) for item in data]
