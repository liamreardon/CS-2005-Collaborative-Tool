# Database models

#region imports
from app import db
from datetime import datetime
from flask_login import UserMixin
#endregion

# todo: examine 'association proxy' and see if it applies here
class ThreadSubscriptions(db.Model):
    """
    ThreadSubscriptions is an association table for users and threads
    An association table is used to allow for notifications
    fields:
        user:   reference to a user
        thread: the thread they're subscriped to
        unseen:  a boolean, True if user has unread posts
    """
    __tablename__ = 'thread_subscriptions'
    user_id = db.Column(db.Integer, db.ForeignKey('User.username'), primary_key=True)
    thread_id = db.Column(db.Integer, db.ForeignKey('Thread.id'), primary_key=True)
    db.Column('unseen', db.Boolean, default=False)
    user = db.relationship("User", back_populates="subs")
    thread = db.relationship("Thread", back_populates="subbed")


# endregion

class User(UserMixin, db.Model):
    """
    A class to store user information
    Fields:
        id:                 Integer primary key
        username:           self explanatory
        password:           self explanatory
        posts:              a list of all the posts this user has made
        subs:               a list of all the threads this user has subscriptions to
        email:              self explanatory
    """
    #fields
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(128))
    email = db.Column(db.String(128), index=True, unique=True)
    #relationships
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    # subs = db.relationship('Thread', secondary="thread_subscriptions", back_populates="subbed")
    subs = db.relationship('ThreadSubscriptions', back_populates='user')
class Post(db.Model):
    """
    A class to store user information
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
    author_id = db.Column(db.Integer,db.ForeignKey('User.id'))
    thread_id = db.Column(db.Integer,db.ForeignKey('Thread.id'))


class Thread(db.Model):
    """
    Thread represents a single forum thread
    Fields:
        id:     primary key
        posts:  a list of posts in the thread
        topic:  what the post is about
        subbed: users who are subscribed to the thread
    """
    __tablename__ = "Thread"
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(128))
    posts = db.relationship('Post', backref='thread')
    # subbed = db.relationship('User', secondary="thread_subscriptions", back_populates="subs")
    subbed = db.relationship('ThreadSubscriptions', back_populates='thread')