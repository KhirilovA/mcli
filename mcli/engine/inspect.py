import datetime
import hashlib
import importlib.resources
import json
import os
from pathlib import Path, PureWindowsPath
from sqlalchemy import text, create_engine, insert, update, delete
from sqlmodel import select, SQLModel
from mcli.engine.render_view import ViewRenderer
from mcli.engine.models import ConfigModel, ViewInspectorModel


class ViewInspector:
    __get_mat_views = """
    select matviewname as view_name
    from pg_matviews
    where schemaname = :schema_name
    order by view_name;
    """

    def __init__(self, config: ConfigModel):

        self.cfg = config
        self.__engine = create_engine(self.cfg.db_url)
        SQLModel.metadata.create_all(self.__engine)

    def recreate_views(self):
        statement = select(ViewInspectorModel)
        _prev_config = self.cfg
        with self.__engine.begin() as session:
            configs = [dict(r).get('config', {}) for r in session.execute(statement).fetchall()]
            for config in configs:
                self.cfg = ConfigModel(**json.loads(config))
                self.multiply_delete()
                self.multiply_register()
        self.cfg = _prev_config



    def get_views(self, ):
        with self.__engine.begin() as session:
            return [r[0] for r in session.execute(
                text(self.__get_mat_views),
                {"schema_name": self.cfg.db_schema}
            ).fetchall()]

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

    def multiply_funcer(self, func):

        files = {}

        path_ = Path(PureWindowsPath(self.cfg.sql_full_path + f"/{self.cfg.templates_dir}"))
        for (root, _, files_) in os.walk(path_, topdown=True):
            if files_:
                files[root] = files_

        for k, v in files.items():

            part = os.path.basename(os.path.normpath(k))
            module_part = f"{self.cfg.sql_module}.{self.cfg.templates_dir}"
            if part:
                module_part += f".{part}"

            for item in v:
                view_name = f"{self.cfg.view_name}_{part}_{item[:-4]}"
                print("FOUNDED VIEW:", view_name)
                args = {
                    "view_name": view_name,
                    "sql": importlib.resources.read_text(module_part, item),
                    "index": "",

                }
                if part:
                    path = PureWindowsPath(f"{self.cfg.sql_full_path}\\{self.cfg.templates_dir}\\{part}\\{item}")
                else:
                    path = PureWindowsPath(f"{self.cfg.sql_full_path}\\{self.cfg.templates_dir}\\{item}")
                func(args=args, sql_path=path, sql_name=item)

    def multiply_delete(self):
        return self.multiply_funcer(self.delete_view)

    def multiply_register(self):
        return self.multiply_funcer(self.register_view)

    def delete_view(self, args=None, sql_path=None, sql_name=None):
        view_renderer: ViewRenderer = ViewRenderer(
            config=self.cfg, args=args
        )
        view_renderer.delete_view()
        statement = delete(ViewInspectorModel).where(ViewInspectorModel.view_name == self.cfg.view_name)
        with self.__engine.begin() as session:
            session.execute(statement)

    def register_view(self, args=None, sql_path=None, sql_name=None):

        view_renderer: ViewRenderer = ViewRenderer(config=self.cfg, args=args)
        _sql_path = PureWindowsPath(f"{self.cfg.sql_full_path}\\{self.cfg.sql_name}") if not sql_path else sql_path
        _view_name = self.cfg.view_name if not args else args['view_name']
        _sql_name = self.cfg.sql_name if not sql_name else sql_name
        sql_hash = self.get_hash_md5(sql_path)
        with self.__engine.begin() as session:
            statement = select(ViewInspectorModel).where(ViewInspectorModel.view_name == _view_name)
            obj: ViewInspectorModel = session.execute(statement).first()
            if not obj:
                if _view_name not in self.get_views():
                    view_renderer.create_view()
                else:
                    view_renderer.refresh_view()
                statement = insert(ViewInspectorModel).values(
                    view_name=_view_name,
                    sql_name=_sql_name,
                    sql_hash=self.get_hash_md5(_sql_path),
                    date_created=datetime.datetime.now(),
                    date_modified=datetime.datetime.now(),
                    config=self.cfg.json()
                )

            else:
                if sql_hash != obj.sql_hash:
                    view_renderer.refresh_view()
                statement = (update(ViewInspectorModel)
                             .where(ViewInspectorModel.view_name == _view_name)
                             .values(sql_name=_sql_name,
                                     sql_hash=sql_hash,
                                     date_modified=datetime.datetime.now(),
                                     config=self.cfg.json()
                                     ))
            session.execute(statement)
