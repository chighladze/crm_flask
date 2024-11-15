# crm_flask/app/forms/department_positions.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, Length, Optional
from ..models.departments import Departments
from ..models.department_positions import DepartmentPositions

class DepartmentPositionCreateForm(FlaskForm):
    name = StringField(label='პოზიციის სახელი:', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField(label='პოზიციის აღწერილობა:', validators=[Optional(), Length(max=255)])
    department_id = SelectField(label='დეპარტამენტი:', coerce=int)
    submit = SubmitField('შენახვა')

    def __init__(self, department_id, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if department_id is not None:
            department = Departments.query.get(department_id)
            if department:
                self.department_id.choices = [(department.id, department.name)]
                self.department_id.default = department.id

    def validate_name(self, field):
        position = DepartmentPositions.query.filter_by(name=field.data).first()
        if position:
            raise ValidationError(f'პოზიცია ({self.name.data}) უკვე არსებობს')
