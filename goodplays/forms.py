from flask_wtf import FlaskForm
from wtforms import TextField, BooleanField, HiddenField, PasswordField, DateField, SelectField
from wtforms.fields.html5 import IntegerField
from wtforms.validators import Required, NumberRange

from goodplays.models import Status


class LoginForm(FlaskForm):
    username = TextField('Username', validators=[Required()])
    password = PasswordField('Password', validators=[Required()])
    remember = BooleanField('Remember Me', default=False)


class AddPlayForm(FlaskForm):
    started = DateField('Started')
    finished = DateField('Finished')
    status = SelectField('Status', choices=[
        (Status.interested, 'Interested'),
        (Status.playing, 'Playing'),
        (Status.completed, 'Completed'),
        (Status.hundred, '100%'),
        (Status.abandoned, 'Abandoned'),
    ])
    tags = TextField('Tags')
    comments = TextField('Comments')
    rating = SelectField('Rating', choices=[
        (0, ''),
        (2, u'\u2605' + u'\u2606' * 4),
        (4, u'\u2605' * 2 + u'\u2606' * 3),
        (6, u'\u2605' * 3 + u'\u2606' * 2),
        (8, u'\u2605' * 4 + u'\u2606' * 1),
        (10, u'\u2605' * 5),
    ])


class EditPlayForm(FlaskForm):
    id = HiddenField('ID', validators=[Required()])
    started = DateField('Started')
    finished = DateField('Finished')
    status = SelectField('Status', choices=[
        (Status.interested, 'Interested'),
        (Status.playing, 'Playing'),
        (Status.completed, 'Completed'),
        (Status.hundred, '100%'),
        (Status.abandoned, 'Abandoned'),
    ])
    tags = TextField('Tags')
    comments = TextField('Comments')
    rating = SelectField('Rating', choices=[
        (0, ''),
        (2, u'\u2605' + u'\u2606' * 4),
        (4, u'\u2605' * 2 + u'\u2606' * 3),
        (6, u'\u2605' * 3 + u'\u2606' * 2),
        (8, u'\u2605' * 4 + u'\u2606' * 1),
        (10, u'\u2605' * 5),
    ])

