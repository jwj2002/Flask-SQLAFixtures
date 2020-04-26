import os
from pathlib import Path
import sys
import shutil
import simplejson as json
import time
from click.testing import CliRunner
from flask_sqlafixtures import SQLAFixtures
from flask_sqlafixtures import commands, db_utils
from flask import current_app
from flask.cli import with_appcontext
from unittest.mock import MagicMock, Mock
import datetime as dt
from app.users.models import User, Tool
from app.extensions import fixtures

BASEDIR = Path(__file__).parent.parent


class Test_Config:
    """Test configuration."""

    def test_dev_app(self, dev_app):
        """Test app based on the Config class."""

        app = dev_app
        assert app.config['SECRET_KEY'] == "secret_key"
        assert app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] == False
        assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///' + os.path.join(
            BASEDIR, "app_dev.db")
        assert app.config['SQLAFIXTURES_DIRECTORY'] == os.path.join(
            BASEDIR, 'sqlafixtures')
        assert app.config['SQLAFIXTURES_FILENAME'] == 'fixtures_file.xlsx'
        assert app.config['SQLAFIXTURES_MODULES'] == ['app.users.models']

    def test_test_app(self, app):
        """Test app based on the Config class."""

        assert app.config['SECRET_KEY'] == "secret_key"
        assert app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] == False
        assert app.config['SQLALCHEMY_DATABASE_URI'] == "sqlite://"
        assert app.config['SQLAFIXTURES_DIRECTORY'] == os.path.join(
            BASEDIR, 'sqlafixtures')
        assert app.config['SQLAFIXTURES_FILENAME'] == 'fixtures_file.xlsx'
        assert app.config['SQLAFIXTURES_MODULES'] == ['app.users.models']
        assert app.config['SQLAFIXTURES_MODE'] == 'testing'


class TestSQLAFixtures:
    """Test SQLAFixtures."""

    def test__init__with_no_configuration(self, app, db):
        """Test __init__ with no configuration."""

        fixtures = SQLAFixtures(app, db)
        assert fixtures.db == db

        sqlafixtures = app.extensions['sqlafixtures']
        assert sqlafixtures.base_directory == os.path.join(
            BASEDIR, 'sqlafixtures')
        assert sqlafixtures.directory == os.path.join(
            BASEDIR, 'sqlafixtures', 'testing')
        assert sqlafixtures.modules == ['app.users.models']
        assert sqlafixtures.file == os.path.join(
            BASEDIR, 'sqlafixtures', 'testing', 'fixtures_file.xlsx')

    def test_get_base_directory_configured(self, app_object):
        """Test get_base_directory when SQLAFIXTURES_DIRECTORY is configured."""

        app_object.config['SQLAFIXTURES_DIRECTORY'] = 'base_directory'
        fixtures = SQLAFixtures(app_object)
        base_directory = fixtures.get_base_directory(app_object)
        assert base_directory == 'base_directory'

    def test_get_base_directory_not_configured(self, app_object):
        """Test get_base_directory when SQLAFIXTURES_DIRECTORY is not configured."""

        fixtures = SQLAFixtures(app_object)
        base_directory = fixtures.get_base_directory(app_object)
        assert base_directory == './sqlafixtures'

    def test_get_directory_configured(self, app_object):
        """Test get_directory when SQLAFIXTURES_MODE is configured."""

        app_object.config['SQLAFIXTURES_MODE'] = 'jason'

        fixtures = SQLAFixtures(app_object)
        fixtures.base_directory = 'base_directory'
        directory = fixtures.get_directory(app_object)
        assert directory == 'base_directory/jason'

    def test_get_directory_not_configured(self, app_object):
        """Test get_directory when SQLAFIXTURES_MODE is not configured."""

        fixtures = SQLAFixtures(app_object)
        fixtures.base_directory = 'base_directory'
        directory = fixtures.get_directory(app_object)
        assert directory == 'base_directory/testing'

    def test_get_fixtures_file_configured(self, app_object):
        """Test get_fixtures_file when SQLAFIXTURES_FILENAME is configured."""

        app_object.config['SQLAFIXTURES_FILENAME'] = 'my_fixtures_file'

        fixtures = SQLAFixtures(app_object)
        fixtures.directory = 'directory'
        file = fixtures.get_fixtures_file(app_object)
        assert file == 'directory/my_fixtures_file'

    def test_get_fixtures_file_not_configured(self, app_object):
        """Test get_fixtures_file when SQLAFIXTURES_FILENAME is not configured."""

        fixtures = SQLAFixtures(app_object)
        fixtures.directory = 'directory'
        file = fixtures.get_fixtures_file(app_object)
        assert file == 'directory/fixtures_file'

    def test_get_fixtures_modules_configured(self, app_object):
        """Test get_fixtures_file when SQLAFIXTURES_MODULES is configured."""

        app_object.config['SQLAFIXTURES_MODULES'] = ['app.tools.models']

        fixtures = SQLAFixtures(app_object)
        modules = fixtures.get_fixtures_modules(app_object)
        assert modules == ['app.tools.models']

    def test_get_fixtures_modules_not_configured(self, app_object):
        """Test get_fixtures_file when SQLAFIXTURES_MODULES is not configured."""

        fixtures = SQLAFixtures(app_object)
        modules = fixtures.get_fixtures_modules(app_object)
        assert modules == []


