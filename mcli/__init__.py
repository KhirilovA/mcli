import json
import click
from mcli.engine.inspect import ViewInspector
from mcli.engine.render_model import ModelRenderer
from mcli.engine.models import ConfigModel


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
    args_values.update({"db_url": db_url})
    config = ConfigModel(**args_values)
    ViewInspector(config=config).register_view()


@click.option('--config', default="mcli_config.json",
              help='JSON config of mcli')
@click.option('--view_name', prompt='Name of view to delete')
@click.command()
def delete_view(config, view_name: str):
    ViewInspector(config=config).delete_view(view_name)


@click.option('--config', default="mcli_config.json",
              help='JSON config of mcli')
@click.command()
def validate_views(config):
    pass


@click.option('--config', default="mcli_config.json",
              help='JSON config of mcli')
@click.command()
def create_model(config):
    ModelRenderer(config=config).create_module()
