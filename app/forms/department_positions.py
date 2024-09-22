from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, Length, Optional
from ..models.departments import Departments
from ..models.department_positions import DepartmentPositions

class DepartmentPositionCreateForm(FlaskForm):
    name = StringField(label='პოზიციის სახელი:', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField(label='პოზიციის აღწერილობა:', validators=[Optional(), Length(max=255)])
    department_id = SelectField(label='დეპარტამენტი:', coerce=int)  # Используем coerce для преобразования значений в int
    submit = SubmitField('შენახვა')

    def __init__(self, department_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.department_id.choices = [(dept.id, dept.name) for dept in Departments.query.all()]
        if department_id is not None:
            self.department_id.default = department_id

    def validate_name(self, field):
        position = DepartmentPositions.query.filter_by(name=field.data).first()
        if position:
            raise ValidationError(f'პოზიცია ({self.name.data}) უკვე არსებობს')
