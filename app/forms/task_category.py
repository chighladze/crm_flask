# crm_flask/app/forms/task_category.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length
from ..models.division_positions import DivisionPositions


class TaskCategoryForm(FlaskForm):
    name = StringField('კატეგორიის სახელი', validators=[DataRequired(), Length(max=50)])
    position_id = SelectField('გნაყოფილების პოზიცია', coerce=int)
    submit = SubmitField('შენახვა')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.position_id.choices = [(pos.id, pos.name) for pos in DivisionPositions.query.all()]
