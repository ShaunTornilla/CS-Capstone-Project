from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,   
    BooleanField )
from wtforms.validators import (
    DataRequired,
    Email )

class LoginForm(FlaskForm):
    # username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                            validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                            validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log in')

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name',
                                validators=[DataRequired()])
    last_name = StringField('Last Name',
                                validators=[DataRequired()])
    email = StringField('Email',
                                validators=[DataRequired(), Email()])
    submit = SubmitField('Register')