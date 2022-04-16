import json
import click
from mcli.engine.inspect import ViewInspector


@click.group()
def click_group():
    pass


@click.option('--config',
              default="mcli_config.json",
              help='JSON config of mcli')
@click.command()
def create_view(config):
    with open(config, "r") as file:
        settings = json.load(file)
        args_values = settings['config']['data']

    db_url = f"postgresql+psycopg2://{args_values['db_user']}:{args_values['db_password']}" \
             f"@{args_values['db_host']}:{args_values['db_port']}/{args_values['db_name']}"
    ViewInspector(db_url=db_url,
                  module_name=args_values['module_name'],
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


@click.option('--config',  default="mcli_config.json",
              help='JSON config of mcli')
@click.option('--view_name', prompt='Name of view to delete')
@click.command()
def delete_view(config, view_name: str):
    pass


@click.option('--config',  default="mcli_config.json",
              help='JSON config of mcli')
@click.command()
def validate_views(config):
    pass
