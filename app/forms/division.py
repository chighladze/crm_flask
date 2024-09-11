from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, SubmitField, FileField, ValidationError, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, Email, Optional
from ..models.division import Divisions
from ..models.departments import Departments


class DivisionCreateForm(FlaskForm):
    name = StringField(label='განყოფილების სახელი:', validators=[DataRequired(), Length(min=2, max=100)])
    description = StringField(label='განყოფილების აღწერილობა:', validators=[Optional(), Length(max=255)])
    department_id = SelectField(label='დეპარტამენტი:')
    submit = SubmitField('შენახვა')

    def __init__(self, department_id, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # # Сначала обработаем данные
        # self.process()
        # print(self.name)

        # Если передан department_id, устанавливаем только этот департамент в списке выбора
        if department_id is not None:
            department = Departments.query.get(department_id)
            if department:
                self.department_id.choices = [(department.id, department.name)]
                self.department_id.default = department.id

    def validate_name(self, field):
        division = Divisions.query.filter_by(name=field.data).first()
        if division:
            raise ValidationError(f'განყოფილება ({self.name.data}) უკვე არსებობს')
