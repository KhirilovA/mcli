import importlib.resources
import logging
import os
from pathlib import PureWindowsPath, Path
from string import Template
from sqlalchemy import create_engine
from mcli.engine.models import ConfigModel


class ViewRenderer:
    __create_template = Template("""
CREATE MATERIALIZED VIEW $view_name AS (
$sql
);
$index

    """)
    __index_template__ = Template("CREATE UNIQUE INDEX $index_name ON $view_name($col_name);")
    __types_template__ = Template("""
SELECT column_name, data_type FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = TABLE_NAME
""")

    def __init__(self,
                 config: ConfigModel):
        self.cfg = config
        self.engine = create_engine(self.cfg.db_url)

    def create_plot_view(self):
        files = {}

        path_ = Path(PureWindowsPath(self.cfg.sql_full_path + f"/{self.cfg.templates_dir}"))
        for (root, _, files_) in os.walk(path_, topdown=True):
            files[root] = files_

        for k, v in files.items():

            part = str(Path(k)).split("/")[-1]
            module_part = f"{self.cfg.sql_module}.{self.cfg.templates_dir}"
            if part:
                module_part += f".{part}"
            for item in v:
                view_name = f"{self.cfg.view_name}_{part}_{item[:-4]}"
                args = {
                    "view_name": view_name,
                    "sql": importlib.resources.read_text(module_part, item),
                    "index": ""
                }
                print(args)
                #self.create_view(args=args)

    def create_view(self, args=None):
        if args is None:
            args = {
                "view_name": self.cfg.view_name,
                "sql": importlib.resources.read_text(self.cfg.sql_module, self.cfg.sql_name),
                "index": ""
            }
        if self.cfg.create_index:
            args['index'] = self.__index_template__.substitute({"index_name": self.cfg.index_name,
                                                                "col_name": self.cfg.index_column,
                                                                "view_name": self.cfg.view_name})
        try:
            assert all(args.values())
        except AssertionError as e:
            logging.error(msg=f"Attribute not set.{e.__repr__()}")
            raise Exception(f"Attributes not set: {','.join(args.items())}")
        with self.engine.begin() as session:
            session.execute(self.__create_template.substitute(**args))

    def refresh_view(self):
        self.delete_view()
        self.create_view()

    def delete_view(self):
        with self.engine.begin() as session:
            session.execute(f"DROP MATERIALIZED VIEW IF EXISTS {self.cfg.view_name}")

    def __str__(self):
        return self.cfg.view_name
