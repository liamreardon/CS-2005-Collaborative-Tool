"""
models.py holds the information for all the persistent classes used in the project
Classes are implemented using Flask-SQLAlchemy
Classes:
    User: Holds all information about a specific user
    Post: A post represents a single post by a single user
    Thread: An ADT that contains references to many threads, and users subscribed to follow the thread
    Topic: Serves as a way to group posts by topics as well as subscribe users to all posts tagged with the same name
todo: consider refactoring all id and otherwise private variables to have a leading underscore
"""
from app import db
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.ext.associationproxy import association_proxy


class ThreadSubscriptions(db.Model):
    """
    ThreadSubscriptions is an association table for users and threads
    An association table is used to allow for notifications
    fields:
        id:     primary key
        user:   reference to a user
        thread: the thread they're subscriped to
        unseen: boolean, True if user has unread posts
    """
    __tablename__ = 'thread_subscriptions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.username'))
    thread_id = db.Column(db.Integer, db.ForeignKey('Thread.id'))
    user = db.relationship("User", back_populates="sub_id")
    thread = db.relationship("Thread", back_populates="subbed_id")
    unseen = db.Column('unseen', db.Boolean, default=False)

    def __init__(self, user=None, thread=None):
        self.user = user
        self.thread = thread

    def __repr__(self):
        return "ThreadSubscription object for thread: " + str(self.thread.topic)


class TopicSubscriptions(db.Model):
    """
    TopicSubscriptions is an association table for users and topics
    An association table is used to allow for notifications
    fields:
        id:     primary key
        user:   reference to the user
        name:  reference to the thread
        unseen: boolean, True if user has unread posts
    """
    __tablename__ = 'topic_subscriptions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    topic_id = db.Column(db.Integer, db.ForeignKey('Topic.id'))
    user = db.relationship("User", back_populates="topic_id")  # todo add this to user
    topic = db.relationship("Topic", back_populates="user_id")  # todo add this to name
    unseen = db.Column('unseen', db.Boolean, default=False)

    def __init__(self, user=None, topic=None):
        self.user = user
        self.topic = topic

    def __repr__(self):
        return "TopicSubscription association for " + str(self.user.username) + " and " + str(self.topic.name)


# endregion

class User(UserMixin, db.Model):
    """
    A class to store user information
    Fields:
        id:                 Integer primary key
        username:           self explanatory
        password:           self explanatory
        email:              self explanatory
        posts:              a list of all the posts this user has made
        subs:               a list of all the threads this user has subscriptions to
    """
    # fields
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(128))
    email = db.Column(db.String(128), index=True, unique=True)
    # relationships
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    sub_id = db.relationship('ThreadSubscriptions', back_populates='user')
    subs = association_proxy('sub_id', 'thread', creator=lambda t: ThreadSubscriptions(thread=t))
    topic_id = db.relationship('TopicSubscriptions', back_populates='user')
    topics = association_proxy('topic_id', 'topic', creator=lambda t: TopicSubscriptions(topic=t))

    def __init__(self, *args, **kwargs):
        db.session.add(self)
        db.session.commit()
        for key, value in kwargs.items():
            setattr(self, key, value)

    def has_notifications(self):
        """
        returns True if the user has unseen notifications
        """
        for sub in self.sub_id:
            if sub.unseen:
                return True
        return False

    def __repr__(self):
        usrname = "USERNAME NOT SET"
        if self.username is not None:
            usrname = self.username
        return "User " + self.username


class Post(db.Model):
    """
    A class to store post information
    Fields:
        id:         Integer primary key
        title:      title of the post
        text:       content of the post
        timestamp:  UTC time the post was made
        author:     relationship with user (1:n)
        thread:     relationship with Thread (1:n)
    """
    __tablename__ = "Post"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    text = db.Column(db.Text())
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    # relationships
    # topic_id = db.Column(db.Integer, db.ForeignKey('Topic.id'))
    # topic = db.relationship('Topic', back_populates='posts')
    author_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    thread_id = db.Column(db.Integer, db.ForeignKey('Thread.id'))

    def __init__(self, user=None, title=None, text=None, thread=None):
        db.session.add(self)
        db.session.commit()


class Thread(db.Model):
    """
    Thread represents a single forum thread
    Fields:
        id:     primary key
        posts:  a list of posts in the thread
        name:  what the post is about
        subbed: users who are subscribed to the thread
        topic:  the topic object associated with this thread
    """
    __tablename__ = "Thread"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    # relationships
    posts = db.relationship('Post', backref='thread')
    topic_id = db.Column(db.Integer, db.ForeignKey('Topic.id'))
    topic = db.relationship('Topic', back_populates='threads')
    subbed_id = db.relationship('ThreadSubscriptions', back_populates='thread')
    subbed = association_proxy('subbed_id', 'user', creator=lambda u: ThreadSubscriptions(user=u))

    def __init__(self, first_post=None, topic=None):
        """
        Creates a thread object that adds itself to the DB and commits
        :param first_post: if supplied will set the post name and subscribe the user to the thread
        """
        db.session.add(self)
        if first_post:
            self.add_first_post(first_post)
        if topic:
            self.topic = topic;
        db.session.commit()

    def add_first_post(self, first_post):
        """
        Adds the first post to the top of the thread
        Sets the title of the thread to the title of the post
        Subscribes the user to the thread automatically
        :param first_post: the OP of the thread
        :return:
        """
        self.name = first_post.title
        self.posts = [first_post]
        self.subbed = [first_post.author]
        self.notify()

    def add_post(self, post):
        """
        Adds a post to the thread and notifies the users
        :param post:
        """
        self.posts.append(post)
        self.notify()
        self.subbed.append(post.author)

    def notify(self):
        for sub in self.subbed_id:
            sub.unseen = True

    def __repr__(self):
        return "Thread " + str(self.name)


class Topic(db.Model):
    """
    Topics are tags that can be added to threads
    Users can subscribe to topics in order to be notified about any post made with that topic
    """
    __tablename__ = 'Topic'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    # relationships
    threads = db.relationship("Thread", back_populates='topic')
    user_id = db.relationship('TopicSubscriptions', back_populates='topic')
    users = association_proxy('user_id', 'user', creator=lambda u: TopicSubscriptions(user=u))

    def add_thread(self, thread):
        self.threads.append(thread)

    def add_user(self, user):
        self.users.append(user)

    def notify(self):
        for user in self.user_id:
            user.unseen = True

    def __init__(self, topic_name=None):
        """
        Creates a topic object that adds itself to the DB and commits
        :param topic_name: if supplied will set the topic name
        """
        db.session.add(self)
        if topic_name:
            self.name = topic_name
        db.session.commit()
