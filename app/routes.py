# --- Imports ---
from flask import render_template, session, redirect, url_for, request
import os
# --- Custom imports ---
from app import app
from app.models import *
from app.forms import *
# --- BAD IMPORTS ---
#todo: delete this
from app.unit_testing import *


@app.route('/')
@app.route('/index')
def index():
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
    return render_template("index.html", title="Example Title", text="Hello: World")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

    return render_template('signup.html', form=form)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


