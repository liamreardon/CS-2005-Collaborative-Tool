import os
from app import app
import unittest
import tempfile
from app.config import Config, TestConfig
from app.models import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user


class UnitTest(unittest.TestCase):
    TESTING = True

    def setUp(self):
        """
        setup changes the config to a temporary test config
        wtform authentication is bypassed
        the database path is changed to test.db
        the database is then initialized
        """
        app.config.from_object(TestConfig)
        app.config['WTF_CSRF_ENABLED'] = False
        app.testing = True
        self.app = app.test_client()
        db.create_all()
        # login for wtforms

    def tearDown(self):
        """
        teardown removes the database session, drops the table, and restores the original config
        """
        db.session.remove()
        db.drop_all()
        app.config.from_object(Config)

    def login(self, username, password):
        """
        a conveinence method that creates a user then logs them in using a post method to the login page
        the user will be redirected to the home page after this method is called
        """
        hashed_password = generate_password_hash(password, method='sha256')
        user = User(username=username, email='test_email', password=hashed_password)
        return self.app.post('/login', data=dict(
            username=username,
            password=password,
            form=''
        ), follow_redirects=True)

    # region Class Creation Tests

    def test_empty_db(self):
        """
        Asserts that queries from initialized databases all return empty
        """
        self.assertTrue(User.query.all() == [])
        self.assertTrue(Post.query.all() == [])
        self.assertTrue(Thread.query.all() == [])
        self.assertTrue(Topic.query.all() == [])
        self.assertTrue(Group.query.all() == [])

    def test_create_User(self):
        """
        Creates a user and tests the attributes that return from the DB are accurate
        """
        usr = User('test_username', 'test_password', 'test_email')
        usr.about_me = 'test_about_me'
        id = usr.id
        usr = User.query.filter_by(id=id).first()
        self.assertTrue(usr.username == 'test_username')
        self.assertTrue(usr.password == 'test_password')
        self.assertTrue(usr.email == 'test_email')
        self.assertTrue(usr.about_me == 'test_about_me')

    def test_create_Post(self):
        """
        Creates a post and tests the attributes that return from the DB are accurate
        """
        usr = User('test_username', 'test_password', 'test_email')
        post = Post(usr, 'test_post_text', title='test_post_title')
        id = post.id
        post = Post.query.filter_by(id=id).first()
        self.assertTrue(post.text == 'test_post_text')
        self.assertTrue(post.title == 'test_post_title')

    def test_create_Thread(self):
        """
        creates a thread and tests the attributes that return from the DB are accurate
        """
        thread = Thread()
        thread.name = 'test_thread'
        id = thread.id
        thread = Thread.query.filter_by(id=id).first()
        self.assertTrue(thread.name == 'test_thread')

    def test_create_Topic(self):
        topic = Topic('test_topic')
        id = topic.id
        topic = Topic.query.filter_by(id=id).first()
        self.assertTrue(topic.name == 'test_topic')

    def test_create_Group(self):
        group = Group('test_group', 'test_group_description')
        id = group.id
        group = Group.query.filter_by(id=id).first()
        self.assertTrue(group.name == 'test_group')
        self.assertTrue(group.descr == 'test_group_description')

    # endregion

    # region Class Association Tests
    def test_user_post_relationship(self):
        """
        Associates a user and a post and checks the bidirectional relationship is working
        """
        usr = User('test_username', 'test_password', 'test_email')
        post = Post(usr, 'test_post_text', title='test_post_title')
        self.assertTrue(post in usr.posts)
        self.assertTrue(post.author == usr)

    def test_user_thread_relationship(self):
        usr = User('test_username', 'test_password', 'test_email')
        thread = Thread()
        thread.subbed.append(usr)
        self.assertTrue(thread in usr.subs)
        self.assertTrue(usr in thread.subbed)

    def test_user_topic_relationship(self):
        usr = User('test_username', 'test_password', 'test_email')
        topic = Topic('test_topic')
        topic.users.append(usr)
        self.assertTrue(usr in topic.users)
        self.assertTrue(topic in usr.topics)

    def test_user_group_relationship(self):
        usr = User('test_username', 'test_password', 'test_email')
        group = Group('test_group', 'test_group_description')
        group.users.append(usr)
        self.assertTrue(usr in group.users)
        self.assertTrue(group in usr.groups)

    def test_post_thread_relationship(self):
        usr = User('test_username', 'test_password', 'test_email')
        post = Post(usr, 'test_post_text', title='test_post_title')
        thread = Thread(post)
        self.assertTrue(post in thread.posts)
        self.assertTrue(post.thread == thread)

    def test_thread_topic_relationship(self):
        topic = Topic('test_topic')
        thread = Thread(topic=topic)
        self.assertTrue(thread.topic == topic)
        self.assertTrue(thread in topic.threads)

    def test_thread_group_relationship(self):
        group = Group('test_group', 'test_group_description')
        thread = Thread()
        group.threads.append(thread)
        self.assertTrue(thread in group.threads)
        self.assertTrue(thread.group == group)

    # endregion

    # region Routing Tests

    def test_sign_in_redirect(self):
        """
        tests that the home directory redirects to the Login page when the user isn't logged in
        """
        response = self.app.get('/')
        self.assertTrue(b'<title>Login</title>' in response.data)

    def test_home_page(self):
        """
        tests that the user is redirected to the homepage after a successful login
        """
        rv = self.login('test_user', 'test_password')
        self.assertTrue(b'<title>\n    Home\n</title>' in rv.data)

    # endregion

    #region Post Request Tests
    #todo: these
    #endregion


if __name__ == '__main__':
    print("Testing")
    unittest.main()
