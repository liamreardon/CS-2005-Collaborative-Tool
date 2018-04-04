# --- Imports ---
from flask import render_template, session, redirect, url_for, request, flash
import os
# --- Custom imports ---
from app import app
from app.models import *
from app.forms import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from app.loaders import *
from app.models import *


# from app.forms import EditProfileForm


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('home'))
    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm(request.form)
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Thanks for registering!')
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)

# region Public Threads and Topics
@app.route('/create_thread', methods=['GET', 'POST'])
@login_required
def create_thread():
    """
    Create a new thread with a title, a new topic,
    and a new post and commits it to the database.
    """
    form = ThreadForm()
    if form.validate_on_submit():
        new_thread = Thread()
        new_topic = Topic(name=form.topic.data)
        new_post = Post(title=form.thread.data, text=form.post.data, user=current_user)
        new_thread.add_first_post(new_post)
        new_thread.add_topic(new_topic)
        db.session.add(new_thread)
        db.session.commit()
        # flash('Thread submitted.')
        return redirect(url_for('view_threads'))
    return render_template('create_thread.html', form=form)


@app.route('/view_threads', methods=['GET', 'POST'])
@login_required
def view_threads():
    """
    Insert all the threads within the database into
    a table and display the title, author,
    datetime and topic of each thread.
    """
    threads = Thread.query.filter_by(group = None).all()
    return render_template('view_threads.html', threads=threads)


@app.route('/view_thread/<string:id>', methods=['GET', 'POST'])
@login_required
def view_thread(id):
    """
    Display all the posts within a thread and include
    a form to create a new post within that thread.
    """
    posts = Post.query.filter_by(thread_id=id).all()
    current_thread = Thread.query.get(id)
    form = PostForm()
    if form.validate_on_submit():
        new_post = Post(title=current_thread.name, text=form.post.data, user=current_user)
        current_thread.add_post(new_post)
        db.session.commit()
        # flash('Post submitted.')
        return redirect(url_for('view_thread', id=id))
    return render_template('view_thread.html', form=form, posts=posts, current_thread=current_thread)


@app.route('/view_thread/edit_post/<string:id>', methods=['GET', 'POST'])
@login_required
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
        # flash('Post editted.')
        return redirect(url_for('view_thread', id=current_post.thread_id))
    return render_template('edit_post.html', id=id, form=form, post=current_post)


@app.route('/edit_thread/<string:id>', methods=['GET', 'POST'])
@login_required
def edit_thread(id):
    """
    Identify a thread created by the user and allow the user 
    to edit that thread.
    """
    current_thread = Thread.query.get(id)
    form = ThreadForm(thread=current_thread.name, topic=current_thread.topic.name, post=current_thread.posts[0].text)
    if form.validate_on_submit():
        current_thread.name = form.thread.data
        current_thread.topic.name = form.topic.data
        current_thread.posts[0].text = form.post.data
        db.session.commit()
        # flash('Thread editted.')
        return redirect(url_for('view_threads', id=id))
    return render_template('edit_thread.html', id=id, form=form, thread=current_thread)


@app.route('/view_topic/<string:topic_name>')
@login_required
def view_topic(topic_name):
    topic = Topic.get(topic_name)
    threads = topic.threads
    return render_template('view_topic.html', threads=threads)


# endregion

# region subscriptions

@app.route('/subscriptions')
@login_required
def subscriptions():
    return render_template('subscriptions.html')


@app.route('/sub_topic/<string:topic_name>')
@login_required
def sub_topic(topic_name):
    current_user.topics.append(Topic.get(topic_name))
    db.session.commit()
    redir = request.args.get('redir')
    if redir is None:
        redir = 'home'
    return redirect(redir)


@app.route('/sub_thread/<int:thread_id>')
@login_required
def sub_thread(thread_id):
    thread = Thread.query.filter_by(id=thread_id).first_or_404()
    if thread not in current_user.subs:
        current_user.subs.append(thread)
        db.session.commit()
    redir = request.args.get('redir')
    if redir is None:
        redir = 'home'
    return redirect(redir)


@app.route('/unsub_topic/<string:topic_name>')
@login_required
def unsub_topic(topic_name):
    current_user.topics.remove(Topic.get(topic_name))
    db.session.commit()
    redir = request.args.get('redir')
    if redir is None:
        redir = 'home'
    return redirect(redir)


@app.route('/unsub_thread/<int:thread_id>')
@login_required
def unsub_thread(thread_id):
    thread = Thread.query.filter_by(id=thread_id).first_or_404()
    if thread in current_user.subs:
        current_user.subs.remove(thread)
        db.session.commit()
    redir = request.args.get('redir')
    if redir is None:
        redir = 'home'
    return redirect(redir)


# endregion

# region groups
@app.route('/groups')
@login_required
def groups():
    rem = request.args.get("rem")
    groups = current_user.groups
    if rem is not None:
        group = Group.query.filter_by(id=rem).first()
        group.users.remove(current_user)
        db.session.commit()
    return render_template('groups.html', groups=groups)


@app.route('/create_group', methods=['GET', 'POST'])
@login_required
def create_group():
    form = CreateGroupForm()
    if form.validate_on_submit():
        name = form.title.data
        descr = form.descr.data
        g = Group(name, descr, user=current_user)
        id = g.id
        return redirect(url_for('manage_group', id=id))
    return render_template('create_group.html', form=form)


@app.route('/manage_group', methods=['GET', 'POST'])
@login_required
def manage_group():
    group_id = request.args.get('id')
    group = Group.query.filter_by(id=group_id).first()
    form = AddUserToGroupForm()
    if form.validate_on_submit():
        username = form.username.data
        user = User.query.filter_by(username=username).first()
        if user is None:
            # redirect(url_for('manage_group', id=group_id, status="bad_user"))
            return render_template('manage_group.html', group=group, form=form, status="bad_user")
        else:
            group.users.append(user)
            db.session.commit()
            redirect(url_for('manage_group', id=group_id))
    return render_template('manage_group.html', group=group, form=form)


@app.route('/view_group/<string:id>', methods=['GET', 'POST'])
@login_required
def view_group(id):
    group = Group.query.filter_by(id=id).first()
    form = AddThreadToGroup()
    #todo: validate if user is member of the group
    #todo add form for posting
    if form.validate_on_submit():
        new_thread = Thread()
        new_topic = Topic.get(form.topic.data)
        new_post = Post(title=form.title.data, text=form.post.data, user=current_user)
        new_thread.add_first_post(new_post)
        new_thread.add_topic(new_topic)
        group.threads.append(new_thread)
        db.session.add(new_thread)
        db.session.commit()
        # flash('Thread submitted.')
        # return "well done"
        # return render_template('view_group.html', group=group, form=form)
    return render_template('view_group.html', group=group, form=form)


# endregion

@app.route('/home')
@login_required
def home():
    return render_template('home.html', name=current_user.username)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/alerts')
@login_required
def alerts():
    return render_template('alerts.html', name=current_user.username)


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
    form = ChangePasswordForm(request.form)
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        current_user.password = hashed_password
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        hashed_password = current_user.password

    return render_template('change_password.html', title='Change Password',
                           form=form)

# endregion
