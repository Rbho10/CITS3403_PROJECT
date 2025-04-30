from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, SelectField
from wtforms.validators import InputRequired

class CreateStudySubjectForm(FlaskForm):
    subject_name = StringField("Subject Name", validators=[InputRequired()])
    #graph_type = SelectField("Graph Type", choices=[("line_graph", "Line Graph"),
    #                                                ("pie_graph", "Pie Graph"),
    #                                                ("bar_graph", "Bar Graph")])
    #graph_scale = SelectField("Graph Scale", choices=[(1, "One Month"),
    #                                                  (3, "Three Months"),
    #                                                  (6, "Six Months"),
    #                                                  (12, "One Year"),
    #                                                  (36, "Three Years")]) #integers are indicative of month length
    #privacy = SelectField("Privacy Setting", choices=[("public", "Public"), 
    #                                                  ("private", "Private"),
    #                                                  ("hidden", "Hidden")])
    #opinion_toggle = BooleanField("Allow Opinions", default="checked")
    submit = SubmitField('Create Subject')
