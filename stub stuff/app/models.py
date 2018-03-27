"""
models.py holds the information for all the persistent classes used in the project
Classes are implemented using Flask-SQLAlchemy
Classes:
    User: Holds all information about a specific user
    Post: A post represents a single post by a single user
    Thread: An ADT that contains references to many threads, and users subscribed to follow the thread
todo: consider refactoring all id and otherwise private variables to have a leading underscore
todo: implement topics and topic notification (maybe as a new object)
"""
from app import db
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.ext.associationproxy import association_proxy)

groups_joined = db.Table('groups_joined', db.Column('user_id', db.Integer, db.ForeignKey('User.username')), db.Column('group_id', db.Integer, db.ForeignKey('Group.id')))

# endregion

class User(UserMixin, db.Model):
    """
    A class to store user information
    Fields:
        id:                 Integer primary key
        username:           self explanatory
        password:           self explanatory
        email:              self explanatory
        groups:             list of groups the user is subscribed to

    """
    # fields
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(128))
    email = db.Column(db.String(128), index=True, unique=True)
    # relationships
    groups = db.relationships('Group', secondary="groups_joined", back_populate="joined")

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

class Group(db.Model):

        __tablename__ = "Group"
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(128))
        author_id = db.Column(db.Integer, db.ForeignKey('User.id'))
        group_id = db.Column(db.Integer, db.ForeginKey('Group.id'))
        users = db.relationship('Users', backref='group')

        def __init__(self, title, author_id):
            self.title = title
            self.author_id = author_id
            db.session.add(self)
            db.session.commit()
        
        #def add_user(self, User.username)

#another class for messages (?)

