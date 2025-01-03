# crm_flask/app/forms/division.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError, SelectField
from wtforms.validators import DataRequired, Length, Optional
from ..models.division import Divisions
from ..models.departments import Departments


class DivisionCreateForm(FlaskForm):
    name = StringField(label='განყოფილების სახელი:', validators=[DataRequired(), Length(min=2, max=100)])
    description = StringField(label='განყოფილების აღწერილობა:', validators=[Optional(), Length(max=255)])
    department_id = SelectField(label='დეპარტამენტი:')
    submit = SubmitField('შენახვა')

    def __init__(self, department_id, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # If department_id is passed, set only that department in the selection list
        if department_id is not None:
            department = Departments.query.get(department_id)
            if department:
                self.department_id.choices = [(department.id, department.name)]
                self.department_id.default = department.id

    def validate_name(self, field):
        division = Divisions.query.filter_by(name=field.data).first()
        if division:
            raise ValidationError(f'განყოფილება ({self.name.data}) უკვე არსებობს')
