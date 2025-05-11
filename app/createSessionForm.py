from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, IntegerField
from wtforms.validators import InputRequired

class CreateSessionForm(FlaskForm):
    date = DateField("Date and Time (YYYY-MM-DD HH:MM:SS)", validators=[InputRequired()])
    study_duration = IntegerField("Hours Studied", validators=[InputRequired()])
    study_break = IntegerField("Break Time Hours")
    environment = StringField("Study Environment")
    energy_level_before = StringField("Energy Level Before Study")
    energy_level_after = StringField("Energy Level After Study")
    difficulty = StringField("Difficulty")
    progress = StringField("Progress")
    submit = SubmitField('Create Session')