from typing import Optional, Any, Literal

from pydantic import BaseModel

from mcli.engine.utils import QueryBuilderItem, AdaptedModel


class MultiplyQueryBuilderItem(QueryBuilderItem):
    project: dict = {}
    filter: dict = {}
    sort: dict = {}
    skip: dict = {}
    count: dict = {}
    limit: dict = {}


class MultiplyQueryBuilderRequest(AdaptedModel):
    qb: MultiplyQueryBuilderItem


class BaseFormatter(BaseModel):

    def get_frmt(self, *args, **kwargs):
        raise NotImplemented


class DateChartItem(BaseModel):
    """base convenient response block for date-chart,
    should normally be padded with response fields"""
    id: int = 0


class DateChartResponse(BaseFormatter):
    """convenient response structure for date-chart
    good parent for other response-models
    {
      "name": "9999-2-20-OSTERBAD19BBSV",
      "data": [
        {
          "transaction_net": 74.19,
          "date": "2021-26",
          "count": 2
        },
        {
          "transaction_net": 27.64,
          "date": "2021-27",
          "count": 1
        },
        {
          "transaction_net": 21.8,
          "date": "2021-29",
          "count": 1
        }
      ]
}
    """
    name: str = ""
    data: list[DateChartItem] = [DateChartItem()]

    def get_frmt(self, core_field: str = "id", model=None) -> list:
        if not self.data:
            self.data = [model()]
        basic_names = set([getattr(item, core_field) for item in self.data])
        basic = {name: {"name": name,
                        "data": []
                        }
                 for name in basic_names}
        for index, item in enumerate(self.data):
            basic[getattr(item, core_field)]['data'].append(
                item.dict(exclude={core_field}) | {"id": len(basic[getattr(item, core_field)]['data'])}
            )

        return list(basic.values())


class FlatChartColumnItem(BaseModel):
    categories: list[str]
    data: list[float]


class FlatChartDataItem(BaseModel):
    name: str
    value: Any


class BarChartColumnItem(BaseModel):
    name: str
    data: Optional[list[Any]]


class BarChart(BaseFormatter):
    """
    {
      "columns": ["A", "B", "C"],
      "data": [
        {
          "name": "current",
          "data": [1522, 4683, 9552]
        },
        {
          "name": "prev",
          "data": [1163, 7550, 14218]
        }
      ],
      "timeframes": [
        {
          "name": "current",
          "data": ["2021-03-05", "2022-03-05"]
        },
        {
          "name": "prev",
          "data": ["2020-03-05", "2021-03-05"]
        }
      ]
    }
    """
    columns: Optional[list[str]]
    data: Optional[BarChartColumnItem]
    timeframes: Optional[BarChartColumnItem]

    def get_frmt(self, raw_data: Optional[list],
                 column_root_key: str = "",
                 data_root_name: str = "",
                 data_root_key: str = "",
                 timeframes: list = None,
                 ):
        self.columns = [item.dict().get(column_root_key) for item in raw_data]
        self.data = BarChartColumnItem(
            name=data_root_name,
            data=[item.dict().get(data_root_key) for item in raw_data]
        )
        if timeframes:
            self.timeframes = BarChartColumnItem(
                name=data_root_name,
                data=timeframes
            )
        return self


class GroupBarChart(BaseFormatter):
    columns: Optional[list[str]] = []
    data: Optional[list[BarChartColumnItem]] = []
    timeframes: Optional[list[BarChartColumnItem]] = []

    def get_frmt(self, bar_charts: list[BarChart]):
        for chart in bar_charts:
            self.columns.extend(chart.columns)
            self.data.append(chart.data)
            self.timeframes.append(chart.timeframes)
        self.columns = list(set(self.columns))
        return self


class FlatChartMixin(BaseFormatter):
    """
      categories: ["one", "two"]
      data: ["one_value", "two_value"]

    """
    categories: Optional[list[str]]
    data: Optional[list[Any]]

    def get_frmt(self, raw_data: Optional[list],
                 category_key: str = "",
                 value_key: str = ""):
        self.categories = []
        self.data = []
        if raw_data:
            for item in raw_data:
                dicted_item = item.dict()
                self.categories.append(dicted_item.pop(category_key, ""))
                self.data.append(dicted_item.pop(value_key, ""))
        return self


class StatItem(BaseModel):
    name: str
    value: float | int


class PostAggregate(BaseModel):
    field_name: str
    func: Literal["average", "sum", "count"]
    args: Optional[tuple]


class StatMixin(BaseFormatter):
    data: Optional[list[StatItem]]

    @staticmethod
    def average(data: list[int | float], *args) -> float:
        if "rounded" in args:
            return round(sum(data) / len(data), 2)
        return sum(data) / len(data)

    @staticmethod
    def sum(data: list[int | float], *args) -> float:
        if "rounded" in args:
            return round(sum(data), 2)
        return sum(data)

    @staticmethod
    def count(data: list[int | float | str], *args) -> int:
        return len(data)

    def get_frmt(self,
                 raw_data: Optional[list[BaseModel]],
                 p_aggregates: list[PostAggregate],
                 rename_map: dict
                 ):
        self.data = []
        for aggregate in p_aggregates:
            self.data.append(
                StatItem(
                    name=rename_map.get(aggregate.field_name, aggregate.field_name),
                    value=getattr(self, aggregate.func)(
                        [item.dict().get(aggregate.field_name) for item in raw_data],
                        *(aggregate.args if aggregate.args else (None,))
                    )
                )
            )
        return self


class InstanceOption(BaseModel):
    name: str
    fields: list[str]
    enable_filtering: bool = True
    enable_aggregations: bool = False


class CountItem(DateChartItem):
    count: int


class CountResponse(DateChartResponse):
    data: list[CountItem]
