from typing import Optional
from fastapi_utils.enums import StrEnum # noqa
from mcli.engine.interfaces.aggregators import BaseAggregator
from mcli.engine.interfaces.api_models import MultiplyQueryBuilderRequest


class BaseController:
    instances_map = {}
    response_map = {}

    def __init__(self, qb: MultiplyQueryBuilderRequest,
                 aggregator: Optional[BaseAggregator],
                 db,
                 userinfo):
        self.qb = qb
        self.db = db
        self.userinfo = userinfo
        self.project = self.qb.qb.project
        self.filter = self.qb.qb.filter
        self.sort = self.qb.qb.sort
        self.limit = self.qb.qb.limit
        self.count = self.qb.qb.count
        self.skip = self.qb.qb.skip
        self.aggregator = aggregator

    def __call__(self, instance: StrEnum, *args, **kwargs):
        raise NotImplemented
