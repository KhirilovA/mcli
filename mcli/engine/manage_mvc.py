import os
from typing import List

from cookiecutter.main import cookiecutter
from jinja2 import Template
from sqlalchemy import create_engine, inspect

from mcli import ConfigModel
from mcli.engine.types import types

__raw__types__ = types


class MVCTemplateManager:
    models_imports_template = Template("""{{imports}}""")
    controller_instances_map_template = Template("""
    instances_map = {
        {{instances_map}}
    }
    """)
    match_instances_template = Template("""{{match_block}}""")
    models_template = Template("""{{models_template}}""")

    def __init__(self, config: ConfigModel):
        self.cfg = config
        self.engine = create_engine(self.cfg.db_url)
        self.links = self.cfg.view_names_linked
        self.current__dir = os.path.dirname(__file__)

    def create_fields(self, view_name: str = None) -> str:
        inspector = inspect(self.engine)
        columns_table = self.__clean_str_types__(inspector.get_columns(view_name, self.cfg.db_schema))
        return self.__render_field_types__(columns_table)

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

    @staticmethod
    def __render_field_types__(columns_table: dict):
        fields_template = ""
        first = True
        for name, type_ in columns_table.items():
            if first:
                fields_template += f"    {name}: Optional[{type_}] = Field(default=None, primary_key=True)\n"
                first = False
                continue
            fields_template += f"    {name}: Optional[{type_}]\n"

        return fields_template

    def get_cutter_args(self):
        _pascal_names = ""
        _instances_map = ""
        _raw_instances = ""
        _match_template = Template("""match instance:{{instances}}""")
        _m_instances = """"""
        models_result = """"""
        _models_template = Template("""
class {{name}}DataItem(SQLModel, AdaptedModel, table=True):
    __tablename__ = "{{view_name}}"
{{fields}}
""")
        _responses = ""
        _response_template = Template("""class {{name}}Response({{name}}DataItem):
    ...""")
        _fields = ""
        _field_template = Template("""    {{instance}} = {{name}}DataItem.get_field_names()""")
        _options = ""
        _option_template = Template("""    {{instance}} = InstanceOption(
        name={{name}}Instances.{{instance}},
        fields={{name}}Fields().{{instance}},
        enable_filtering=True,
        enable_aggregations=True
    )""")
        _filters = ""
        _filter_template = Template("    {{instance}} = {}")
        _response_sets = ""
        _response_set_template = Template("""{{instance}}: Optional[{{name}}Response]""")
        for index, item in enumerate(self.links):
            _instances_map += f"\n        {self.cfg.pascal_name}Instances.{item.instance_name}:{item.pascal_cls_name}DataItem"
            if index != len(self.links) - 1:
                _instances_map += ","
            _pascal_names += f"\n{item.pascal_cls_name}DataItem"
            _m_instances += f"""\n            case {self.cfg.pascal_name}Instances.{item.instance_name}:
                           ..."""
            if self.links[index] != self.links[-1]:
                _pascal_names += ",\n"
            models_result += _models_template.render(name=item.pascal_cls_name,
                                                     view_name=item.view_name,
                                                     fields=self.create_fields(item.view_name))
            _raw_instances += f"\n{item.instance_name}: str = auto()"
            _responses += f"\n{_response_template.render(name=item.pascal_cls_name)}"
            _fields += f"\n{_field_template.render(name=item.pascal_cls_name, instance=item.instance_name)}"
            _options += f"\n{_option_template.render(name=self.cfg.pascal_name, instance=item.instance_name)}"
            _filters += f"\n{_filter_template.render(instance=item.instance_name)}"
            _response_sets += f"\n{_response_set_template.render(name=item.pascal_cls_name, instance=item.instance_name)}"

        return {
            "model_imports": _pascal_names,
            "instances_map": _instances_map,
            "match_block": _match_template.render(instances=_m_instances),
            "models_result": models_result,
            "instances": _raw_instances,
            "responses": _responses,
            "fields": _fields,
            "options": _options,
            "filters": _filters,
            "response_sets": _response_sets
        }

    def create_template(self):
        conf = self.get_cutter_args()
        cookiecutter(
            template=f"{self.current__dir}/boilerplate_mvc",
            no_input=True,
            extra_context={"root_folder": self.cfg.root_folder,
                           "module_name": self.cfg.module_name,
                           "pascal_name": self.cfg.pascal_name,
                           "model_imports": self.models_imports_template.render(
                               imports=conf.get('model_imports')
                           ),
                           "controller_instances_map": self.controller_instances_map_template.render(
                               instances_map=conf.get("instances_map")
                           ),
                           "match_instances_template": self.match_instances_template.render(
                               match_block=conf.get("match_block")
                           ),
                           "models_template": self.models_template.render(
                               models_template=conf.get("models_result")
                           ),
                           "instances": conf.get("instances"),
                           "responses": conf.get("responses"),
                           "fields": conf.get("fields"),
                           "options": conf.get("options"),
                           "filters": conf.get("filters"),
                           "response_sets": conf.get("response_sets"),
                           "url": self.cfg.url
                           }
        )
