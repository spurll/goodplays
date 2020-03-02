from flask_wtf import FlaskForm
from wtforms import TextField, BooleanField, HiddenField, PasswordField, DateField, SelectField
from wtforms.fields.html5 import IntegerField
from wtforms.validators import Required, NumberRange, Optional

from goodplays.models import Status


class LoginForm(FlaskForm):
    username = TextField('Username', validators=[Required()])
    password = PasswordField('Password', validators=[Required()])
    remember = BooleanField('Remember Me', default=False)


class AddPlayForm(FlaskForm):
    started = DateField('Started', id='add-started', format='%Y-%m-%d',
        validators=[Optional()])
    finished = DateField('Finished', id='add-finished', format='%Y-%m-%d',
        validators=[Optional()])
    status = SelectField('Status', id='add-status', coerce=Status.coerce,
        choices=Status.choices())
    tags = TextField('Tags', id='add-tags')
    comments = TextField('Comments', id='add-comments')
    rating = SelectField('Rating', id='add-rating', coerce=int, choices=[
        (0, ''),
        (2, u'\u2605' + u'\u2606' * 4),
        (4, u'\u2605' * 2 + u'\u2606' * 3),
        (6, u'\u2605' * 3 + u'\u2606' * 2),
        (8, u'\u2605' * 4 + u'\u2606' * 1),
        (10, u'\u2605' * 5),
    ])


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
    rating = SelectField('Rating', id='edit-rating', coerce=int, choices=[
        (0, ''),
        (2, u'\u2605' + u'\u2606' * 4),
        (4, u'\u2605' * 2 + u'\u2606' * 3),
        (6, u'\u2605' * 3 + u'\u2606' * 2),
        (8, u'\u2605' * 4 + u'\u2606' * 1),
        (10, u'\u2605' * 5),
    ])

