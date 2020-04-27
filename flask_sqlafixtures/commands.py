import os
import importlib
import simplejson as json
import click
from flask import current_app
from flask.cli import with_appcontext

from flask_sqlafixtures import db_utils


@click.command()
@with_appcontext
def check_sqlafixtures_config():
    """Function to show user current config."""

    fixtures = current_app.extensions['sqlafixtures']
    click.echo('Application configuration variables:')
    for config in [
        'SQLAFIXTURES_DIRECTORY',
        'SQLAFIXTURES_MODULES',
        'SQLAFIXTURES_MODE',
        'SQLAFIXTURES_FILENAME'
    ]:
        try:
            click.echo('{}: {}'.format(config, current_app.config[config]))
        except KeyError:
            click.echo(
                '{}: is not setup in the application configuration.'.format(config))
    click.echo('')
    click.echo('Actual configuration:')
    for attr in (
        ('base_directory', 'BASE DIRECTORY'),
        ('directory', 'FIXTURES DIRECTORY'),
        ('modules', 'FIXTURES MODULES'),
        ('file', 'FIXTURES FILE')
    ):
        click.echo('{}: {}'.format(attr[1], getattr(fixtures, attr[0])))


@click.command()
@with_appcontext
def init_sqlafixtures():
    """Initialize sqlafixtures."""

    base_directory = current_app.extensions['sqlafixtures'].base_directory
    directory = current_app.extensions['sqlafixtures'].directory
    if not os.path.exists(base_directory):
        os.mkdir(base_directory)
        directory = os.path.join(
            base_directory, directory)  # fixtures_directory
        os.mkdir(directory)
        click.echo('SQLAFixtures intialization is complete.')
    else:
        click.echo('Aborting... SQLAFixtures has already been initialized.')


def check_fixtures_file_exists():
    fixtures_file = current_app.extensions['sqlafixtures'].file
    if fixtures_file == None:
        click.echo("'SQLAFIXTURES_FILE' is not configured.")
        return False
    if fixtures_file and not os.path.isfile(fixtures_file):
        click.echo("'SQLAFIXTURES_FILE' is configured. File is not found")
        click.echo("Configures path is {}".format(fixtures_file))
        return False
    return True


@click.command()
@click.option('--models', multiple=True, default=[])
@with_appcontext
def seed(models):
    """Seed the database.

    if user does not enter model_names, seed all
    if user enters one or more model_names, seed those only
    """
    model_names = models

    if model_names:
        model_names = model_names[0].split(',')
    else:
        model_names = []
    click.echo(model_names)

    db_utils.seed(model_names)


@click.command()
@click.option('--models', multiple=True, default=[])
@click.option('--excludes', multiple=True, default=[])
@with_appcontext
def create_fixtures_from_xlsx(models, excludes):
    """Create fixtures from an excel file.


    """
    model_names = models

    # # validate sqlafixtures has been intitiated
    # if not check_sqlafixture_is_initialized():
    #     return

    if model_names:
        model_names = model_names[0].split(',')
    else:
        model_names = []

    if excludes:
        excludes = excludes[0].split(',')
    else:
        excludes = []
    db_utils.create_fixtures(model_names, excludes, from_file=True)
    click.echo('Completed creating fixtures from xlsx')


@click.command()
@click.option('--models', multiple=True, default=[])
@click.option('--excludes', multiple=True, default=[])
@with_appcontext
def create_fixtures_from_db(models, excludes):
    """Create fixtures from the database."""
    model_names = models

    # # validate sqlafixtures has been intitiated
    # if not check_sqlafixture_is_initialized():
    #     return

    if model_names:
        model_names = model_names[0].split(',')
    else:
        model_names = []

    if excludes:
        excludes = excludes[0].split(',')
    else:
        excludes = []
    db_utils.create_fixtures(model_names, excludes, from_file=False)
    click.echo('Completed creating fixtures from db')
