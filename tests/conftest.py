import pytest
from app import create_app
from app.extensions import db as _db
from config import DevConfig, TestConfig
from app.users.models import User, Tool
import pandas as pd
import numpy as np
import datetime as dt


@pytest.fixture
def app_object():
    """An app_object for testing SQLAFixtures model"""

    class App():
        root_path = 'root_directory'
        config = {

        }
    return App


@pytest.fixture
def dev_app():
    """A development app for testing.

    When testing click commands, app will be created using autoapp.py.
    This app has the same configuration.
    """

    app = create_app(DevConfig)
    return app


@pytest.fixture
def app():

    app = create_app(TestConfig)
    return app


# @pytest.fixture
# def app():
#     """An app for testing."""

#     _app = create_app(TestConfig)
#     ctx = _app.test_request_context()
#     ctx.push()
#     yield _app
#     ctx.pop()


# @pytest.fixture
# def app2():
#     """A not configured app for testing."""

#     _app = create_app(TestConfig2)

#     ctx = _app.test_request_context()
#     ctx.push()
#     yield _app
#     ctx.pop()


@pytest.fixture
def db(app):
    """A database for testing."""

    _db.app = app
    with app.app_context():
        _db.create_all()

    yield _db

    _db.session.close()
    _db.drop_all()


@pytest.fixture
def user(db):
    user = User(name='Jason')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def tool(db):
    tool = Tool(
        name='screw driver',
        added=dt.date(2020, 3, 29),
        last_seen=dt.datetime(2020, 4, 12, 5, 22, 33)
    )
    db.session.add(tool)
    db.session.commit()
    return tool


@pytest.fixture
def cols():
    return [col for col in Tool.__table__.columns]


@pytest.fixture
def records():
    return [
        {
            "id": 1,
            "name": "screw driver",
            "added": "2020-03-29",
            "last_seen": "2020-04-12 05:22:33"
        },
        {
            "id": 2,
            "name": "hammer",
            "added": "2020-04-19",
            "last_seen": "2020-05-07 23:30:05"
        }
    ]


@pytest.fixture
def tools_df():
    data = [
        (1, 'screw driver', dt.date(2020, 3, 29),
         dt.datetime(2020, 4, 12, 5, 22, 33)),
        (2, 'hammer', dt.date(2020, 4, 19), dt.datetime(2020, 5, 7, 23, 30, 5))
    ]
    df = pd.DataFrame(data)
    df.columns = ['id', 'name', 'added', 'last_seen']
    return df


@pytest.fixture
def tools_df_dates():
    data = [
        (1, 'screw driver', '2020-03-29', '2020-04-12 05:22:33'),
        (2, 'hammer', '2020-04-19', '2020-05-07 23:30:05')
    ]
    df = pd.DataFrame(data)
    df.columns = ['id', 'name', 'added', 'last_seen']
    return df


@pytest.fixture
def tools_df_dates_none():
    data = [
        (1, 'screw driver', '2020-03-29', '2020-04-12 05:22:33'),
        (2, 'hammer', '2020-04-19', None)
    ]
    df = pd.DataFrame(data)
    df.columns = ['id', 'name', 'added', 'last_seen']
    return df


@pytest.fixture
def tools_df_none():
    data = [
        (1, 'screw driver', dt.date(2020, 3, 29),
         dt.datetime(2020, 4, 12, 5, 22, 33)),
        (2, 'hammer', dt.date(2020, 4, 19), None)
    ]
    df = pd.DataFrame(data)
    df.columns = ['id', 'name', 'added', 'last_seen']
    return df


@pytest.fixture
def json_dump_1():
    return {
        "table": {
            "name": "new_tools"
        },
        "records": [
            {
                "id": 1,
                "name": "screw driver",
                "added": "2020-03-29",
                "last_seen": "2020-04-12 05:22:33"
            },
            {
                "id": 2,
                "name": "hammer",
                "added": "2020-04-19",
                "last_seen": "2020-05-07 23:30:05"
            }
        ]
    }


@pytest.fixture
def json_dump_2():
    return {
        "table": {
            "name": "new_tools_none"
        },
        "records": [
            {
                "id": 1,
                "name": "screw driver",
                "added": "2020-03-29",
                "last_seen": "2020-04-12 05:22:33"
            },
            {
                "id": 2,
                "name": "hammer",
                "added": "2020-04-19",
                "last_seen": None
            }
        ]
    }
