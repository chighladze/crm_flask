# crm_flask/app/forms/tasks.py
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, DateField, IntegerField
from wtforms.validators import DataRequired, Optional

class TaskCreateForm(FlaskForm):
    task_category_id = SelectField('Категория задачи', coerce=int, validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
    status_id = SelectField('Статус', coerce=int, validators=[DataRequired()])
    task_priority_id = SelectField('Приоритет', coerce=int, validators=[DataRequired()])
    due_date = DateField('Срок выполнения', validators=[Optional()])