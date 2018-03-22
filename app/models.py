"""
models.py holds the information for all the persistent classes used in the project
Classes are implemented using Flask-SQLAlchemy
Classes:
    User:   A single user and all their information
    Thread: A series of posts made by many users in response to eachother
    Post:   A single post by a single user within a thread
    Topic:  Topics are user-submitted strings that are used to classify and group threads by topic
todo: consider refactoring all id and otherwise private variables to have a leading underscore
"""
from app import db
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.ext.associationproxy import association_proxy


# region Association Classes
# Association classes are used by SQLAlchemy to manage many-to-many relationships
# Outside of this module they should not need to be referenced directly

class ThreadSubscriptions(db.Model):
    """
    ThreadSubscriptions is an association table for users and threads
    An association table is used to allow for notifications
    fields:
        id:     primary key
        user:   reference to a user
        thread: the thread they're subscribed to
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
        name:   reference to the thread
        unseen: boolean, True if user has unread posts
    """
    __tablename__ = 'topic_subscriptions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    topic_id = db.Column(db.Integer, db.ForeignKey('Topic.id'))
    user = db.relationship("User", back_populates="topic_id")
    topic = db.relationship("Topic", back_populates="user_id")
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

    def __init__(self, username, password, email, **kwargs):
        """
        Constructor for user
        Adds the required fields and commits the object to the database
        """
        self.username = username
        self.email = email
        self.password = password
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.add(self)
        db.session.commit()

    def has_notifications(self):
        """
        returns True if the user has unseen notifications
        """
        for sub in self.sub_id:
            if sub.unseen:
                return True
        return False

    # todo this needs to be tested
    def get_unseen_threads(self):
        threads = []
        for sub in self.sub_id:
            if sub.unseen:
                threads.append(sub.thread)
        return threads

    # todo this needs to be tested
    def get_unseen_topics(self):
        topics = []
        for topic in self.topic_id:
            if topic.unseen:
                topics.append(topic.thread)
        return topics

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
    author_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    thread_id = db.Column(db.Integer, db.ForeignKey('Thread.id'))

    def __init__(self, user, text, thread=None, title=None):
        """
        Creates a post object and commits it to the database
        If a reference to a thread is provided this post is automatically appended
        If the passed thread has no posts this post will be considered the first post and will initialize the thread
        NOTE: Threads can only be initialized with posts that have a title
        Otherwise the post will be appended as a child post to the thread
        If no thread is passed then this post must be added using add_post or add_first_post on the thread elsewhere
        """
        self.author = user
        self.text = text
        self.title = title
        self.thread = thread
        if thread is not None:
            if thread.posts == []:
                if title is None:
                    raise ValueError("You cannot initialize an empty thread with a post that has no title!")
                else:
                    thread.add_first_post(self)
            else:
                thread.add_post(self)
        db.session.add(self)
        db.session.commit()


class Thread(db.Model):
    """
    Thread represents a single forum thread
    Threads must be linked to a 'first post' which must have a title
    The title of the first post becomes the 'name' of the thread
    You can initialize the first post by passing it as an argument in the constructor
    If you do not initialize with the constructor then you must add one using add_first_post()
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
        self.topic = topic
        db.session.add(self)
        if first_post:
            self.add_first_post(first_post)
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

    def add_post(self, post):
        """
        Adds a post to the thread and notifies the users
        Automatically subscribes the user who posted to this thread
        :param post:
        """
        self.posts.append(post)
        self.notify()
        self.subbed.append(post.author)

    def add_topic(self, topic):
        self.topic = topic

    def notify(self):
        """
        Sets 'unseen' flags for every subscribed user
        """
        for sub in self.subbed_id:
            sub.unseen = True

    def __repr__(self):
        return "Thread " + str(self.name)


class Topic(db.Model):
    """
    Topics are tags that can be added to threads
    Users can subscribe to topics in order to be notified about any post made with that topic
    Topics must have unique names, attempting to create a topic with a name that already exists will throw an error
    You can do a check for a name manually and create the topic if the name doesn't exist...
    Alternatively use the class method get() to return or create the topic when appropriate
    todo: can we avoid the singleton shenanigans?
    """
    __tablename__ = 'Topic'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)
    # relationships
    threads = db.relationship("Thread", back_populates='topic')
    user_id = db.relationship('TopicSubscriptions', back_populates='topic')
    users = association_proxy('user_id', 'user', creator=lambda u: TopicSubscriptions(user=u))

    @classmethod
    def get(cls, name):
        q = Topic.query.filter_by(name=name).first()
        if q is None:
            return Topic(name)
        else:
            return q

    def __init__(self, name):
        if Topic.query.filter_by(name=name).first() is not None:
            raise ValueError("You have attempted to create a Topic with a pre-existing name, use Topic.get() instead")
        self.name = name
        db.session.add(self)
        db.session.commit()

    def add_thread(self, thread):
        self.threads.append(thread)

    def add_user(self, user):
        self.users.append(user)

    def notify(self):
        for user in self.user_id:
            user.unseen = True

    def __repr__(self):
        return "Topic " + self.name
