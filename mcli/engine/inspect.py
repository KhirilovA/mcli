import datetime
import hashlib
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import text, create_engine, insert, update, delete
from sqlmodel import SQLModel, Field, select
from mcli.engine.render_view import ViewRenderer
from mcli.engine.render_model import ModelRenderer


class ViewInspectorModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    view_name: str = Field(index=True)
    sql_name: str
    sql_hash: str
    date_created: datetime.datetime
    date_modified: datetime.datetime


class ConfigModel(BaseModel):
    db_name: str
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_schema: str
    sql_module: str
    sql_full_path: str
    sql_name: str
    root_folder: str
    view_name: str
    create_index: bool
    index_name: str
    index_column: str
    render_model: bool
    url: str
    module_name: str
    api_class_name_pascal_case: str
    api_class_name_snake_case: str
    db_url: str


class ViewInspector:

    __get_mat_views = """
    select matviewname as view_name
    from pg_matviews
    where schemaname = :schema_name
    order by view_name;
    """

    def __init__(self, config: ConfigModel):

        self.cfg = config
        # self.db_url = f"postgresql+psycopg2://{self.cfg.db_user}:{self.cfg.db_password}" \
        #               f"@{self.cfg.db_host}:{self.cfg.db_port}/{self.cfg.db_name}"
        self.__engine = create_engine(self.cfg.db_url)

    def delete_view(self, view_name: str):
        view_renderer: ViewRenderer = ViewRenderer(
            config=self.cfg
        )
        view_renderer.delete_view()
        statement = delete(ViewInspectorModel).where(ViewInspectorModel.view_name == self.cfg.view_name)
        with self.__engine.begin() as session:
            session.execute(statement)

    def get_views(self, ):
        with self.__engine.begin() as session:
            return [r[0] for r in session.execute(
                text(self.__get_mat_views),
                {"schema_name": self.cfg.db_schema}
            ).fetchall()]

    @staticmethod
    def get_hash_md5(filepath: str):
        """Stolen from https://badeud.ru/post/2/. Requires verification."""
        with open(filepath, 'rb') as f:
            m = hashlib.md5()
            while True:
                data = f.read(8192)
                if not data:
                    break
                m.update(data)
            return m.hexdigest()

    def register_view(self):
        view_renderer: ViewRenderer = ViewRenderer(config=self.cfg)

        sql_hash = self.get_hash_md5(f"{self.cfg.sql_full_path}/{self.cfg.view_name}")
        with self.__engine.begin() as session:
            statement = select(ViewInspectorModel).where(ViewInspectorModel.view_name == self.cfg.view_name)
            obj: ViewInspectorModel = session.execute(statement).first()
            if not obj:
                if self.cfg.view_name not in self.get_views():
                    view_renderer.create_view()
                else:
                    view_renderer.refresh_view()
                statement = insert(ViewInspectorModel).values(
                    view_name=self.cfg.view_name,
                    sql_name=self.cfg.sql_name,
                    sql_hash=self.get_hash_md5(f"{self.cfg.sql_full_path}/{self.cfg.view_name}"),
                    date_created=datetime.datetime.now(),
                    date_modified=datetime.datetime.now()
                )

            else:
                if sql_hash != obj.sql_hash:
                    view_renderer.refresh_view()
                statement = (update(ViewInspectorModel)
                             .where(ViewInspectorModel.view_name == self.cfg.view_name)
                             .values(sql_name=self.cfg.sql_name,
                                     sql_hash=sql_hash,
                                     date_modified=datetime.datetime.now()
                                     ))
            session.execute(statement)

