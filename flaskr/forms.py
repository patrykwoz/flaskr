"""WTF forms for Idealog."""
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, SelectMultipleField, DateTimeField
from wtforms.validators import DataRequired, Email, Length

#############################################################################
# User Model FORMS
class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class UserSignupForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class UserEditForm(FlaskForm):
    """Form for editing users."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    


#############################################################################
#POST MODEL FORMS

class PostAddForm(FlaskForm):
    """Form for adding posts."""

    title = StringField('Post Title', validators=[DataRequired()])
    body = TextAreaField('Post Body', validators=[DataRequired(), Length(min=3)])


class KnowledgeBaseAddForm(FlaskForm):
    """Form for adding knowledge bases."""

    title = TextAreaField('Title', validators=[DataRequired()])

