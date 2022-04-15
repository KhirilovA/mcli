import datetime
import hashlib
from typing import Optional
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


class ViewInspector:  # Render View Builder

    __get_mat_views = """
    select matviewname as view_name
    from pg_matviews
    where schemaname = :schema_name
    order by view_name;
    """

    def __init__(self,
                 db_url: str,
                 db_name: str,
                 sql_module: str,
                 sql_full_path: str
                 ):
        self._sql_dir = sql_module
        self._sql_full_path = sql_full_path
        self.__engine = create_engine(db_url)
        self.__db_name = db_name
        SQLModel.metadata.create_all(self.__engine)

    def delete_view(self, view_name: str):
        view_renderer: ViewRenderer = ViewRenderer(
            view_name,
        )
        view_renderer.delete_view()
        statement = delete(ViewInspectorModel).where(ViewInspectorModel.view_name == view_renderer.view_name)
        with self.__engine.begin() as session:
            session.execute(statement)

    def get_views(self, ):
        with self.__engine.begin() as session:
            return [r[0] for r in session.execute(
                text(self.__get_mat_views),
                {"schema_name": self.__db_name}
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

    def register_view(self,
                      view_name: str,
                      sql_name: str,
                      index_name: str,
                      index_col_name: str,
                      create_index: bool = False,
                      render_model: bool = False,
                      url: str = False,
                      api_class_name_pascal_case: str = "",
                      api_class_name_snake_case: str = "",
                      root_name: str = "",
                      schema_name: str = ""
                      ):
        view_renderer: ViewRenderer = ViewRenderer(
            view_name,
            sql_name,
            create_index,
            index_name,
            index_col_name,
            self._sql_dir
        )

        sql_hash = self.get_hash_md5(f"{self._sql_full_path}/{view_renderer.sql_name}")
        with self.__engine.begin() as session:
            statement = select(ViewInspectorModel).where(ViewInspectorModel.view_name == view_renderer.view_name)
            obj: ViewInspectorModel = session.execute(statement).first()
            if not obj:
                if view_renderer.view_name not in self.get_views():
                    view_renderer.create_view()
                else:
                    view_renderer.refresh_view()
                statement = insert(ViewInspectorModel).values(
                    view_name=view_renderer.view_name,
                    sql_name=view_renderer.sql_name,
                    sql_hash=self.get_hash_md5(f"{self._sql_full_path}/{view_renderer.sql_name}"),
                    date_created=datetime.datetime.now(),
                    date_modified=datetime.datetime.now()
                )

            else:
                if sql_hash != obj.sql_hash:
                    view_renderer.refresh_view()
                statement = (update(ViewInspectorModel)
                             .where(ViewInspectorModel.view_name == view_renderer.view_name)
                             .values(sql_name=view_renderer.sql_name,
                                     sql_hash=sql_hash,
                                     date_modified=datetime.datetime.now()
                                     ))
            session.execute(statement)
        if render_model:
            model_renderer = ModelRenderer(rendered_view=view_renderer,
                                           api_class_name_pascal_case=api_class_name_pascal_case,
                                           api_class_name_snake_case=api_class_name_snake_case,
                                           url=url,
                                           root_name=root_name,
                                           schema_name=schema_name
                                           )
            model_renderer.create_module()