class Test_SQLAFixtures_Commands:
    """Test sqlafixtures.command."""

    @classmethod
    def setup_class(cls):
        from config import basedir

        db_path = os.path.join(basedir, 'app_dev.db')
        try:
            os.remove(db_path)
        except OSError:
            pass
        try:
            shutil.rmtree(
                os.path.join(basedir, 'sqlafixtures'))
        except OSError:
            pass

    @classmethod
    def teardown_class(cls):
        from config import basedir

        db_path = os.path.join(basedir, 'app_dev.db')
        try:
            os.remove(db_path)
        except OSError:
            pass
        try:
            shutil.rmtree(
                os.path.join(basedir, 'sqlafixtures'))
        except OSError:
            pass

    def test_init_sqlafixtures_not_initialized(self):
        """Test init_sqlafixtures when not initialized."""

        base_directory = os.path.join(BASEDIR, 'sqlafixtures')
        directory = os.path.join(base_directory, 'development')
        try:
            shutil.rmtree(
                os.path.join(base_directory, 'sqlafixtures'))
        except OSError:
            pass

        runner = CliRunner()
        result = runner.invoke(commands.init_sqlafixtures)
        assert result.output == 'SQLAFixtures intialization is complete.\n'
        assert os.path.exists(base_directory) == True
        assert os.path.exists(directory) == True

    def test_init_sqlafixtures_initialized(self):
        """Test init_sqlafixtures when initialized."""

        base_directory = os.path.join(BASEDIR, 'sqlafixtures')
        if not os.path.exists(base_directory):
            os.mkdir(base_directory)
        directory = os.path.join(base_directory, 'development')
        if not os.path.exists(directory):
            os.mkdir(directory)

        runner = CliRunner()
        result = runner.invoke(commands.init_sqlafixtures)
        expected = "Aborting... SQLAFixtures has already been initialized.\n"
        assert result.output == expected

    def test_seed_no_model_names(self):
        """Test seed when no model names provided."""

        seed = db_utils.seed
        db_utils.seed = MagicMock()

        runner = CliRunner()
        result = runner.invoke(
            commands.seed, catch_exceptions=False)
        assert not result.exception
        db_utils.seed.assert_called_with([])
        db_utils.seed = seed

    def test_seed_multiple_single_model(self):
        """Test seed with single model name."""

        seed = db_utils.seed
        db_utils.seed = MagicMock()
        runner = CliRunner()
        result = runner.invoke(
            commands.seed, ['--models', 'User'], catch_exceptions=False)
        assert not result.exception
        db_utils.seed.assert_called_with(['User'])
        db_utils.seed = seed

    def test_seed_multiple_model_names(self):
        """Test seed with multiple model names."""

        seed = db_utils.seed
        db_utils.seed = MagicMock()
        runner = CliRunner()
        result = runner.invoke(
            commands.seed, ['--models', 'User,Tool'], catch_exceptions=False)
        assert not result.exception
        db_utils.seed.assert_called_with(['User', 'Tool'])
        db_utils.seed = seed

    def test_create_fixtures_from_xlsx_no_models_no_exclues(self, app):
        """Test create_fixtures_from_xlsx with no models."""

        create_fixtures = db_utils.create_fixtures
        db_utils.create_fixtures = MagicMock()
        runner = CliRunner()
        result = runner.invoke(
            commands.create_fixtures_from_xlsx, catch_exceptions=False)
        assert not result.exception
        db_utils.create_fixtures.assert_called_with([], [], from_file=True)
        assert result.output == 'Completed creating fixtures from xlsx\n'
        db_utils.create_fixtures = create_fixtures

    def test_create_fixtures_from_xlsx_single_model_single_excludes(self):
        """Test create_fixtures_from_xlsx with single model, single excludes."""

        create_fixtures = db_utils.create_fixtures
        db_utils.create_fixtures = MagicMock()
        runner = CliRunner()
        result = runner.invoke(
            commands.create_fixtures_from_xlsx, ['--models', 'User', '--excludes', 'Tool'], catch_exceptions=False)
        assert not result.exception
        db_utils.create_fixtures.assert_called_with(
            ['User'], ['Tool'], from_file=True)
        assert result.output == 'Completed creating fixtures from xlsx\n'
        db_utils.create_fixtures = create_fixtures

    def test_create_fixtures_from_xlsx_multiple_model_multiple_excludes(self):
        """Test create_fixtures_from_xlsx with multiple models, multiple excludes."""

        create_fixtures = db_utils.create_fixtures
        db_utils.create_fixtures = MagicMock()
        runner = CliRunner()
        result = runner.invoke(
            commands.create_fixtures_from_xlsx, ['--models', 'User,Tool', '--excludes', 'Boat,Car'], catch_exceptions=False)
        assert not result.exception
        db_utils.create_fixtures.assert_called_with(
            ['User', 'Tool'], ['Boat', 'Car'], from_file=True)
        assert result.output == 'Completed creating fixtures from xlsx\n'
        db_utils.create_fixtures = create_fixtures

    def test_create_fixtures_from_db_no_models_no_excludes(self):
        """Test create_fixtures_from_db with no models no exludes."""

        create_fixtures = db_utils.create_fixtures
        db_utils.create_fixtures = MagicMock()
        runner = CliRunner()
        result = runner.invoke(
            commands.create_fixtures_from_db, catch_exceptions=False)
        assert not result.exception
        db_utils.create_fixtures.assert_called_with([], [], from_file=False)
        assert result.output == 'Completed creating fixtures from db\n'
        db_utils.create_fixtures = create_fixtures

    def test_create_fixtures_from_db_single_model_single_excludes(self):
        """Test create_fixtures_from_db with single model, single excludes."""

        create_fixtures = db_utils.create_fixtures
        db_utils.create_fixtures = MagicMock()
        runner = CliRunner()
        result = runner.invoke(
            commands.create_fixtures_from_db, ['--models', 'User', '--excludes', 'Tool'], catch_exceptions=False)
        assert not result.exception
        db_utils.create_fixtures.assert_called_with(
            ['User'], ['Tool'], from_file=False)
        assert result.output == 'Completed creating fixtures from db\n'
        db_utils.create_fixtures = create_fixtures

    def test_create_fixtures_from_db_multiple_model_multiple_excludes(self):
        """Test create_fixtures_from_db with multiple models, multiple excludes."""

        create_fixtures = db_utils.create_fixtures
        db_utils.create_fixtures = MagicMock()
        runner = CliRunner()
        result = runner.invoke(
            commands.create_fixtures_from_db, ['--models', 'User,Tool', '--excludes', 'Boat,Car'], catch_exceptions=False)
        assert not result.exception
        assert result.output == 'Completed creating fixtures from db\n'
        db_utils.create_fixtures.assert_called_with(
            ['User', 'Tool'], ['Boat', 'Car'], from_file=False)
        db_utils.create_fixtures = create_fixtures

    def test_check_sqlafixtures_is_initialized_not(self, app):
        """Test check_sqlafixtures_is_initialized."""

        app.extensions['sqlafixtures'].fixtures_modules = None
        with app.app_context():
            results = commands.check_fixtures_file_exists()
        assert results == False

    def test_check_sqlafixtures_file_exists_not_configure(self, app):
        """Test check_sqlafixtures_is_iexists when not configured."""

        app.extensions['sqlafixtures'].fixtures_file = None
        with app.app_context():
            results = commands.check_fixtures_file_exists()
        assert results == False

    def test_check_sqlafixtures_file_exists_configured_not_file(self, app):
        """Test check_sqlafixtures_is_iexists when configured no file exists."""

        app.extensions['sqlafixtures'].fixtures_file = 'fixtures_file'
        isfile = os.path.isfile
        os.path.isfile = MagicMock(return_value=False)
        with app.app_context():
            results = commands.check_fixtures_file_exists()
        assert results == False
        os.path.isfile == isfile

    def test_check_sqlafixtures_file_exists_configured_valid_file(self, app):
        """Test check_sqlafixtures_is_iexists when configured with a valid file."""

        app.extensions['sqlafixtures'].fixtures_file = 'fixtures_file'
        isfile = os.path.isfile
        os.path.isfile = MagicMock(return_value=True)
        with app.app_context():
            results = commands.check_fixtures_file_exists()
        assert results == True
        os.path.isfile == isfile


