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
# todo: delete this
from app.unit_testing import *
from app.models import *


# from app.forms import EditProfileForm


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
    # wipe DB and make dummy users
    # init_db()
    # users = make_users()
    # # user0 creates a new thread
    # topic1 = Topic("topic1")
    # p1 = Post(users[0], "this is a test post #1 in thread #1", title="Thread #1 Title")
    # thread1 = Thread(first_post=p1, topic=topic1)
    # # users 1 and 2 reply
    # p2 = Post(users[1], "this is a reply in thread1", thread1)
    # p3 = Post(users[2], "this is a reply in thread1", thread1)
    # p6 = Post(users[1], "this is my second post in thread1", thread1)
    # thread1.add_post(p2)
    # thread1.add_post(p3)
    # thread1.add_post(p6)
    # # user 3 posts a new thread with the same topic
    # p4 = Post(users[3], "this is the first post in thread #2", title="Thread 2 title")
    # thread2 = Thread(first_post=p4, topic=topic1)
    # # user 4 will post a new thread with a new topic
    # topic2 = Topic("topic2")
    # p5 = Post(users[4], "this is a test post with a new topic", title="Thread 3 title")
    # thread3 = Thread(p5, topic2)
    return render_template("unit_testing.html", title="Example Title", posts=Post.query.all(), topics=Topic.query.all())


@app.route('/create_thread', methods=['GET', 'POST'])
# @login_required()
def create_thread():
    form = ThreadForm()
    if form.validate_on_submit():
        # new_thread = Thread(topic=form.thread.data)
        new_post = Post(title=form.thread.data, text=form.post.data)
        # db.session.add(new_thread)
        db.session.add(new_post)
        db.session.commit()
        return '<h1>Thread submitted.</h1>'
        # return '<h1>' + form.thread.data + form.post.data + '</h1>'
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
        return render_template('redirect_signup.html')

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


@app.route('/subscriptions')
@login_required
def subscriptions():
    return render_template('subscriptions.html')


# region Profile

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        # flash('Your changes have been saved.') #flash not imported
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        current_user.password = hashed_password
        db.session.commit()
        # flash('Your changes have been saved.') #flash not imported
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        hashed_password = current_user.password

    return render_template('change_password.html', title='Change Password',
                           form=form)



# endregion
