# Stores configuration variables
import os

# get DB directory
basedir = os.path.abspath(os.pardir)
dbPath = basedir + "/app/databases/testDB.db"


class Config:
    # Flask
    SECRET_KEY = "super_secret_key"
    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + dbPath
    SQLALCHEMY_TRACK_MODIFICATIONS = False
