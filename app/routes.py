# --- Imports ---
from flask import flash, render_template, session, redirect, url_for, request
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
def create_thread():
    """
    Creates a new thread with a title and a new post with a body and
    commits it to the database.
    """
    form = ThreadForm()
    if form.validate_on_submit():
        new_thread = Thread()
        new_post = Post(title=form.thread.data,text=form.post.data,author_id=current_user.id,thread_id=new_thread.id)
        new_thread.add_first_post(new_post)
        db.session.commit()
        #flash('Thread submitted.')
        return redirect(url_for('home'))
    return render_template('create_thread.html', form=form)

@app.route('/view_threads', methods=['GET', 'POST'])
#@login_required()
def view_threads():
    """
    Displays all the threads within the database into
    a table and displays the id, title, author, and
    datetime.
    """
    threads = Thread.query.all()
    return render_template('view_threads.html', threads=threads)

@app.route('/view_thread/<string:id>', methods=['GET', 'POST'])
#@login_required()
def view_thread(id):
    """
    Displays all the posts within a specific thread and includes
    a form to insert a post within that thread.
    """
    posts = Post.query.filter_by(thread_id=id).all()
    current_thread = Thread.query.get(id)

    form = PostForm()
    if form.validate_on_submit():
        new_post = Post(title=form.thread.data,text=form.post.data,author_id=current_user.id)
        current_thread.add_post(new_post)
        #flash('Post submitted.')
        return render_template('view_thread.html', form=form, posts=posts)
    return render_template('view_thread.html', form=form, posts=posts)

@app.route('/edit_post/<string:id>', methods=['GET', 'POST'])
#@login_required()
def edit_post(id):
    """
    Users who have created posts can edit the posts they have created.
    """
    form = PostForm()
    if form.validate_on_submit():
        form.thread.data = current_thread
        form.post.data = current_post
        new_post = Post(title=form.thread.data,text=form.post.data,author_id=current_user.id,thread_id=new_thread.id)
        current_thread.add_post(new_post)
        #flash('Post editted.')
        return render_template('edit_post.html', form=form)
    return render_template('edit_post.html', form=form)

@app.route('/edit_thread/<string:id>', methods=['GET', 'POST'])
#@login_required()
def edit_thread(id):
    """
    Users who have created threads can edit threads they have created.
    """
    form = ThreadForm()
    if form.validate_on_submit():
        form.thread.data = current_thread
        form.post.data = current_post
        new_post = Post(title=form.thread.data,text=form.post.data,author_id=current_user.id,thread_id=new_thread.id)
        current_thread.add_post(new_post)
        #flash('Thread editted.')
        return render_template('edit_thread.html', form=form)
    return render_template('edit_thread.html', form=form)

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



