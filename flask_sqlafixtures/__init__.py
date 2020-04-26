import os
from flask_sqlafixtures import commands
from flask import current_app
from pathlib import Path


class _SQLAFixturesConfig(object):
    def __init__(self, db, base_directory, directory, modules, file):
        self.db = db
        self.base_directory = base_directory
        self.directory = directory
        self.modules = modules
        self.file = file


class SQLAFixtures(object):
    def __init__(self, app=None, db=None):
        self.db = db
        if app is not None and db is not None:
            self.init_app(app, db)

    def init_app(self, app, db=None):
        self.db = db or self.db
        self.base_directory = self.get_base_directory(app)
        self.directory = self.get_directory(app)
        self.file = self.get_fixtures_file(app)
        self.fixtures_modules = self.get_fixtures_modules(app)
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['sqlafixtures'] = _SQLAFixturesConfig(
            self.db, self.base_directory, self.directory, self.fixtures_modules, self.file)
        register_commands(app)

    def get_base_directory(self, app):
        """Get the sqlafixtures base directory.

        Use app config 'SQLAFIXTURES_DIRECTORY' or add to parent directory of app.root_path
        sqlafixtures directory tree is created with sqlafixture_init command
        """

        base_dir = Path(app.root_path).parent
        try:
            directory = app.config['SQLAFIXTURES_DIRECTORY']
        except KeyError:
            directory = os.path.join(base_dir, 'sqlafixtures')
        return directory

    def get_directory(self, app):
        try:
            mode = app.config['SQLAFIXTURES_MODE']
        except KeyError:
            mode = 'testing'
        directory = os.path.join(self.base_directory, mode)
        return directory

    def get_fixtures_file(self, app):
        """Get the sqlafixtures file."""

        try:
            filename = app.config['SQLAFIXTURES_FILENAME']
        except KeyError:
            filename = 'fixtures_file'
        file = os.path.join(self.directory, filename)
        return file

    def get_fixtures_modules(self, app):
        """Get the app config for 'SQLAFIXTURES_MODULES'

        FIXTURES_MODULES is a list of modules being handled by sqlafixtures.
        """
        try:
            fixtures_modules = app.config['SQLAFIXTURES_MODULES']
        except KeyError:
            fixtures_modules = []
        return fixtures_modules


def register_commands(app):
    app.cli.add_command(commands.init_sqlafixtures)
    app.cli.add_command(commands.seed)
    app.cli.add_command(commands.create_fixtures_from_xlsx)
    app.cli.add_command(commands.create_fixtures_from_db)
    app.cli.add_command(commands.check_sqlafixtures_config)
