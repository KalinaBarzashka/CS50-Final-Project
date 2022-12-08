from wtforms import Form, BooleanField, StringField, TextAreaField, PasswordField, IntegerField, RadioField, validators
from wtforms.validators import Length, InputRequired, DataRequired, EqualTo

class RegistrationForm(Form):
    username = StringField('Username', validators=[Length(min=4, max=25), InputRequired(message="Enter your username please!")])
    password = PasswordField('Password', validators=[
        DataRequired(),
        EqualTo('confirmation', message='Passwords must match')
    ])
    confirmation = PasswordField('Confirm Password', validators=[
        DataRequired()
    ])

