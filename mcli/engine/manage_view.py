import hashlib
import datetime
from pathlib import Path

from jinja2 import Template
from sqlalchemy import create_engine, select, insert, update

from mcli import ConfigModel
from mcli.engine.models import ViewInspectorModel


class ViewManager:
    __create_template = Template("""
    DROP MATERIALIZED VIEW IF EXISTS {{view_name}} CASCADE;
    CREATE MATERIALIZED VIEW {{view_name}} AS (
    {{sql}}
    );
    """)
    __delete_template = Template("""
    DROP MATERIALIZED VIEW IF EXISTS {{view_name}} CASCADE;
    """)

    def __init__(self, config: ConfigModel):
        self.cfg = config
        self.engine = create_engine(self.cfg.db_url)
        self.links = self.cfg.view_names_linked

    @staticmethod
    def get_hash_md5(filepath):
        """Stolen from https://badeud.ru/post/2/. Requires verification."""
        with open(Path(filepath), 'rb') as f:
            m = hashlib.md5()
            while True:
                data = f.read(8192)
                if not data:
                    break
                m.update(data)
            return m.hexdigest()

    def create_views(self):
        with self.engine.begin() as session:
            for item in self.links:
                print("FOUNDED VIEW:", item.view_name)
                with open(item.sql_path, "r") as file:
                    sql = file.read()
                session.execute(self.__create_template.render(
                    view_name=item.view_name,
                    sql=sql
                ))
                statement = select(ViewInspectorModel).where(ViewInspectorModel.view_name == item.view_name)
                obj: ViewInspectorModel = session.execute(statement).first()
                to_save = self.cfg.dict()
                to_save.pop("db_url")
                if not obj:
                    statement = insert(ViewInspectorModel).values(
                        view_name=item.view_name,
                        sql_hash=self.get_hash_md5(item.sql_path),
                        date_created=datetime.datetime.now(),
                        date_modified=datetime.datetime.now(),
                        config=to_save
                    )

                else:
                    statement = (update(ViewInspectorModel)
                                 .where(ViewInspectorModel.view_name == item.view_name)
                                 .values(
                                         sql_hash=self.get_hash_md5(item.sql_path),
                                         date_modified=datetime.datetime.now(),
                                         config=to_save
                                         ))
                session.execute(statement)

