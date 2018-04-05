"""
models.py is a Python module that holds information on all persistent classes used in the prototype.
Classes are implemented using Flask-SQLAlchemy

Classes
-------
ThreadSubscriptions : db.Model
    An associated table that allows for thread notifications for each individual user
TopicSubscriptions : db.Model
    An associated table that allows for topic-based thread notifications for each individual user. 
User : db.Model
    A single user and all their information
Thread : db.Model
    A series of posts made by many users in response to eachother
Post : db.Model
    A single post by a single user within a thread
Topic : db.Model
    Topics are user-submitted strings that are used to classify and group threads by topic
Group : db.Model
    Discussion group with a list of users and threads made within each respective group
"""

from app import db
from datetime import datetime, timedelta
from flask_login import UserMixin
from sqlalchemy import desc
from sqlalchemy.ext.associationproxy import association_proxy
from hashlib import md5


# region Association Classes
# Association classes are used by SQLAlchemy to manage many-to-many relationships
# Outside of this module they should not need to be referenced directly

class ThreadSubscriptions(db.Model):
    """
    ThreadSubscriptions is an association table for users and threads.
    An association table is used to allow for notifications to appear on the client side.
    
    Attributes
    ----------
    id : Integer
        Primary key
    user_id : Integer
        Reference to the currently logged in user
    thread_id : Integer 
        Reference to the thread the user is subscribed to
    user : User
        The user currently logged in
    thread : Thread
        The thread currently subscribed to by the user.
    unseen: Boolean 
        Returns True if user has unread posts, otherwise remain False
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
    TopicSubscriptions is an association table for users and discussion group topics.
    An association table is used to allow for notifications to appear on the client side.
    
    Attributes
    ----------
    id : Integer
        primary key
    user_id : Integer
        reference to the user currently logged in
    topic_id : Integer
        reference to the topic categorizing multiple threads
    user : User
        The user currently logged in
    topic : Topic
        The topic used to categorize multiple threads
    unseen: Boolean 
        True if user has unread posts pertaining to a particular topic, otherwise remain False
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


group_user_association = db.Table('group_user', db.metadata,
                                  db.Column('user_id', db.Integer, db.ForeignKey('User.id')),
                                  db.Column('group_id', db.Integer, db.ForeignKey('Group.id'))
                                  )


# endregion

class User(UserMixin, db.Model):
    """
    The User class is used to store user profile information, such as username, password,
    identification reference (id), email, and lists of posts/threads/discussion group topics related to the user.

    Attributes
    ----------
    id : Integer 
        primary key
    username : String
        User's identification name as it appears on the website.
    password : String
        User's password for logging onto the site.
    email : String
        User's email address
    about_me : Text
        A section of the user profile dedicated to a biography about said user
    posts : Post
        A list of all the posts this user has made
    sub_id : Integer
        A reference to the list of threads the user has subscriptions to
    subs : ThreadSubscriptions
        A list of all the threads this user has subscriptions to
    topic_id : Integer
        A reference to the list of thread topics the user has subscriptions to
    topics : TopicSubscriptions
        A list of thread topics the user has subscriptions to

    """
    # fields
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(128))
    email = db.Column(db.String(128), index=True, unique=True)
    about_me = db.Column(db.Text())
    # relationships
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    sub_id = db.relationship('ThreadSubscriptions', back_populates='user')
    subs = association_proxy('sub_id', 'thread', creator=lambda t: ThreadSubscriptions(thread=t))
    topic_id = db.relationship('TopicSubscriptions', back_populates='user')
    topics = association_proxy('topic_id', 'topic', creator=lambda t: TopicSubscriptions(topic=t))
    groups = db.relationship(
        "Group",
        secondary=group_user_association,
        back_populates="users")

    def __init__(self, username, password, email, **kwargs):
        """
        Constructor for User class. Adds the required fields and commits the object to the database.
        Parameters
        ----------
        username : String
            Human readable string showing the user's identifiable username 
        password : String 
            Human readable string acting as the user's password for accessing their user profile on the website
        email : String
            Human readable string depecting the user's respective email address.
        **kwargs
            Arbitrary keyword arguements.
        """

        self.username = username
        self.email = email
        self.password = password
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.add(self)
        db.session.commit()

    def has_notifications(self):
        """returns True if the user has unseen notifications"""
        for sub in self.sub_id:
            if sub.unseen:
                return True
        return False

    # todo this needs to be tested
    def get_unseen_threads(self):
        """returns True if the user has unseen threads"""
        threads = []
        for sub in self.sub_id:
            if sub.unseen:
                threads.append(sub.thread)
        return threads

    # todo this needs to be tested
    def get_unseen_topics(self):
        """returns True if the user has unseen topics"""
        topics = []
        for topic in self.topic_id:
            if topic.unseen:
                topics.append(topic.thread)
        return topics

    def get_feed(self):
        """returns a set of threads created by other users, ordered latest first"""
        feed = set()
        for thread in self.subs:
            for thread_post in thread.posts:
                if thread_post.author == self:
                    continue
                feed.add(thread_post)
        for topic in self.topics:
            for topic_thread in topic.threads:
                for topic_post in topic_thread.posts:
                    if topic_post.author == self:
                        continue
                    feed.add(topic_post)
        feed = sorted(list(feed), key=lambda post: post.timestamp, reverse=True)
        return feed

    def avatar(self, size):
        """returns an adjusted profile avatar for a user's profile"""
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.cs2005group.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def __repr__(self):
        """
        returns an error message should a user not have a username;
        otherwise, return the user's username as a String
        """
        usrname = "USERNAME NOT SET"
        if self.username is not None:
            usrname = self.username
        return self.username


