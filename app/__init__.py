"""__init__.py docstring

This method serves as a constructor for the prototype which initializes the database, as well as the CSS and HTML-based design templates, and defines the Flask variables for the test server. 

Notes
-----
    For the sake of convention, database initiallization and user-data/client-side based retrievals have been coded in seperate files.

    config.py initializes the database by creating a client-side directory, followed by setting up the SECRET_KEY Flask variable and the SQLALCHEMY_DATABASE_URI database variable.

    loaders.py stores the method that allows for user data to be retrieved from the database by cross-checking user identification numbers with those cached within the database.

Flask
-----
    The basis of the website, the Flask micro web framework written in Python and based on the Werkzeug toolkit and Jinja2 template engine, licensed under BSD. In addition to providing the framework for the database and the Jinja-based templates, Flask also serves as the local server for which the website's features will be tested on.

Database
--------
    The database is defined using SQLAlchemy, an open source SQL toolkit and object-relational mapper released under the MIT License. Through SQLAlchemy, any data passed through the current iteration of the prototype, such as usernames and/or passwords, is cached and mapped to the database via a data mapper pattern. 

HTML Templates
--------------
    The HTML templates are defined using the Bootstrap front-end framework, an open source library for designing website templates. As this prototype is based on the Flask framework, the templates created will be based on Jinja2 conventions for HTML webpages.

"""

from flask import Flask
from app.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config.from_object(Config)
app.static_folder = 'static'
db = SQLAlchemy(app)
Bootstrap(app)

# must come after app declaration
from app import routes, models
