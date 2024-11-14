# crm_flask/app/forms/division_positions.py
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired


class DivisionPositionCreateForm(FlaskForm):
    name = StringField('პოზიციის დასახელბა', validators=[DataRequired()])
    division_id = IntegerField('განყოფილების ID', validators=[DataRequired()])
    submit = SubmitField('შენახვა')
