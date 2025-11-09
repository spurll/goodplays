from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, HiddenField, PasswordField, \
    DateField, SelectField, SelectMultipleField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Optional, Email, EqualTo, Length

from goodplays import app
from goodplays.models import Status, Platform


with app.app_context():
    available_platforms = [
        (p.id, p.name) for p in Platform.query.order_by(Platform.name).all()
    ]


class LoginForm(FlaskForm):
    username = StringField('Username:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])
    remember = BooleanField('Remember Me', default=True)


class SignupForm(FlaskForm):
    email = StringField('Email:', validators=[Email()])
    name = StringField('Display Name:', validators=[DataRequired()])
    username = StringField('Username:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[Length(min=16)])
    confirm = PasswordField('Confirm Password:', validators=[EqualTo('password')])


class EditGameForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    image_url = StringField('Image URL')
    gb_id = StringField('GB ID')
    steam_id = StringField('Steam ID')
    hltb_id = StringField('HLTB ID')
    description = TextAreaField('Description')
    released = DateField('Released', format='%Y-%m-%d',
        validators=[Optional()])
    platforms = SelectMultipleField('Platforms', coerce=int,
        choices=available_platforms)


class AddPlayForm(FlaskForm):
    started = DateField('Started', id='add-started', format='%Y-%m-%d',
        validators=[Optional()])
    finished = DateField('Finished', id='add-finished', format='%Y-%m-%d',
        validators=[Optional()])
    status = SelectField('Status', id='add-status', coerce=Status.coerce,
        choices=Status.choices())
    tags = StringField('Tags', id='add-tags')
    comments = StringField('Comments', id='add-comments')
    rating = HiddenField('Rating', id='add-rating')
    fave = HiddenField('Fave', id='add-fave')


class EditPlayForm(FlaskForm):
    id = HiddenField('ID', id='edit-id', validators=[DataRequired()])
    started = DateField('Started', id='edit-started', format='%Y-%m-%d',
        validators=[Optional()])
    finished = DateField('Finished', id='edit-finished', format='%Y-%m-%d',
        validators=[Optional()])
    status = SelectField('Status', id='edit-status', coerce=Status.coerce,
        choices=Status.choices())
    tags = StringField('Tags', id='edit-tags')
    comments = StringField('Comments', id='edit-comments')
    rating = HiddenField('Rating', id='edit-rating')
    fave = HiddenField('Fave', id='edit-fave')

