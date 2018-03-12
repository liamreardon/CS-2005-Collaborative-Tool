# --- Imports ---
from flask import render_template, session, redirect, url_for, request
import os
# --- Custom imports ---
from app import app
from app.models import *
# --- BAD IMPORTS ---
#todo: delete this
from app.unit_testing import *


@app.route('/')
@app.route('/index')
def index():
<<<<<<< HEAD
    return render_template("index.html", title="Example Title", text="Hello: Dude")

@app.route('/testing')
def testing():
    """
    Visiting this route will wipe the DB and perform some unit testing
    The objects will be printed to the site for debugging and validation
    """
    init_db()
    users = make_users()
    posts = make_posts(users)
    users = User.query.all()
    return render_template("unit_testing.html", title="Example Title", posts=posts)
=======
    return render_template("index.html", title="Example Title", text="Hello: World")
>>>>>>> login

