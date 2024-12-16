# crm_flask/app/forms/task_category.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length
from ..models import Divisions, Departments
from ..models.division_positions import DivisionPositions


class TaskCategoryForm(FlaskForm):
    name = StringField('კატეგორიის სახელი', validators=[DataRequired(), Length(max=50)])
    department_id = SelectField('დეპარტამენტი', coerce=int, validators=[DataRequired()])
    division_id = SelectField('განყოფილება', coerce=int, validators=[DataRequired()])
    position_id = SelectField('პოზიცია', coerce=int, validators=[DataRequired()])
    submit = SubmitField('შენახვა')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.department_id.choices = [(department.id, department.name) for department in Departments.query.all()]
        self.division_id.choices = [(division.id, division.name) for division in Divisions.query.all()]
        self.position_id.choices = [(position.id, position.name) for position in DivisionPositions.query.all()]
