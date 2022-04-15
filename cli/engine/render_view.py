import importlib.resources
import logging
from string import Template
from sqlalchemy import create_engine


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
                 view_name: str,
                 sql_name: str = None,
                 create_index: bool = False,
                 index_name: str = None,
                 index_col_name: str = None,
                 sql_dir:str = None,
                 db_url:str = ""):
        self.engine = create_engine(db_url)
        self.create_index = create_index
        self.view_name = view_name
        self.sql_name = sql_name
        self.sql = None
        if self.sql_name:
            self.sql = importlib.resources.read_text(sql_dir, self.sql_name)
        self._index_name = index_name
        self._col_name = index_col_name
        lvred_name = self.view_name.lower()
        self.view_name_frmt = f"mv_{lvred_name}" if "mv_" not in lvred_name else lvred_name

    def create_view(self):
        args = {
            "view_name": self.view_name_frmt,
            "sql": self.sql,
            "index": ""

        }
        if self.create_index:
            args['index'] = self.__index_template__.substitute({"index_name": self._index_name,
                                                                "col_name": self._col_name})
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
            session.execute(f"DROP MATERIALIZED VIEW IF EXISTS {self.view_name_frmt}")

    def __str__(self):
        return self.view_name