class Test_SQLAFixtures_DB_Utils:
    """Test sqlafixtures.db_utils."""

    def test_get_fitures_directory(self, app):
        """Test get_fixtures_directory."""

        with app.app_context():
            directory = db_utils.get_fixtures_directory()
        assert directory == app.extensions['sqlafixtures'].directory

    def test_get_fixtures_models_no_models_no_exludes(self, app):
        """Test get_fixture_models with no model_names and no excludes."""

        with app.app_context():
            models = db_utils.get_fixture_models()
        assert models == [User, Tool]

    def test_get_fixtures_models_single_model_no_exludes(self, app):
        """Test get_fixture_models with single model_name and no excludes."""

        with app.app_context():
            models = db_utils.get_fixture_models(['User'])
        assert models == [User]

    def test_get_fixtures_models_no_models_and_exludes(self, app):
        """Test get_fixture_models with no model_names and excludes."""

        with app.app_context():
            models = db_utils.get_fixture_models(excludes=['User'])
        assert models == [Tool]

    def test_get_fixtures_models_incorrect_model_name(self, app):
        """Test get_fixture_models with an incorrect model_name."""

        try:
            with app.app_context():
                models = db_utils.get_fixture_models(['Truck'])
        except db_utils.ModelNameError as e:
            assert e.message == "Model 'Truck' is not defined as a fixture."

    def test_seed_no_model_name(self, app, db):
        """Test seed with no model_names."""

        base_dir = Path(app.root_path).parent
        test_dir = os.path.join(base_dir, 'tests', 'data')

        get_fixtures_directory = db_utils.get_fixtures_directory
        db_utils.get_fixtures_directory = MagicMock(return_value=test_dir)

        with app.app_context():
            db_utils.seed()
        statement = 'SELECT * from users'
        rows = db.session.execute(statement)
        rows = list(rows)
        assert rows == [(1, 'Jason'), (2, 'Sheila')]
        statement = 'SELECT * FROM tools'
        rows = db.session.execute(statement)
        rows = list(rows)
        assert rows == [(1, 'screw driver', '2020-03-29', '2020-04-12 05:22:33.000000'),
                        (2, 'hammer', '2020-04-19', '2020-05-07 23:30:05.000000')]

        db_utils.get_fixtures_directory = get_fixtures_directory

    def test_convert_str_to_datetime_or_date_date_none(self):
        """Test convert_str_to_datetime_or_date date with None."""

        data = None
        new_data = db_utils.convert_str_to_datetime_or_date(
            data, dt.date)  # default for date is True
        assert new_data == None

    def test_convert_str_to_datetime_or_date_datetime_none(self):
        """Test convert_str_to_datetime_or_date datetime with None."""

        data = None
        new_data = db_utils.convert_str_to_datetime_or_date(
            data, dt.datetime)  # default for date is True
        assert new_data == None

    def test_convert_str_to_datetime_or_date_date_empty(self):
        """Test convert_str_to_datetime_or_date date with empty string."""

        data = ''
        new_data = db_utils.convert_str_to_datetime_or_date(
            data, dt.date)  # default for date is True
        assert new_data == None

    def test_convert_str_to_datetime_or_date_datetime_empty(self):
        """Test convert_str_to_datetime_or_date datetime with empty string."""

        data = ''
        new_data = db_utils.convert_str_to_datetime_or_date(
            data, dt.datetime)  # default for date is True
        assert new_data == None

    def test_convert_str_to_datetime_or_date_date_valid(self):
        """Test convert_str_to_datetime_or_date date with valid date string."""

        data = '2020-07-04'
        new_data = db_utils.convert_str_to_datetime_or_date(
            data, dt.date)  # default for date is True
        assert new_data == dt.date(2020, 7, 4)

    def test_convert_str_to_datetime_or_date_datetime_valid(self):
        """Test convert_str_to_datetime_or_date datetime with valid datetime."""

        data = '2021-5-27 23:11:31'
        new_data = db_utils.convert_str_to_datetime_or_date(
            data, dt.datetime)  # default for date is True
        assert new_data == dt.datetime(2021, 5, 27, 23, 11, 31)

    def test_format_fixture_record_dates(self, cols, records):
        """Test format_fixture_record_dates."""

        records = db_utils.format_fixture_record_dates(cols, records)
        assert records[0]['added'] == dt.date(2020, 3, 29)
        assert records[0]['last_seen'] == dt.datetime(2020, 4, 12, 5, 22, 33)

    def test_create_fixtures_file(self, app):
        """Test create_fixtures from file."""

        get_fixture_models = db_utils.get_fixture_models
        create_fixture_from_file = db_utils.create_fixture_from_file
        create_fixture_from_db = db_utils.create_fixture_from_db

        db_utils.get_fixture_models = MagicMock(return_value=[User])
        db_utils.create_fixture_from_file = MagicMock()
        db_utils.create_fixture_from_db = MagicMock()

        db_utils.create_fixtures(['User'], [], from_file=True)

        db_utils.create_fixture_from_file.assert_called_with(User)
        db_utils.create_fixture_from_db.assert_not_called()

        db_utils.get_fixture_models = get_fixture_models
        db_utils.create_fixture_from_file = create_fixture_from_file
        db_utils.create_fixture_from_db = create_fixture_from_db

    def test_create_fixtures_db(self, app):
        """Test create_fixtures from db."""

        get_fixture_models = db_utils.get_fixture_models
        create_fixture_from_file = db_utils.create_fixture_from_file
        create_fixture_from_db = db_utils.create_fixture_from_db

        db_utils.get_fixture_models = MagicMock(return_value=[User])
        db_utils.create_fixture_from_file = MagicMock()
        db_utils.create_fixture_from_db = MagicMock()

        db_utils.create_fixtures(['User'], [], from_file=False)

        db_utils.create_fixture_from_file.assert_not_called()
        db_utils.create_fixture_from_db.assert_called_with(User)

        db_utils.get_fixture_models = get_fixture_models
        db_utils.create_fixture_from_file = create_fixture_from_file
        db_utils.create_fixture_from_db = create_fixture_from_db

    def test_get_fixtures_dataframe_users(self, app):
        """Test get_fixtures_dataframe."""

        base_dir = Path(app.root_path).parent
        test_dir = os.path.join(base_dir, 'tests', 'data')
        fixtures_file = os.path.join(test_dir, 'fixtures_file.xlsx')
        app.extensions['sqlafixtures'].file = fixtures_file
        table_name = 'users'
        with app.app_context():
            df = db_utils.get_fixture_dataframe(table_name)

        assert list(df.columns) == ['id', 'name']
        assert list(df['id']) == [1, 2, 3]
        assert list(df['name']) == ['Jason', 'Sheila', 'Maiyan']

    def test_get_fixtures_dataframe_tools(self, app):
        """Test get_fixtures_dataframe."""

        base_dir = Path(app.root_path).parent
        test_dir = os.path.join(base_dir, 'tests', 'data')
        fixtures_file = os.path.join(test_dir, 'fixtures_file.xlsx')
        app.extensions['sqlafixtures'].file = fixtures_file
        table_name = 'tools'
        with app.app_context():
            df = db_utils.get_fixture_dataframe(table_name)

        assert list(df.columns) == ['id', 'name', 'added', 'last_seen']
        assert list(df['id']) == [1, 2]
        assert df['added'][0].to_pydatetime() == dt.datetime(2020, 3, 29)
        assert df['last_seen'][1].to_pydatetime(
        ) == dt.datetime(2020, 5, 7, 23, 30, 5)

    def test_convert_df_dates_to_str(self, tools_df):
        """Test convert_df_dates to str."""

        cols = Tool.__table__.columns
        df = db_utils.convert_df_dates_to_str_or_none(tools_df, cols)
        assert df['added'][0] == '2020-03-29'
        assert df['last_seen'][0] == '2020-04-12 05:22:33'

    def test_convert_df_dates_to_str_none(self, tools_df_none):
        """Test convert_df_dates to str with a None date."""

        cols = Tool.__table__.columns
        df = db_utils.convert_df_dates_to_str_or_none(tools_df_none, cols)
        assert df['added'][0] == '2020-03-29'
        assert df['last_seen'][0] == '2020-04-12 05:22:33'
        assert df['last_seen'][1] == None

    def test_create_fixture_file(self, app, tools_df, tools_df_dates, json_dump_1):
        """Test create_fixture_from_file."""

        base_dir = Path(app.root_path).parent
        test_dir = os.path.join(base_dir, 'tests', 'data')

        get_fixtures_directory = db_utils.get_fixtures_directory
        db_utils.get_fixtures_directory = MagicMock(return_value=test_dir)

        get_fixtures_dataframe = db_utils.get_fixture_dataframe
        db_utils.get_fixture_dataframe = MagicMock(return_value=tools_df)

        convert_dates = db_utils.convert_df_dates_to_str_or_none
        db_utils.convert_df_dates_to_str_or_none = MagicMock(
            return_value=tools_df_dates)

        Tool.__table__.name = 'new_tools'
        db_utils.create_fixture_from_file(Tool)

        json_file = os.path.join(test_dir, 'new_tools.json')
        assert os.path.isfile(json_file) == True

        fixture = json.load(open(json_file))
        assert fixture == json_dump_1

        db_utils.get_fixtures_directory = get_fixtures_directory
        db_utils.get_fixture_dataframe = get_fixtures_dataframe
        db_utils.convert_df_dates_to_str_or_none = convert_dates
        os.remove(json_file)
        Tool.__table__.name = 'tools'

    def test_create_fixture_file_none(self, app, tools_df_none, tools_df_dates_none, json_dump_2):
        """Test create_fixture_from_file with None for data"""

        base_dir = Path(app.root_path).parent
        test_dir = os.path.join(base_dir, 'tests', 'data')

        get_fixtures_directory = db_utils.get_fixtures_directory
        db_utils.get_fixtures_directory = MagicMock(return_value=test_dir)

        get_fixtures_dataframe = db_utils.get_fixture_dataframe
        db_utils.get_fixture_dataframe = MagicMock(return_value=tools_df_none)

        convert_dates = db_utils.convert_df_dates_to_str_or_none
        db_utils.convert_df_dates_to_str_or_none = MagicMock(
            return_value=tools_df_dates_none)

        Tool.__table__.name = 'new_tools_none'
        db_utils.create_fixture_from_file(Tool)

        json_file = os.path.join(test_dir, 'new_tools_none.json')
        assert os.path.isfile(json_file) == True

        fixture = json.load(open(json_file))
        assert fixture == json_dump_2

        db_utils.get_fixtures_directory = get_fixtures_directory
        db_utils.get_fixture_dataframe = get_fixtures_dataframe
        db_utils.convert_df_dates_to_str_or_none = convert_dates
        os.remove(json_file)
        Tool.__table__.name = 'tools'

    def test_json_encoder_date(self):
        """Test json_encoder with date."""

        date = dt.date(2020, 5, 6)
        result = db_utils.json_encoder(date)
        assert result == '2020-05-06'

    def test_json_encoder_datetime(self):
        """Test json_encoder with datetime."""

        date = dt.datetime(2020, 5, 6, 17, 55, 6)
        result = db_utils.json_encoder(date)
        assert result == '2020-05-06 17:55:06'

    def test_create_fixture_from_db(self, app, db, tool):

        base_dir = Path(app.root_path).parent
        test_dir = os.path.join(base_dir, 'tests', 'data')
        json_file = os.path.join(test_dir, 'db_tools.json')

        join = os.path.join
        os.path.join = MagicMock(return_value=json_file)

        get_fixtures_directory = db_utils.get_fixtures_directory
        db_utils.get_fixtures_directory = MagicMock(return_value=test_dir)

        with app.app_context():
            db_utils.create_fixture_from_db(Tool)

        assert os.path.isfile(json_file) == True

        db_utils.get_fixtures_directory = get_fixtures_directory
