import os
from typing import List
from sqlalchemy import inspect, create_engine
from mcli.engine.types import types
from cookiecutter.main import cookiecutter

__raw__types__ = types

from mcli.engine.models import ConfigModel


class ModelRenderer(object):

    def __init__(self, config: ConfigModel
                 ):
        self.cfg = config
        self.engine = create_engine(self.cfg.db_url)

    def create_module(self):
        current__dir = os.path.dirname(__file__)
        cookiecutter(
            template=f"{current__dir}/boilerplate",
            no_input=True,
            extra_context={"module_name": self.cfg.module_name,
                           "root_folder": self.cfg.root_folder,
                           "api_class_name_pascal_case": self.cfg.api_class_name_pascal_case,
                           "url": self.cfg.url,
                           "api_class_name_snake_case": self.cfg.api_class_name_snake_case,
                           "view_name": self.cfg.view_name,
                           "fields": self.create_fields()}
        )

    def create_fields(self) -> str:
        inspector = inspect(self.engine)
        columns_table = self.__clean_str_types__(inspector.get_columns(self.cfg.view_name, self.cfg.db_schema))
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
