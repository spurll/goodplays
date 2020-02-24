from flask_wtf import FlaskForm
from wtforms import TextField, BooleanField, HiddenField, PasswordField, DateField
from wtforms.fields.html5 import IntegerField
from wtforms.validators import Required, NumberRange

from goodplays.models import Status


class LoginForm(FlaskForm):
    username = TextField('Username', validators=[Required()])
    password = PasswordField('Password', validators=[Required()])
    remember = BooleanField('Remember Me', default=False)


class PlayForm(FlaskForm):
    started = DateField('Started')
    finished = DateField('Finished')
    status = SelectField('Status', choices=[
        ('Interested', Status.interested),
        ('Playing', Status.playing),
        ('Completed', Status.completed),
        ('100%', Status.hundred),
        ('Abandoned', Status.abandoned),
    ])
    tags = TextField('Tags')
    comments = TextField('Comments')
    rating = SelectField('Rating', choices=[
        ('None', 0),
        ('&#9733;', 2),
        ('&#9733;' * 2, 4),
        ('&#9733;' * 3, 6),
        ('&#9733;' * 4, 8),
        ('&#9733;' * 5, 10),
    ])

class EditPlayForm(FlaskForm):
    id = HiddenField('ID', validators=[Required()])
    started = DateField('Started')
    finished = DateField('Finished')
    status = SelectField('Status', choices=[
        ('Interested', Status.interested),
        ('Playing', Status.playing),
        ('Completed', Status.completed),
        ('100%', Status.hundred),
        ('Abandoned', Status.abandoned),
    ])
    tags = TextField('Tags')
    comments = TextField('Comments')
    rating = SelectField('Rating', choices=[
        ('None', 0),
        ('&#9733;', 2),
        ('&#9733;' * 2, 4),
        ('&#9733;' * 3, 6),
        ('&#9733;' * 4, 8),
        ('&#9733;' * 5, 10),
    ])

