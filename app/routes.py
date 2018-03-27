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
    init_db()
    # users = make_users()
    # posts = make_posts(users)
    # threads = make_thread(users,posts)
    # users = User.query.all()
    return render_template("unit_testing.html", title="Example Title", posts=Post.query.all())

@app.route('/create_thread', methods=['GET', 'POST'])
#@login_required()
def create_thread():
    """
    Create a new thread with a title and a new post
    with a body and commits it to the database.
    """
    form = ThreadForm()
    if form.validate_on_submit():
        new_thread = Thread()
        new_post = Post(title=form.thread.data,text=form.post.data,author_id=current_user.id,thread_id=new_thread.id)
        new_thread.add_first_post(new_post)
        db.session.add(new_thread)
        db.session.commit()
        #flash('Thread submitted.')
        return redirect(url_for('view_threads'))
    return render_template('create_thread.html', form=form)

@app.route('/add_topic/<string:id>', methods=['GET', 'POST'])
#@login_required()
def add_topic(id):
    """
    Create a new topic for a thread and commits
    it to the database.
    """
    current_thread=Thread.query.get(id)

    form = TopicForm()
    if form.validate_on_submit():
        new_topic = Topic(name=form.topic.data)
        new_topic.add_thread(current_thread)
        db.session.add(new_topic)
        db.session.commit()
        #flash('Thread submitted.')
        return redirect(url_for('view_threads'))
    return render_template('add_topic.html', form=form)

@app.route('/view_threads', methods=['GET', 'POST'])
#@login_required()
def view_threads():
    """
    Insert all the threads within the database into
    a table and display the id, title, author, and
    datetime of each thread.
    """
    threads = Thread.query.all()#topic.author.username
    return render_template('view_threads.html', threads=threads)

@app.route('/view_thread/<string:id>', methods=['GET', 'POST'])
#@login_required()
def view_thread(id):
    """
    Display all the posts within a thread and include
    a form to create a new post within that thread.
    """
    posts = Post.query.filter_by(thread_id=id).all()
    #posts = Thread.query.filter_by(id=id).first().posts
    current_thread = Thread.query.get(id)

    form = PostForm()
    if form.validate_on_submit():
        new_post = Post(title=current_thread.name,text=form.post.data,author_id=current_user.id,thread_id=current_thread.id)
        current_thread.add_post(new_post)
        #flash('Post submitted.')
        return redirect(url_for('view_thread',id=id))
    return render_template('view_thread.html', form=form, posts=posts, current_thread=current_thread)

@app.route('/view_thread/edit_post/<string:id>', methods=['GET', 'POST'])
#@login_required()
def edit_post(id):
    """
    Identify a post created by the user and allow the user
    to edit that post.
    """
    current_post = Post.query.get(id)

    form = PostForm(post=current_post.text)
    if form.validate_on_submit():
        current_post.text = form.post.data
        db.session.commit()
        #flash('Post editted.')
        return redirect(url_for('view_thread', id=current_post.thread_id))
    return render_template('edit_post.html', id=id, form=form, post=current_post)

@app.route('/edit_thread/<string:id>', methods=['GET', 'POST'])
#@login_required()
def edit_thread(id):
    """
    Identify a thread created by the user and allow the user 
    to edit that thread.
    """
    current_thread = Thread.query.get(id)

    form = ThreadForm(thread=current_thread.name, post=current_thread.posts[0].text)
    if form.validate_on_submit():
        current_thread.name = form.thread.data
        current_thread.posts[0].text = form.post.data
        db.session.commit()
        #flash('Thread editted.')
        return redirect(url_for('view_threads', id=id))
    return render_template('edit_thread.html', id=id, form=form, thread=current_thread)

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



