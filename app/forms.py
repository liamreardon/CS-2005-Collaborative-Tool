"""
forms.py holds the various classes of form types
The classes are implemented by using flask_wtf and wtforms
Classes:
	LoginForm: class for the login form 
	RegistrationForm: class for the signup/registration form
	ThreadForm: class for creating a new thread
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length

class LoginForm(FlaskForm):
	"""
	LoginForm is the class which creates the forms and variables for logging in a user.
	fields:
		username: StringField which takes in the a users username
		password: PasswordField which takes in a users password
		remember: BooleanField which creates a box a user can check to stay logged in

		Username and Password fields have InputRequired and Length constraints.
	"""
	username = StringField('username', validators=[InputRequired(), Length(min=4, max=20)])
	password = PasswordField('password', validators=[InputRequired(), Length(min=6, max=80)])
	remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
	"""
	RegistrationForm is the class which creates the forms and variables for signing up a user.
	fields:
		email: StringField which takes in a users email
		username: StringField which takes in the a users username
		password: PasswordField which takes in a users password
		
		Username and Password fields both have InputRequired and length constraints, and the email field has an email constraint
		which must be in format 'email@test.com'

	"""
	email = StringField('email', validators=[InputRequired(), Email(message='Invalid Email'), Length(max=50)])
	username = StringField('username', validators=[InputRequired(), Length(min=4, max=20)])
	password = PasswordField('password', validators=[InputRequired(), Length(min=6, max=80)])

class ThreadForm(FlaskForm):
	
        thread = StringField('Title:', validators=[InputRequired(), Length(min=1, max=128)])
        post = TextAreaField('Body:', validators=[InputRequired(), Length(min=1, max=1000)])
