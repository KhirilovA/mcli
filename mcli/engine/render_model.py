import os
from jinja2 import Template
from typing import List
from sqlalchemy import inspect, create_engine
from mcli.engine.types import types
from cookiecutter.main import cookiecutter

__raw__types__ = types

from mcli.engine.models import ConfigModel


class ModelRenderer(object):
    __match__template__ = Template(
        """
match instance:
    {{data}}
"""  # noqa
    )
    __multiply_schemas__ = Template(
        """
class {{name}}DataItem(SQLModel, AdaptedModel, table=True):
    __tablename__ = "{{view_name}}"
    {{fields}}
    
class {{name}}Response(SQLModel, AdaptedModel):
    columns: list[str] = {{name}}DataItem.get_field_names()
    data: list[{{name}}DataItem]
"""  # noqa
    )

    def __init__(self, config: ConfigModel
                 ):
        self.cfg = config
        self.engine = create_engine(self.cfg.db_url)
        self.current__dir = os.path.dirname(__file__)
        # "view_names_linked": "KpiNewsletterWeek - mv_kpi_newsletter_plots_week"

    def create_module(self):
        cookiecutter(
            template=f"{self.current__dir}/boilerplate_multiply",
            no_input=True,
            extra_context={"module_name": self.cfg.module_name,
                           "root_folder": self.cfg.root_folder,
                           "api_class_name_pascal_case": self.cfg.api_class_name_pascal_case,
                           "url": self.cfg.url,
                           "api_class_name_snake_case": self.cfg.api_class_name_snake_case,
                           "view_name": self.cfg.view_name,
                           "fields": self.create_fields()}
        )

    def generate_multiply_linked_cls(self):
        _obj = ""
        _pascal_names = ""
        _snake_names = []
        for item in self.cfg.view_names_linked:
            _obj += self.__multiply_schemas__.render(
                name=item.pascal_cls_name,
                view_name=item.view_name,
                fields=self.create_fields(item.view_name)
            )
            _pascal_names += f"{item.pascal_cls_name}DataItem, {item.pascal_cls_name}Response"
            _snake_names.append(item.snake_cls_name)
        return _obj, _pascal_names, _snake_names

    def construct_match(self):
        _obj = ""
        for item in self.cfg.view_names_linked:
            _obj += \
f"""case {item.snake_cls_name}:
        model = {item.pascal_cls_name}Response
"""
        return _obj

    def create_multiply_module(self):
        schemas, pascal_names, _ = self.generate_multiply_linked_cls()
        kwargs = {
            "module_name": self.cfg.module_name,
            "root_folder": self.cfg.root_folder,
            "api_class_name_pascal_case": self.cfg.api_class_name_pascal_case,
            "url": self.cfg.url,
            "api_class_name_snake_case": self.cfg.api_class_name_snake_case,
            "multiply_schemas": schemas,
            "type_alias_name": self.cfg.type_alias,
            "literal_instance_list": pascal_names,
            "match_block": self.construct_match()
        }
        cookiecutter(
            template=f"{self.current__dir}/boilerplate_multiply",
            no_input=True,
            extra_context=kwargs
        )

    def create_fields(self, view_name: str = None) -> str:
        inspector = inspect(self.engine)
        if not view_name:
            view_name = self.cfg.view_name
        columns_table = self.__clean_str_types__(inspector.get_columns(view_name, self.cfg.db_schema))
        return self.__render_field_types__(columns_table)

    @staticmethod
    def __render_field_types__(columns_table: dict):
        fields_template = ""
        first = True
        for name, type_ in columns_table.items():
            if first:
                fields_template += f"    {name}:{type_} = Field(default=None, primary_key=True)\n"
                first = False
                continue
            fields_template += f"    {name}: {type_}\n"

        return fields_template

    @staticmethod
    def __clean_str_types__(columns_table: List[dict]) -> dict:
        clean_str_types = {}
        for row in columns_table:
            try:
                if 'VARCHAR' in str(row['type']):
                    clean_str_types[row["name"]] = __raw__types__['VARCHAR']
                else:
                    clean_str_types[row["name"]] = __raw__types__[str(row['type'])]
            except KeyError:
                clean_str_types[row['name']] = 'Any'
        return clean_str_types
