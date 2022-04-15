from typing import List
from sqlalchemy import inspect
from mat_view_cli.engine.render_view import ViewRenderer
from mat_view_cli.engine.types import types
from cookiecutter.main import cookiecutter

__raw__types__ = types


class ModelRenderer(object):

    def __init__(self,
                 rendered_view: ViewRenderer,
                 schema_name: str,
                 root_name: str,
                 api_class_name_pascal_case: str,
                 api_class_name_snake_case: str,
                 url: str
                 ):
        self._render_obj = rendered_view
        self.api_pascal = api_class_name_pascal_case
        self.api_snake = api_class_name_snake_case
        self.root = root_name
        self.url = url
        self.engine = self._render_obj.engine
        self._dir_name = str(self._render_obj).replace("_", "").replace("-", "")
        self.schema_name = schema_name

    def create_module(self):
        cookiecutter(
            template="cli/engine/boilerplate",
            no_input=True,
            extra_context={"module_name": self._dir_name,
                           "root_folder": self.root,
                           "api_class_name_pascal_case": self.api_pascal,
                           "url": self.url,
                           "api_class_name_snake_case": self.api_snake,
                           "view_name": self._render_obj.view_name_frmt,
                           "fields": self.create_fields()}
        )

    def create_fields(self) -> str:
        inspector = inspect(self.engine)
        columns_table = self.__clean_str_types__(inspector.get_columns(str(self._render_obj), self.schema_name))
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
