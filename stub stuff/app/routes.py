# --- Imports ---
from flask import render_template, session, redirect, url_for, request
import os
# --- Custom imports ---
from app import app
from app.models import *
from app.forms import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from app.loaders import *
# --- BAD IMPORTS ---
#todo: delete this
from app.unit_testing import *
from app.models import *


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
    # init_db()
    # users = make_users()
    # posts = make_posts(users)
    # threads = make_thread(users,posts)
    # users = User.query.all()
    return render_template("unit_testing.html", title="Example Title", posts=Post.query.all())

@app.route('/create_thread', methods=['GET', 'POST'])
#@login_required()

#def create_group():

def create_thread():
    form = ThreadForm()
    if form.validate_on_submit():
        #new_thread = Thread(topic=form.thread.data)
        new_post = Post(title=form.thread.data, text=form.post.data)
        #db.session.add(new_thread)
        db.session.add(new_post)
        db.session.commit()
        return '<h1>Thread submitted.</h1>'
        #return '<h1>' + form.thread.data + form.post.data + '</h1>'
    return render_template('create_thread.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('home'))

        return '<h1>Invalid username or password</h1>'

    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():

        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return render_template('redirectSignup.html')
           

    return render_template('signup.html', form=form)

@app.route('/home')
@login_required
def home():
    return render_template('home.html', name=current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))