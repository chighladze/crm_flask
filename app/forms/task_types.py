# crm_flask/app/forms/task_types.py

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired
from ..models import Divisions, Departments

class TaskTypeForm(FlaskForm):
    name = StringField('Task Type Name', validators=[DataRequired(message="სახელი აუცილებელია")])
    division_id = SelectField('Division', coerce=int, validators=[DataRequired(message="განყოფილების არჩევა აუცილებელია")])
    department_id = SelectField('Department', coerce=int, validators=[DataRequired(message="დეპარტამენტის არჩევა აუცილებელია")])

    def __init__(self, *args, **kwargs):
        super(TaskTypeForm, self).__init__(*args, **kwargs)
        # Populate department choices dynamically
        self.department_id.choices = [(d.id, d.name) for d in Departments.query.all()]
        self.division_id.choices = []  # Division will load dynamically

