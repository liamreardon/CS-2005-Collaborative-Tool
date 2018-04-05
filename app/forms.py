"""forms.py docstring

This is the module that holds the various classes of form types. The classes are implemented by using flask_wtf and wtforms Python modules.

Notes
-----
    The following are merely a list of classes within this module; for further information on each class, refer to their respective classes' docstrings.
    
    Unless otherwise specified, class attribute fields may have any of the following constraints to ensure the classes function as intended:
        * InputRequired(): field cannot have no input.
        * Length(min, max): any input passed through the field must be between 'min' and 'max' length.

    Unless otherwise specified, assume that all inputs passed through each class attribute field are passed as String-type values, with the exception of attributes that do not accept inputs.

Classes
-------
LoginForm : FlaskForm
    class for the login form, to prompt users to login using their credentials
RegistrationForm : FlaskForm
    class for the signup/registration form, to allow users to create their own login credentials
ThreadForm : FlaskForm
    class for creating a new thread
PostForm : FlaskForm
    class for creating a new post to an existing thread
EditProfileForm : FlaskForm
    class for overwriting the user's username and/or creating a biography (i.e about me) for said user.
ChangePassword : FlaskForm
    class for overwriting the user's password
CreateGroupForm : FlaskForm
    class for creating a discussion group, along with it's title/topic and description
AddUserToGroup : FlaskForm
    class for appending a user to the list of users within a discussion group
AddThreadToGroup : FlaskForm
    class for creating a new thread within a discussion group

"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField, validators
from wtforms.validators import InputRequired, Email, Length, DataRequired


class LoginForm(FlaskForm):
    """LoginForm is the class which creates the forms and variables for logging in a user.
    
    Note
    ----
    'username' and 'password' fields have InputRequired() and Length() constraints.
    
    Attributes
    ----------
    username : StringField 
        Takes in a user's username
    password : PasswordField 
        Takes in a user's password
    remember : BooleanField 
        Creates a boolean variable who's value is determined by the user's input, which is then stored as a Boolean-type value.

    """
    username = StringField('', validators=[InputRequired(), Length(min=4, max=20)],
                           render_kw={"placeholder": "Username"})
    password = PasswordField('', validators=[InputRequired(), Length(min=6, max=80)],
                             render_kw={"placeholder": "Password"})
    remember = BooleanField('Remember Me')


class RegistrationForm(FlaskForm):
    """RegistrationForm is the class which creates the forms and variables for signing up a user.

    Notes
    -----
        The 'username' and 'password' fields both have InputRequired() and Length() constraints. 
        The 'email' field has an Email() constraint, which must be in the format 'email@test.com'.
        The 'password' field has DataRequired() and EqualTo() validators, which means that this field must contain data (cannot be blank) and must equal 'confirm' field, or else it will throw an error.

    Attributes
    ----------
    email : StringField 
        Takes in and stores a user's email
    username : StringField 
        Takes in and stores a user's username
    password : PasswordField 
        Takes in and stores a user's password
    confirm : PasswordField 
        Takes in the users password, which is then compared with the String type variable stored in the 'password' attribute

    """
    username = StringField('', [validators.Length(min=4, max=25)], render_kw={"placeholder": "Username"})
    email = StringField('', validators=[InputRequired(), Email(message='Invalid Email'), Length(max=50)], render_kw={"placeholder": "Email"})
    password = PasswordField('', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ], render_kw={"placeholder": "Password"})
    confirm = PasswordField('', render_kw={"placeholder": "Repeat Password"})


class ThreadForm(FlaskForm):
    """ThreadForm is a class which creates the forms and variables for creating a thread on the website.

    Note
    ----
        'thread', 'topic', and 'post' fields all have InputRequired() and Length() constraints.

    Attributes
    ----------
    thread : StringField 
        Takes in the title for a thread
    topic : StringField 
        Takes in the topic for a thread
    post : TextAreaField 
        Takes in the body of a post

    """
    thread = StringField('Title:', validators=[InputRequired(), Length(min=1, max=128)])
    topic = StringField('Topic:', validators=[InputRequired(), Length(min=1, max=128)])
    post = TextAreaField('Body:', validators=[InputRequired(), Length(min=1, max=1000)])


class PostForm(FlaskForm):
    """PostForm is a class which creates the forms and variables for creating a post on a thread.

    Note
    ----
        'post' field has an InputRequired() and a Length() constraint.

    Attributes
    ----------
    post : TextAreaField 
        Takes in the body of a post
    submit : SubmitField 
        Validates the submission of a post

    """
    post = TextAreaField('Add a post:', validators=[InputRequired(), Length(min=1, max=1000)])
    submit = SubmitField('Submit')


class EditProfileForm(FlaskForm):
    """EditProfileForm is the class which creates the forms and variables for overwriting the user's username and creating a biography (i.e about me) for a user's profile.

    Notes
    -----
        'username' field has a DataRequired() constraint
        'about_me' field has a Length() constraint.

    Attributes
    ----------
    username : StringField
        Takes in a user's new username
    about_me : TextAreaField
        Takes in the biography for the user
    submit : SubmitField
        Verifies the changes made to the user's username and the submission of the biography

    """
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')


class ChangePasswordForm(FlaskForm):
    """ChangePasswordForm is the class which creates the forms and variables for changing a user's password.
    
    Notes
    -----
        The 'password' field has DataRequired() and EqualTo() validators, which means that the field must contain data (cannot be blank) and must equal the data in the 'confirm' field, or else it will throw an error.

    Attributes
    ----------
    password : PasswordField 
        Takes in a user's new password
    confirm : PasswordField 
        Takes in the user's new password, which must be the same as the input passed through the 'password' field

    """
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')])

    confirm = PasswordField('Repeat Password')
    submit = SubmitField('Submit')


class CreateGroupForm(FlaskForm):
    """CreateGroupForm is a class that which creates the forms and variables for ccreating a discussion group.

    Notes
    -----
        'title' field has a Length() constraint, and is set to 'Title' by default
        'descr' field has a InputRequired() and Length() constraint, and is set to 'Group Description' by default.

    Attributes
    ----------
    title : StringField
        Takes in the title/topic of the discussion group
    descr : TextAreaField
        Takes in a brief summary/description of rules for the discussion group

    """
    title = StringField('', [validators.Length(min=4, max=64)], render_kw={'placeholder': 'Title'})
    descr = TextAreaField('', validators=[InputRequired(), Length(min=1, max=1000)], render_kw={'placeholder': 'Group Description'})

class AddUserToGroupForm(FlaskForm):
    """AddUserToGroupForm is a class which creates the forms and variables for adding a user into a discussion group

    Note
    ----
        'username' has a Length() constraint, and is set to 'Username' by default.

    Attribute
    ---------
    username : StringField
        Takes in the user's username

    """
    username = StringField('', [validators.Length(min=4, max=64)], render_kw={'placeholder': 'Username'})

class AddThreadToGroup(FlaskForm):
    """AddThreadToGroup is a class which creates the forms and variables for adding a thread to a discussion group

    Note
    ----
        'title', 'topic', and 'post' all have InputRequired() and Length() constraints

    Attributes
    ----------
    title : StringField
        Takes in the title of the thread
    topic : StringField
        Takes in the topic of the thread within the discussion group
    post : TextAreaField
        Takes in the original/first post in the thread

    """
    title = StringField('', validators=[InputRequired(), Length(min=1, max=128)], render_kw={"placeholder": "Title"})
    topic = StringField('', validators=[InputRequired(), Length(min=1, max=128)], render_kw={"placeholder": "Topic"})
    post = TextAreaField('', validators=[InputRequired(), Length(min=1, max=1000)], render_kw={"placeholder": "Text"})
