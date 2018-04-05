"""
config.py
Config is a convenience file used to initialize certain aspects of the Flask config dictionary
Two configurations are presented here, one for production and one for unit testing

Config:
    The main config file sets the SECRET_KEY variable which is used by flask for encryption and should not be made
    publicly available.
    SQLALCHEMY variables are also set here, giving a path to the main data.db file, as well as turning off logging
TestConfig:
    The test config differs from the main config in two ways.
    It sets the variable TESTING to true, which flask uses internally to expose more elements to unit testing
    It sets the location of the SQLALCHEMY database to a separate test.db, located in the same directory
    This allows unit tests to be conducted without modifying the production database

The os module is imported to create the path to the database files
"""
import os

# get DB directory
# basedir = os.path.abspath(os.pardir)
basedir = os.path.dirname(__file__)
dbPath = basedir + "/data/data.db"
test_path = basedir + "/data/test.db"


class Config:
    # Flask
    SECRET_KEY = "super_secret_key"
    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + dbPath
    SQLALCHEMY_TRACK_MODIFICATIONS = False


# meant for unittest testing purposes
class TestConfig:
    TESTING = True
    # Flask
    SECRET_KEY = "super_secret_key"
    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + test_path
    SQLALCHEMY_TRACK_MODIFICATIONS = False
