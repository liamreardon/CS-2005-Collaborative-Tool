"""routes.py docstring

This is a Python module that uses Flask @route() decorator to create and modify individual webpages, based on HTML get and post requests. All of the module methods are implemented using several Flask based imports, as well as imports from other custom modules created for the prototype, such as forms.py. All the HTML files being referred to via the Flask @route() decorators are implemented in Jinja2.

Note
----
The following is simply a list of methods within the module, along with a general description of the functionality behind each method. For further information, refer to the docstrings for the resepctive methods.

Methods
-------
login() : LoginForm
    Have the user sign in via credentials (username and password)
signup() : RegistrationForm
    User enters username and password to be registered and cache credentials within database
signup_success()
    Redirect to page confirming user registration
create_thread() : ThreadForm
    Create a new post thread and committ it to the database
view_threads()
    Display all threads cached within the database in a table in a specified format
view_thread(id) : PostForm
    Display all posts within a specific thread, and prompt a form to create a new post in the thread
edit_post() : PostForm
    Identify and edit a post made by the same user that created the post
edit_thread() : ThreadForm
    Identify and edit a thread made by the same user that created the thread
view_topic()
    Identify and present all threads pertaining to a particular topic
subscriptions()
    Display all subscriptions for an individual user
sub_topic()
    Display, specifically, the list of tags an individual user is subscribed to
sub_thread()
    Display, specifically, the list of threads an individual user is subscribed to
unsub_topic()
    Remove a topic from the list of subscribed topics for an individual user.
unsub_thread()
    Remove a thread from the list of subscribed threads for an individual user.
groups()
    Display all groups that the user has access to.
create_group() : CreateGroupForm()
    Prompt the user to create a discussion group and add it to their list of accessable groups.
manage_group()
    Allow user to make adjustments to the group, such as removing themselves from the group.
view_group()
    Allow user to access a discussion group they're a part of.
home()
    Redirects to the homepage of the website.
logout()
    Logs out the user and returns them to the sign-in page
alerts()
    Notifies users whenever unread thread posts, topic-based threads, or discussion group posts, haven't been viewed yet by the respective user.
user(username)
    Displays user's profile page, displaying the posts they've created and their username.
edit_profile()
    Allows users to overwrite their usernames and biographies (i.e 'about me') in their profile page.
change_password()
    Allows users to overwrite their password credential.

"""

# --- Imports ---
from flask import render_template, session, redirect, url_for, request, flash
import os
# --- Custom imports ---
from app.forms import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from app.loaders import *
from app.models import *




@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Checks the user's username and password with the credentials stored within the database, before redirecting them to the homepage
    """

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
     """Creates a new User object from the data passed throught the webpage's username, password and email fields, then redirects to the signup_success HTML page 
     """

    form = RegistrationForm(request.form)
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('signup_success'))
    return render_template('signup.html', form=form)

@app.route('/signup_success')
def signup_success():
    """Confirms user registration success upon passing valid username, password and email data in their respective fields
    """

    return render_template('signup_success.html')


# region Public Threads and Topics
@app.route('/create_thread', methods=['GET', 'POST'])
@login_required
def create_thread():
    """Create a new thread with a title, a new topic, and a new post and commits it to the database.
    """

    form = ThreadForm()
    if form.validate_on_submit():
        new_thread = Thread()
        # new_topic = Topic(name=form.topic.data)
        new_topic = Topic.get(form.topic.data)
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
    """Insert all the threads within the database into a table and display the title, author, datetime and topic of each thread.
    """

    threads = Thread.query.filter_by(group = None).all()
    return render_template('view_threads.html', threads=threads)


@app.route('/view_thread/<string:id>', methods=['GET', 'POST'])
@login_required
def view_thread(id):
    """Display all the posts within a thread and include a form to create a new post within that thread.
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
    """Identify a post created by the user and allow the user to edit that post.
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
    """Identify a thread created by the user and allow the user to edit that thread.
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
    """Display a list of threads based on topic
    """

    topic = Topic.get(topic_name)
    threads = topic.threads
    return render_template('view_topic.html', threads=threads)


# endregion

# region subscriptions

@app.route('/subscriptions')
@login_required
def subscriptions():
    """Displays to users their respective thread, topic, and group subscriptions
    """

    return render_template('subscriptions.html')


@app.route('/sub_topic/<string:topic_name>')
@login_required
def sub_topic(topic_name):
    """Appends an additional topic into the user's list of subscribed topics
    """

    current_user.topics.append(Topic.get(topic_name))
    db.session.commit()
    redir = request.args.get('redir')
    if redir is None:
        redir = 'home'
    return redirect(redir)


@app.route('/sub_thread/<int:thread_id>')
@login_required
def sub_thread(thread_id):
     """Appends an additional thread into the user's list of subscribed threads, assuming that the thread doesn't already exist within the user's list of subscribed threads
     """

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
    """Removes a topic from the user's list of subscribed topics
    """

    current_user.topics.remove(Topic.get(topic_name))
    db.session.commit()
    redir = request.args.get('redir')
    if redir is None:
        redir = 'home'
    return redirect(redir)


@app.route('/unsub_thread/<int:thread_id>')
@login_required
def unsub_thread(thread_id):
    """Removes a thread from the user's list of subscribed topics
    """

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
    """View a list of all discussion groups the user has access to
    """

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
    """Creates the discussion group, along with it's title and description
    """

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
    """Allows the user to edit a discussion group they have access to, which permits edits such as adding users and removing them (including the current user themselves if they wish)
    """

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
    """Displays the chosen discussion group's threads and posts to the user, while prompting them to either create a new post, new thread, or a new topic
    """

    group = Group.query.filter_by(id=id).first()
    form = AddThreadToGroup()
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
    """Renders the homepage template for the website
    """

    return render_template('home.html', name=current_user.username)


@app.route('/logout')
@login_required
def logout():
    """Logs the user out of their user profile, then redirects to the login webapge
    """

    logout_user()
    return redirect(url_for('login'))


@app.route('/alerts')
@login_required
def alerts():
    """Displays any unread notifications to the users, which pertain to topics, threads and posts
    """

    return render_template('alerts.html', name=current_user.username)


# region Profile

@app.route('/user/<username>')
@login_required
def user(username):
    """Displays the user's profile based on their username, which also reveals a list of posts they've made on the website
    """

    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Retrieves the current user's username and about me (i.e biography) data from the server database, then overrides the user's username and about me data with the input passed through the form
    """

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
    """Retrieves the current user's hashed password from the database, then overrides the user's password with the input passed through the form, which is then hashed
    """    
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
