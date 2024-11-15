# crm_flask/app/forms/departments.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length, Optional
from ..models.departments import Departments


class DepartmentCreateForm(FlaskForm):
    name = StringField('დეპარტამენტის სახელი', validators=[DataRequired(), Length(min=2, max=100)])
    description = StringField('აღწერა', validators=[Optional(), Length(max=255)])
    submit = SubmitField('შენახვა')

    def validate_name(self, field):
        department = Departments.query.filter_by(name=field.data).first()
        if department:
            raise ValidationError('დეპარტამენტი ასეთი სახელი უკვე არსებობს.')
