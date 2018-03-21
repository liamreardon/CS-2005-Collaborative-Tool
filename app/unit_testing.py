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
        u = User()
        u.username = "testUser" + str(n)
        u.password = "password" + str(n)
        u.email = "user" + str(n) + "@nowhere.com"
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


def make_thread(users=None, posts=None):
    if posts is not None:
        t1 = Thread(posts[0])
    else:
        t1 = Thread()
