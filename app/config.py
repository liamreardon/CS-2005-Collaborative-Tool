# Stores configuration variables
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

#meant for unittest testing purposes
class TestConfig:
    TESTING = True
    # Flask
    SECRET_KEY = "super_secret_key"
    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + test_path
    SQLALCHEMY_TRACK_MODIFICATIONS = False



