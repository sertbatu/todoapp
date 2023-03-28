from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, ValidationError, Optional, EqualTo, Length
from wtforms_components import DateTimeLocalField
from todoapp.models import User
from datetime import datetime

# Registrierungsformular
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Sign Up')

# Benutzernamenüberprüfung
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('That username is already taken. Please choose a different one.')

# Login-Formular
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Listen-Formular
class ListForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    submit = SubmitField('Create')

# Datumsvalidator
def future_date(form, field):
    if field.data and field.data <= datetime.now():
        raise ValidationError("The deadline must be a future date.")

# Item-Formular
class ItemForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    deadline = DateTimeLocalField('Deadline', format='%Y-%m-%dT%H:%M', validators=[Optional(), future_date])
    status = SelectField('Status', choices=[('Not Started', 'Not Started'), ('In Progress', 'In Progress'), ('Completed', 'Completed')], validators=[DataRequired()])
    submit = SubmitField('Create')

# EditItem-Formular
class EditItemForm(FlaskForm):
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=2, max=200)])
    deadline = DateTimeLocalField('Deadline', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    status = SelectField('Status', choices=[('Not Started', 'Not Started'), ('In Progress', 'In Progress'), ('Completed', 'Completed')])

