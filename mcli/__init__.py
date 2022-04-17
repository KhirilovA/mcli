import json
import click
from mcli.engine.inspect import ViewInspector
from mcli.engine.render_model import ModelRenderer
from mcli.engine.models import ConfigModel


def load_config(path: str):
    with open(path, "r") as file:
        settings = json.load(file)
        args_values = settings['config']['data']

    db_url = f"postgresql+psycopg2://{args_values['db_user']}:{args_values['db_password']}" \
             f"@{args_values['db_host']}:{args_values['db_port']}/{args_values['db_name']}"
    args_values.update({"db_url": db_url})
    return ConfigModel(**args_values)


@click.group()
def click_group():
    pass


@click.option('--config',
              default="mcli_config.json",
              help='JSON config of mcli')
@click.command()
def create_view(config):
    cfg = load_config(config)
    ViewInspector(config=cfg).register_view()


@click.option('--config', default="mcli_config.json",
              help='JSON config of mcli')
@click.option('--view_name', prompt='Name of view to delete')
@click.command()
def delete_view(config, view_name: str):
    cfg = load_config(config)
    ViewInspector(config=cfg).delete_view(view_name)


@click.option('--config', default="mcli_config.json",
              help='JSON config of mcli')
@click.command()
def validate_views(config):
    cfg = load_config(config)
    pass


@click.option('--config', default="mcli_config.json",
              help='JSON config of mcli')
@click.command()
def create_model(config):
    cfg = load_config(config)
    ModelRenderer(config=cfg).create_module()
