import json
import click

from mcli.engine.models import ConfigModel
from mcli.engine.manage_mvc import MVCTemplateManager
from mcli.engine.manage_view import ViewManager


def load_config(path: str):
    with open(path, "r") as file:
        settings = json.load(file)
        args_values = settings['config']['data']

    db_url = f"postgresql+psycopg2://{args_values['db_user']}:{args_values['db_password']}" \
             f"@{args_values['db_host']}:{args_values['db_port']}/{args_values['db_name']}"
    args_values.update({"db_url": db_url})
    return ConfigModel(**args_values)


@click.option('--config',
              default="mcli_config.json",
              help='JSON config of mcli')
@click.group()
def click_group(config):
    pass


@click.option('--config',
              default="mcli_config.json",
              help='JSON config of mcli')
@click.command()
def create_views(config):
    cfg = load_config(config)
    ViewManager(config=cfg).create_views()


@click.option('--config',
              default="mcli_config.json",
              help='JSON config of mcli')
@click.command()
def create_mvc(config):
    cfg = load_config(config)
    MVCTemplateManager(config=cfg).create_template()
