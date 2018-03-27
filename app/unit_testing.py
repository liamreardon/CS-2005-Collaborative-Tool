from app import *
from app.models import *


def drop_tables():
    """
    Drop all tables
    """
    db.reflect()
    db.drop_all()


def init_db():
    drop_tables()
    db.create_all()


def make_users():
    """
    Makes several user objects for testing
    """
    users = []
    for n in range(5):
        username = "testUser" + str(n)
        password = "password" + str(n)
        email = "user" + str(n) + "@nowhere.com"
        u = User(username, password, email)
        u.about_me = "I'm a test user! I don't really exist."
        users.append(u)
    db.session.add_all(users)
    db.session.commit()
    return users


def make_posts(users=None):
    """
    Makes several post objects for testing
    """
    posts = []
    for n in range(5):
        p = Post()
        p.title = "Post " + str(n)
        p.text = "Text text for post # " + str(n)
        if users is not None:
            p.author = users[n]
        posts.append(p)
    db.session.add_all(posts)
    db.session.commit()
    return posts


def make_thread(users=None, posts=None, topics=None):
    if posts is not None and topics is not None:
        t1 = Thread(first_post=posts[0], topic=topics[0])
    if posts is not None:
        t1 = Thread(posts[0])
    else:
        t1 = Thread()


def make_topics():
    topics = []
    for n in range(3):
        t = Topic(name="topic" + str(n))
        topics.append(t)
    return topics
