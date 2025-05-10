from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already taken. Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email already registered. Please use a different email address.')

class SearchForm(FlaskForm):
    query = StringField('Search', validators=[DataRequired()])
    field = SelectField('Search Field', choices=[
        ('title', 'Journal Title'),
        ('issn', 'ISSN'),
        ('publisher', 'Publisher'),
        ('subject', 'Subject Area')
    ], default='title')
    submit = SubmitField('Search')

class JournalSearchForm(FlaskForm):
    issn = StringField('ISSN', validators=[DataRequired()])
    submit = SubmitField('Search Journal')

class SaveJournalForm(FlaskForm):
    notes = TextAreaField('Notes')
    submit = SubmitField('Save Journal')