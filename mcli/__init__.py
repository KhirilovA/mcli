from mcli.engine.inspect import ViewInspector
from pyfiglet import Figlet

if __name__ == '__main__':
    f = Figlet(font='slant')
    print(f.renderText('QBCLI'))
    args_help = {
        "db_name": "? Name of database: ",
        "db_host": "? Host of database conn: ",
        "db_port": "? Port of database conn: ",
        "db_user": "? Username: ",
        "db_password": "? Password: ",
        "db_schema": "? Name of DB schema: ",
        "sql_module": "? Dotted name of sql-package: (ex: bb.sql) ",
        "sql_full_path": "? Full path to sql-package: ",
        "sql_name": "? Name of sql-file? ",
        "root_folder": "? Full path to Root Folder: ",
        "view_name": "? Name of materialized view: ",
        "create_index": "Need to create an index? [y,n] ",
        "index_name": "? Index name: ",
        "index_column": "? Columns for index: (ex: id,name,surname) ",
        "render_model": "Need to create endpoint boilerplate? [y/n] ",
        "url": "? URL of endpoint: ",
        "module_name": "kpi_newsletter",
        "api_class_name_pascal_case": "? Name of cls in Pascal Case: ",
        "api_class_name_snake_case": "? Name of cls in Snake Case: ",

    }
    args_values = {k: None for k, v in args_help.items()}

    for k, v in args_help.items():
        match k:

            case "db_port":
                args_values[k] = int(input(v))
            case "create_index", "render_model":
                args_values[k] = True if input(v).lower().strip() != "n" else False
            case _:
                args_values[k] = input(v)
    db_url = f"postgresql+psycopg2://{args_values['db_user']}:{args_values['db_password']}" \
             f"@{args_values['db_host']}:{args_values['db_port']}/{args_values['db_name']}"
    ViewInspector(db_url=db_url,
                  db_name=args_values['db_name'],
                  sql_module=args_values['sql_module'],
                  sql_full_path=args_values['sql_full_path']
                  ).register_view(args_values['view_name'],
                                  sql_name=args_values['sql_name'],
                                  create_index=args_values['create_index'],
                                  index_name=args_values['index_name'],
                                  index_col_name=args_values['index_column'],
                                  render_model=args_values['render_model'],
                                  url=args_values['url'],
                                  api_class_name_snake_case=args_values['api_class_name_snake_case'],
                                  api_class_name_pascal_case=args_values['api_class_name_pascal_case'],
                                  root_name=args_values['root_folder'],
                                  schema_name=args_values['db_schema'])