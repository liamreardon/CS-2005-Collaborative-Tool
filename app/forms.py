"""
forms.py holds the various classes of form types
The classes are implemented by using flask_wtf and wtforms
Classes:
	LoginForm: class for the login form 
	RegistrationForm: class for the signup/registration form
	ThreadForm: class for creating a new thread
	PostForm: class for creating a new post
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField, validators
from wtforms.validators import InputRequired, Email, Length, DataRequired


class LoginForm(FlaskForm):
    """
    LoginForm is the class which creates the forms and variables for logging in a user.
    fields:
        username: StringField which takes in the a users username
        password: PasswordField which takes in a users password
        remember: BooleanField which creates a box a user can check to stay logged in
        
        Username and Password fields have InputRequired and Length constraints.
    """
    username = StringField('', validators=[InputRequired(), Length(min=4, max=20)],
                           render_kw={"placeholder": "Username"})
    password = PasswordField('', validators=[InputRequired(), Length(min=6, max=80)],
                             render_kw={"placeholder": "Password"})
    remember = BooleanField('Remember Me')


class RegistrationForm(FlaskForm):
    """
    RegistrationForm is the class which creates the forms and variables for signing up a user.
    fields:
        email: StringField which takes in a users email
        username: StringField which takes in the a users username
        password: PasswordField which takes in a users password
        confirm: PasswordField which takes in the users password which must be the same as 'password' field

        Username and Password fields both have InputRequired and length constraints, and the email field has an email constraint
        which must be in format 'email@test.com'.
        The 'password' field has DataRequired() and EqualTo() validators, which means that the this field must
        contain data (cannot be blank) and must equal 'confirm' field, or else it will throw an error.

    """
    username = StringField('', [validators.Length(min=4, max=25)], render_kw={"placeholder": "Username"})
    email = StringField('', validators=[InputRequired(), Email(message='Invalid Email'), Length(max=50)],
                        render_kw={"placeholder": "Email"})
    password = PasswordField('', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ], render_kw={"placeholder": "Password"})
    confirm = PasswordField('', render_kw={"placeholder": "Repeat Password"})


class ThreadForm(FlaskForm):
    """
    ThreadForm is a class which creates the forms and variables for creating a thread.
    fields:
        thread: StringField which takes in the title for a thread
        topic: StringField which takes in the topic for a thread
        post: TextAreaField which takes in the body of a post
    
        Thread, topic, and post fields all have InputRequired and length constraints.
    """
    thread = StringField('Title:', validators=[InputRequired(), Length(min=1, max=128)])
    topic = StringField('Topic:', validators=[InputRequired(), Length(min=1, max=128)])
    post = TextAreaField('Body:', validators=[InputRequired(), Length(min=1, max=1000)])


class PostForm(FlaskForm):
    """
    PostForm is a class which creates the forms and variables for creating a post.
    fields:
        post: TextAreaField which takes in the body of a post
        submit: SubmitField which validates the post

        Post field has an InputRequired and length constraint.
    """
    post = TextAreaField('Add a post:', validators=[InputRequired(), Length(min=1, max=1000)])
    submit = SubmitField('Submit')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')


class ChangePasswordForm(FlaskForm):
    """
    ChangePasswordForm is the class which creates the forms and variables for changing a users password.
    fields:
        password: PasswordField which takes in a users password
        confirm: PasswordField which takes in the users password which must be the same as 'password' field

        The 'password' field has DataRequired() and EqualTo() validators, which means that the this field must
        contain data (cannt be blank) and must equal 'confirm' field, or else it will throw an error.
    """
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')])

    confirm = PasswordField('Repeat Password')
    submit = SubmitField('Submit')


class CreateGroupForm(FlaskForm):
    """
    TODO: this
    """
    title = StringField('', [validators.Length(min=4, max=64)], render_kw={'placeholder': 'Title'})
    descr = TextAreaField('', validators=[InputRequired(), Length(min=1, max=1000)],
                          render_kw={'placeholder': 'Group Description'})

class AddUserToGroupForm(FlaskForm):
    """
    todo: this
    """
    username = StringField('', [validators.Length(min=4, max=64)], render_kw={'placeholder': 'Username'})

class AddThreadToGroup(FlaskForm):
    """
    Adds a new thread to a user group
    """
    title = StringField('', validators=[InputRequired(), Length(min=1, max=128)], render_kw={"placeholder": "Title"})
    topic = StringField('', validators=[InputRequired(), Length(min=1, max=128)], render_kw={"placeholder": "Topic"})
    post = TextAreaField('', validators=[InputRequired(), Length(min=1, max=1000)], render_kw={"placeholder": "Text"})