class Post(db.Model):
    """
    The Post class is used to store user-created post information
    
    Attributes
    ----------
    id : Integer 
        Primary key
    title : String
        Title of the post
    text: Text
        Content of the post
    timestamp : DateTime
        UTC time the post was made
    author_id : Integer
        reference to/relationship with User (1:n)
    thread_id : Integer
        reference to/relationship with Thread (1:n)
    """

    __tablename__ = "Post"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    text = db.Column(db.Text())
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    # relationships
    author_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    thread_id = db.Column(db.Integer, db.ForeignKey('Thread.id'))

    def get_time(self, relative=True):
        """
        Gets the time as a nicely formatted string

        Parameters
        ----------
        relative: Boolean
            Time as a formatted string

        Returns
        -------
        String
            If True, display date relative to current time, eg. "2 hours from now".
            If False, display data as human readable string, eg. ""
        """

        diff = datetime.utcnow() - self.timestamp
        if not relative:
            dt = self.timestamp.strftime('%b %d, %Y at %X')
            return dt
        # relative time
        if diff < timedelta(hours=1):
            return str(int(diff.seconds / 60)) + " minutes ago"
        if diff < timedelta(hours=24):
            return str(int(diff.seconds / 3600)) + " hours ago"
        else:
            return str(int(diff.days)) + " days ago"

    def __init__(self, user, text, thread=None, title=None):
        """
        Constructor for Post class. Adds the required fields and commits the object to the database.
        
        Notes
        -----
            If the reference to a thread is provided this post is automatically appended. Should the passed thread have
            no posts, this post will be considered the first post and initialize the thread.
            Threads can only be initialized with posts that have a title;
            otherwise, the post will be appended as a child post to the thread
            If no thread is passed, then this post must be added using add_post or add_first_post on the thread elsewhere
            
        Parameters
        ----------
        user : String
            Human readable string showing the user's identifiable username 
        text : String
            Human readable string acting as the body of the post
        thread : Thread
            Object indicating which thread the post is being made in
        title : String
            Human readable string acting as the title of the post
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
    The Thread class represents a single, user-created forum thread.

    Notes
    -----
        Threads must be linked to a 'first post', which must have a title and ultimately the 'name' of the thread.
        The first post can be initialized by passing it as an argument in the constructor;
        otherwise, use the add_first_post() method.
    
    Attributes
    ----------
    id : Integer 
        Primary key
    name : String
        Title of the post thread.
    posts : Post
        A list of posts in the thread
    topic_id : Integer
        Reference to the topic of the thread.
    topic : Topic
        The topic associated with the thread
    subbed_id : Integer
        Reference to the list of users subscribed to the thread
    subbed : ThreadSubscriptions
        List of users subscribed to the thread
    group_id : Integer
        Reference to the group associated with the thread
    group : Group
        The group associated with the thread
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
    group_id = db.Column(db.Integer, db.ForeignKey('Group.id'))
    group = db.relationship('Group', back_populates='threads')

    def __init__(self, first_post=None, topic=None):
        """
        Constructor for Thread class. Adds the required fields and commits the object to the database.
        Note
        ----
            Should the first_post parameter not equal None, then the title of the thread is set to the post title,
            and the user is automatically subscribed to the thread.

        Parameters
        ----------
        first_post : Post
            The first/original post of the thread 
        topic : Topic
            The user-submitted topic associated with the post thread
        
        """

        self.topic = topic
        db.session.add(self)
        if first_post:
            self.add_first_post(first_post)
        db.session.commit()

    def add_first_post(self, first_post):
        """
        Adds the first post to the top of the thread, then sets the title of the thread to the title of the post and
        subscribes the user to the thread automatically.

        Parameter
        ---------
        first_post : Post
            the first/original post of the thread

        """

        self.name = first_post.title
        self.posts = [first_post]
        self.subbed = [first_post.author]

    def add_post(self, post):
        """
        Adds a post to the thread and notifies the users, while automatically subscribes the user who posted to this thread

        Parameter
        ---------
        post : Post
            The user-created post, to be added to the thread
        
        """

        self.posts.append(post)
        self.notify()
        self.subbed.append(post.author)

    def add_topic(self, topic):
        """
        Adds a topic to the thread

        Parameter
        ---------
        topic : Topic
            The user-created topic, to be attached to the thread.

        """

        self.topic = topic

    def notify(self):
        """Sets 'unseen' flags for every subscribed user"""
        for sub in self.subbed_id:
            sub.unseen = True

    def __repr__(self):
        """Represents and returns the name of the thread as a string"""
        return "Thread " + str(self.name)

    def is_visible_by(self, usr):
        """Returns true if this post is public, or if the user is a member of the group"""
        if self.group is None:
            return True
        if usr not in self.group.users:
            return False
        return True


class Topic(db.Model):
    """
    The Topic class represents user-created tags that can be added to threads, which users can then
    subscribe to in order to be notified about any post made with that topic.

    Notes
    -----
    Topics must have unique names; attempting to create a topic with a name that already exists will throw an error.
    You can do a check for a name manually and create the topic if the name doesn't exist.
    Alternatively, use the class method get() to return or create the topic when appropriate

    Attributes
    ----------
    id : Integer
        Primary key
    name : String
        Human readable string representing the name of the topic
    threads : Thread
        The list of threads that the topic will be associated with
    user_id : Integer
        Reference to the list of users subscribed to the topic
    users : User
        The list of users subscribed to the topic
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
        """Retrieve and return the topic by its name, otherwise raise an error"""
        q = Topic.query.filter_by(name=name).first()
        if q is None:
            return Topic(name)
        else:
            return q

    def __init__(self, name):
        """
        Constructor for Topic class. Adds the required fields and commits the object to the database.
        Note
        ----
        If the name of the topic is already used for another topic object, then raise a ValueError.

        Parameter
        ---------
        name : String
            Name of the user-defined topic to be associated with a thread.

        """

        if Topic.query.filter_by(name=name).first() is not None:
            raise ValueError("You have attempted to create a Topic with a pre-existing name, use Topic.get() instead")
        self.name = name
        db.session.add(self)
        db.session.commit()

    def add_thread(self, thread):
        """Creates a new thread object, appends it into a list of threads"""
        self.threads.append(thread)

    def add_user(self, user):
        """Creates a new user object, appends it into a list of users subscribed to the topic"""
        self.users.append(user)

    def notify(self):
        """Send notifications for users in the list of subscribed users whenever there are unseen threads related to the topic"""
        for user in self.user_id:
            user.unseen = True

    def __repr__(self):
        """Represents and returns the Topic name as a string"""
        return "Topic " + self.name


