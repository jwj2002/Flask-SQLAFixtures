import os
import importlib
import simplejson as json
import click
from flask import current_app
import pandas as pd
import numpy as np
from sqlalchemy import Table
import datetime as dt

DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


class Error(Exception):
    """Based class for exceptions in this modules."""
    pass


class ModelNameError(Error):
    """Exception raised when model_name is not in fixture_models."""

    def __init__(self, message):
        self.message = message


def get_fixtures_directory():
    """Return the path to the fixtures directory.

    Returns:
        path (str): string of path to the fixtures directory

    Notes:
        The fixtures directory default is parent directory of app.root_path. This can
        be overriden by setting 'SQLAFIXTURES_DIRECTORY' in app.config.
    """

    return current_app.extensions['sqlafixtures'].directory


def seed(model_names=[]):
    """Seed the database.

    Parameters:
        models_names (list of str): names of models to seed. If empty, seed all.

    Notes:
        app.extensions['sqlafixtures'].fixtures_directory point to the directory
        where fixtures are maintained.
    """

    db = current_app.extensions['sqlafixtures'].db
    fixtures_directory = get_fixtures_directory()

    conn = db.engine.connect()
    metadata = db.metadata

    fixture_models = get_fixture_models(model_names)

    for mdl in fixture_models:
        table_name = mdl.__table__.name
        path = os.path.join(fixtures_directory, table_name + '.json')
        fixture = json.load(open(path))
        table = Table(fixture['table']['name'], metadata)
        cols = [col for col in table.columns]
        fixture['records'] = format_fixture_record_dates(
            cols, fixture['records'])
        conn.execute(table.insert().prefix_with(
            'OR REPLACE'), fixture['records'])


def get_fixture_models(model_names=[], excludes=[]):
    """Return a list of models configured as sqlafixture models.

    Parameters:
        model_names (list of str): name of models to return. If empty, return all
        exludes (list of str): name of models to exclues

    Returns:
        list of models

    Note:
        app.extensions['sqlafixtures'].fixtures_modules is a list of configured modules
        module.FIXTURES is a list of configured models
    """

    models = []
    for module_name in current_app.extensions['sqlafixtures'].modules:
        module = importlib.import_module(module_name)
        for model_name in getattr(module, 'FIXTURES'):
            if model_names and model_name not in model_names:
                continue
            if model_name in excludes:
                continue
            models.append(getattr(module, model_name))
        mdl_names = [mdl.__name__ for mdl in models]

        model_names = [name for name in model_names if name not in excludes]
        for name in model_names:
            if name not in mdl_names:
                message = "Model '{name}' is not defined as a fixture.".format(
                    name=name)
                raise ModelNameError(message)
    return models


def format_fixture_record_dates(cols, records):
    """Covert json string text date to datetime.date or datetime.datetime.

    Parameters:
        cols (list): list of column objects from a database table.
        records (list): list of dict where each dict is a record from the database.

    Returns:
        records (list): list of dict records where col with str date have been convert to date
        or datetime.
    """

    for record in records:
        for col in cols:
            if col.type.python_type in (dt.date, dt.datetime):
                record[col.name] = convert_str_to_datetime_or_date(
                    record[col.name], col.type.python_type)
    return records


def convert_str_to_datetime_or_date(data, col_type=dt.date):
    """Return dt.date or dt.datetime object or None.

    Parameters:
        data (str): string for of a date or datetime.
        col_type (dt.date or dt.datetime): if dt.date, return dt.date, else return dt.datetime
            if ValueError or TypeError, return None

    Return:
        data (dt.date or dt.datetime): returns dt.date, dt.dateimte or None
    """

    date_format = DATE_FORMAT if col_type == dt.date else DATETIME_FORMAT
    try:
        data = dt.datetime.strptime(data, date_format)
    except (ValueError, TypeError):  # ValueError for None, TypeError for not matching format
        data = None
    if data and col_type == dt.date:
        data = data.date()
    return data


def create_fixtures(model_names, excludes=[], from_file=False):
    """Create json fixtures

    Parameters:
        model_names (list of str): names of models to create fixtures. If empty, create all.
        excludes (list of str): names of models to exclude
        from_file (boolean): True - create from xlsx file, False - create from db.
    """

    models = get_fixture_models(model_names, excludes)
    for model in models:
        if from_file:
            create_fixture_from_file(model)
        else:
            create_fixture_from_db(model)


def create_fixture_from_file(model):
    """Create a fixture from an excel file for the associated model.

    Parameters:
        model (object): The model object for the fixture to create from the file.

    """

    fixtures_directory = get_fixtures_directory()

    click.echo('Creating a fixture for "{model}".'.format(model=model))
    fixture = {}
    fixture['table'] = {}
    table = model.__table__
    fixture['table']['name'] = table.name
    fixture['records'] = []
    cols = [col.name for col in model.__table__.columns]
    df = get_fixture_dataframe(table.name)
    try:
        df = df[cols]
    except KeyError as e:
        print(model)
        print(table.name)
        print(df.columns)
        raise e
    df = convert_df_dates_to_str_or_none(df, table.columns)
    fixture['records'] = df.to_dict('records')
    #sfile = fixtures_directory.joinpath(table.name + '.json')
    sfile = os.path.join(fixtures_directory, table.name + '.json')
    with open(sfile, 'w') as outfile:
        json.dump(fixture, outfile, indent=4)


def convert_df_dates_to_str_or_none(df, cols):
    """Convert dataframe dates to str or None.

    Parameters:
        df (pd.DataFrame): The input dataframe
        cols (sqlalchemy table columns): The colums for the associated table

    Returns:
        df (pd.DataFrame): DataFrame with idntified date columns as string or None
    """

    col_names = [col.name for col in cols if col.type.python_type in (
        dt.date, dt.datetime)]
    for name in col_names:
        df[name] = df[name].astype(str)
        df[name] = df[name].replace({'NaT': None})
    return df


def get_fixture_dataframe(table_name):
    """Function to get a fixture dataframe from the masters_fixture_file."""

    sfile = current_app.extensions['sqlafixtures'].file
    df = pd.read_excel(sfile, sheet_name=table_name)
    # Drop all rows with NaN
    df = df.dropna(how='all')
    # for col in df.columns:
    #     if df[col].dtype.name == 'int64':
    #         df[col] = df[col].astype(np.int32)
    #     if df[col].dtype.name == 'datetime64[ns]':
    #         df[col] = df[col].apply(format_datetime)
    return df


def format_datetime(data):
    return data.date().__str__()


def create_fixture_from_db(model):
    """Create a fixture from a model in the db."""

    db = current_app.extensions['sqlafixtures'].db

    fixtures_directory = get_fixtures_directory()

    click.echo('Creating fixture from db for "{model}".'.format(model=model))
    tablename = model.__tablename__
    fixture = {}
    fixture['table'] = {}
    fixture['table']['name'] = tablename
    fixture['records'] = []
    cols = [col.name for col in model.__table__.columns]
    statement = 'SELECT * FROM {}'.format(model.__tablename__)
    rows = db.session.execute(statement)
    [fixture['records'].append(dict(row)) for row in rows]
    sfile = os.path.join(fixtures_directory, tablename + '.json')
    with open(sfile, 'w') as outfile:
        json.dump(fixture, outfile, indent=4, default=json_encoder)


def json_encoder(obj):
    """JSON encode for objects."""

    if type(obj) == dt.date:
        return obj.__str__()
    if type(obj) == dt.datetime:
        return obj.strftime(DATETIME_FORMAT)

    # if isinstance(obj, dt.date):
    #     return obj.__str__()
