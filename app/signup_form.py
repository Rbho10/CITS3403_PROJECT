from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField, SelectField
from wtforms.validators import InputRequired, Email, EqualTo, DataRequired, NumberRange, Optional, Length

class SignUpForm(FlaskForm):
    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name')
    email = StringField('Email', validators=[InputRequired(), Email()])
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    confirm = PasswordField('Confirm Password', validators=[
        InputRequired(), EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	submit = SubmitField('Login')
     
class LogSessionForm(FlaskForm):
    description = TextAreaField(
        'Description', 
        validators=[DataRequired(), Length(max=255)]
    )
    study_duration = IntegerField(
        'Study Duration (minutes)', 
        validators=[DataRequired(), NumberRange(min=0)]
    )
    break_time = IntegerField(
        'Break Time (minutes)', 
        default=0,
        validators=[Optional(), NumberRange(min=0)]
    )
    mood_level = IntegerField(
        'Mood Level (1-10)', 
        validators=[DataRequired(), NumberRange(min=1, max=10)]
    )
    study_environment = SelectField(
        'Study Environment', 
        choices=[
            ('home', 'Home'),
            ('library', 'Library'),
            ('cafe', 'Cafe'),
            ('other', 'Other')
        ],
        validators=[DataRequired()]
    )
    mental_load = IntegerField(
        'Mental Load (1-10)', 
        validators=[DataRequired(), NumberRange(min=1, max=10)]
    )
    distractions = StringField(
        'Distractions (if any)', 
        validators=[Optional(), Length(max=255)]
    )
    goal_progress = SelectField(
        'Goal Progress',
        choices=[
            ('0%', '0%'),
            ('25%', '25%'),
            ('50%', '50%'),
            ('75%', '75%'),
            ('100%', '100%')
        ],
        validators=[DataRequired()]
    )
    focus_level = IntegerField(
        'Focus Level (1-10)', 
        validators=[DataRequired(), NumberRange(min=1, max=10)]
    )
    effectiveness = IntegerField(
        'Effectiveness (1-10)', 
        validators=[DataRequired(), NumberRange(min=1, max=10)]
    )
    submit = SubmitField('Add Session')


# form to update user settings
class SettingsForm(FlaskForm):
    email = StringField('Email',      validators=[Optional(), Email()])
    username = StringField('Username', validators=[Optional()])
    first_name = StringField('First Name', validators=[Optional()])
    last_name  = StringField('Last Name',  validators=[Optional()])

    current_password = PasswordField(
        'Current Password',
        validators=[InputRequired(message="Please enter your current password")]
    )
    new_password = PasswordField(
        'New Password',
        validators=[Optional(), Length(min=8, message="Must be at least 8 characters")]
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[EqualTo('new_password', message='Passwords must match')]
    )

    submit = SubmitField('Update')