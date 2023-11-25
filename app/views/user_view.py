# app/views/user_view.py

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import BooleanField, PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired

class UserProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    #role = SelectField('Role', choices=[('user', 'User'), ('admin', 'Admin')], default='user')
    role = SelectField('Role', choices=[('user', 'User'), ('admin', 'Admin')], default='user')
    language = SelectField('Language', choices=[('en', 'English'), ('es', 'Spanish')], validators=[DataRequired()])
    submit = SubmitField('Update Profile')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
