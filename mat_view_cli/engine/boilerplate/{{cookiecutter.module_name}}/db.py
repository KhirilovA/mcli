from fastapi import HTTPException
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import ProgrammingError
from {{cookiecutter.root_folder}}.utils import QueryBuiderItem, get_qb
from ufautils.status import HTTP_400_BAD_REQUEST


async def get_{{cookiecutter.api_class_name_snake_case}}(db, locale: str, qb: QueryBuiderItem, model):
    mq = get_qb(model, qb)
    q = mq.end()
    try:
        sql = q.statement.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True})

        data = (await db.session.execute(str(sql))).mappings().all()
    except ProgrammingError as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=f'Database Error, code: {e.code}'
        )
    return data, mq
