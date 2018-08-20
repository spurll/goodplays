from flask_wtf import FlaskForm
from wtforms import TextField, BooleanField, HiddenField, PasswordField
from wtforms.fields.html5 import IntegerField
from wtforms.validators import Required, NumberRange


class LoginForm(FlaskForm):
    username = TextField("Username", validators=[Required()])
    password = PasswordField("Password", validators=[Required()])
    remember = BooleanField("Remember Me", default=False)


class TemplateForm(FlaskForm):
    hidden = HiddenField("Hidden", validators=[Required()])
    integer = IntegerField("Int", default=0, validators=[NumberRange(min=0)])