class Group(db.Model):
    """
    The Group class represents user-created discussion groups that are capable of creating their own threads,
    with the exception of a few select users are capable of accessing any of these group-specific threads.
    Attributes
    ----------
    id : Integer
        Primary key
    name : String
        Title of the discussion group
    descr : Text
        Brief description/summary of rules for the discussion group
    threads : Thread
        List of threads that exist within the discussion group
    users : User
        List of users that have access to the discussion group

    """

    __tablename__ = 'Group'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    descr = db.Column(db.Text())
    # relationships
    threads = db.relationship("Thread", back_populates='group')
    users = db.relationship(
        "User",
        secondary=group_user_association,
        back_populates="groups")

    def __init__(self, name, descr, user=None):
        """
        Constructor for Group class.  Adds the required fields and commits the object to the database.

        Note
        ----
        If there is no user passed initially (i.e user = None), then the add_user() and add_users() methods are to be
        referred to add users into the discussion group. Otherwise, the constructor method will create a group with
        no members in it.

        Parameters
        ----------
        name : String
            Name/Title of the discussion group
        descr : String
            Brief description/summary of rules for the discussion group
        user : String
            The user to be added to the discussion group
        """
        db.session.add(self)
        self.name = name
        self.descr = descr
        if user is not None:
            self.add_user(user)
        db.session.commit()

    def add_user(self, usr):
        """Adds a single user to the discussion group"""
        self.users.append(usr)

    def add_users(self, users):
        """Adds a list of users to the discussion group"""
        for usr in users:
            self.add_user(usr)

    def __repr__(self):
        """Represents and returns the title of the discussion group as a string"""
        return "Group " + self.name
