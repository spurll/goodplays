from flask_wtf import FlaskForm
from wtforms import TextField, BooleanField, HiddenField, PasswordField, \
    DateField, SelectField, SelectMultipleField, TextAreaField
from wtforms.fields.html5 import IntegerField
from wtforms.validators import Required, Optional, Email, EqualTo, Length

from goodplays.models import Status, Platform


class LoginForm(FlaskForm):
    username = TextField('Username:', validators=[Required()])
    password = PasswordField('Password:', validators=[Required()])
    remember = BooleanField('Remember Me', default=True)


class SignupForm(FlaskForm):
    email = TextField('Email:', validators=[Email()])
    name = TextField('Display Name:', validators=[Required()])
    username = TextField('Username:', validators=[Required()])
    password = PasswordField('Password:', validators=[Length(min=16)])
    confirm = PasswordField('Confirm Password:', validators=[EqualTo('password')])


class EditGameForm(FlaskForm):
    name = TextField('Name', validators=[Required()])
    image_url = TextField('Image URL')
    gb_id = TextField('GB ID')
    hltb_id = TextField('HLTB ID')
    description = TextAreaField('Description')
    released = DateField('Released', format='%Y-%m-%d',
        validators=[Optional()])
    platforms = SelectMultipleField('Platforms', coerce=int, choices=[
        (p.id, p.name) for p in Platform.query.order_by(Platform.name).all()
    ])


class AddPlayForm(FlaskForm):
    started = DateField('Started', id='add-started', format='%Y-%m-%d',
        validators=[Optional()])
    finished = DateField('Finished', id='add-finished', format='%Y-%m-%d',
        validators=[Optional()])
    status = SelectField('Status', id='add-status', coerce=Status.coerce,
        choices=Status.choices())
    tags = TextField('Tags', id='add-tags')
    comments = TextField('Comments', id='add-comments')
    rating = HiddenField('Rating', id='add-rating')
    fave = HiddenField('Fave', id='add-fave')


class EditPlayForm(FlaskForm):
    id = HiddenField('ID', id='edit-id', validators=[Required()])
    started = DateField('Started', id='edit-started', format='%Y-%m-%d',
        validators=[Optional()])
    finished = DateField('Finished', id='edit-finished', format='%Y-%m-%d',
        validators=[Optional()])
    status = SelectField('Status', id='edit-status', coerce=Status.coerce,
        choices=Status.choices())
    tags = TextField('Tags', id='edit-tags')
    comments = TextField('Comments', id='edit-comments')
    rating = HiddenField('Rating', id='edit-rating')
    fave = HiddenField('Fave', id='edit-fave')

