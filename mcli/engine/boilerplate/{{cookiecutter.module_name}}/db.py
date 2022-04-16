from fastapi import HTTPException
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import ProgrammingError
from mcli.engine.utils import QueryBuiderItem, get_qb


async def get_{{cookiecutter.api_class_name_snake_case}}(db, locale: str, qb: QueryBuiderItem, model):
    mq = get_qb(model, qb)
    try:
        sql = mq.statement.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True})
        data = (await db.session.execute(str(sql))).mappings().all()
    except ProgrammingError as e:
        raise HTTPException(
            status_code=400, detail=f'Database Error, code: {e.code}'
        )
    return data, mq
