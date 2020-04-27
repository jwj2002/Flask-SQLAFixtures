# Flask-SQLAFixtures

[![Build Status](https://travis-ci.org/jwj2002/Flask-SQLAFixtures.png?branch=master)](https://travis-ci.org/jwj2002/Flask-SQLAFixtures)

Flask-SQLAFixtures is an extension the handles fixtures for Flask applications using SQLAlchemy.

## Installation

Install Flask-SQLAFixtures

## Configuration

Here are the availabe application config variables:

SQLAFIXTURES_DIRECTORY

    - Configures the base directory to store operation directories ('testing', 'development').
    - Default is 'sqlafixtures' in the root directory for the application.

SQLAFIXTURES_MODE

    - Configures the operation directory to use.
    - Default is 'testing'.
    - Support for multiple modes is supported.

SQLAFIXTURES_FILENAME

    - The filename for the excel fixtures file.
    - Default is 'fixtures_file.xlsx'

SQLAFIXTURE_MODULES

    - List of application modules asssigned to Flask-SQLAFixtures
    - Ex: ['app.users.models]
    - Within each models.py file, provide a list of models to varialbe FIXTURES.

## Commands
