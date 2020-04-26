
import os
from flask import Flask
from app.extensions import db, fixtures
import click


HERE = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.join(HERE, os.pardir)


def create_app(config_class):
    """Create the application."""

    app = Flask(__name__)
    app.config.from_object(config_class)
    register_extensions(app)

    @click.command()
    @click.argument("testfile", nargs=-1)
    def test(testfile):
        """Run the tests."""

        import pytest

        testfile = "tests/{}".format(testfile[0]) if testfile else "tests"
        test_path = os.path.join(PROJECT_ROOT, testfile)
        rv = pytest.main([test_path, "-vv"])
        exit(rv)

    app.cli.add_command(test)

    return app


def register_extensions(app):
    db.init_app(app)
    fixtures.init_app(app, db)


from app.users import models  # noqa
