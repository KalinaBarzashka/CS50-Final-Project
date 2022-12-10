from wtforms import Form, DateField, StringField, TextAreaField, PasswordField, IntegerField, FloatField, validators
from wtforms.validators import Length, InputRequired, DataRequired, EqualTo
from datetime import datetime, date

class RegistrationForm(Form):
    username = StringField('Username', validators=[Length(min=4, max=25), InputRequired(message="Enter your username please!")])
    password = PasswordField('Password', validators=[
        DataRequired(),
        EqualTo('confirmation', message='Passwords must match')
    ])
    confirmation = PasswordField('Confirm Password', validators=[
        DataRequired()
    ])

class LoginForm(Form):
    username = StringField('Username', validators=[Length(min=4, max=25), InputRequired(message="Enter your username please!")])
    password = PasswordField('Password', validators=[
        DataRequired()
    ])

class AgencyForm(Form):
    name = StringField('Name', validators=[Length(min=5), InputRequired(message="Enter name of the agency please!")])
    department = StringField('Department', validators=[Length(min=5), InputRequired(message="Enter department of the agency please!")])

class StateForm(Form):
    name = StringField('Name', validators=[Length(min=4), InputRequired(message="Enter name of the state please!")])

class MonumentForm(Form):
    name = StringField('Name', validators=[Length(min=5), InputRequired(message="Enter name of the monument please!")])
    description = TextAreaField('Description', validators=[InputRequired(), Length(max=6000)])
    latitude = FloatField('Latitude', validators=[InputRequired()])
    longitude = FloatField('Longitude', validators=[InputRequired()])
    imageurl = StringField('Image URL', validators=[Length(min=15), InputRequired()])
    dateestablished = DateField('Date Established', format='%Y-%m-%d', default=datetime.now())
    acres = StringField('Total Acres', validators=[InputRequired()])