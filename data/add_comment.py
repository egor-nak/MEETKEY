from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, BooleanField, IntegerField
from wtforms.validators import DataRequired


class AddJobForm(FlaskForm):
    content = StringField('Your comment', validators=[DataRequired()])
    submit = SubmitField('Submit')