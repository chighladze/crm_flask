# crm_flask/app/forms/tasks.py
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, DateField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Optional

class TaskForm(FlaskForm):
    task_category_id = SelectField('Task Category', coerce=int)
    task_type_id = SelectField('Task Type', coerce=int)
    description = TextAreaField('Description', validators=[Optional()])
    status_id = SelectField('Status', coerce=int)
    task_priority_id = SelectField('Priority', coerce=int)
    assigned_to = SelectField('Assigned To', coerce=int)
    created_by = SelectField('Created By', coerce=int)
    completed_by = SelectField('Completed By', coerce=int)
    created_division_id = SelectField('Created Division', coerce=int)
    completed_division_id = SelectField('Completed Division', coerce=int)
    due_date = DateField('Due Date', validators=[Optional()])
    start_date = DateField('Start Date', validators=[Optional()])
    end_date = DateField('End Date', validators=[Optional()])
    estimated_time = IntegerField('Estimated Time', validators=[Optional()])
    actual_time = IntegerField('Actual Time', validators=[Optional()])
    parent_task_id = SelectField('Parent Task', coerce=int)
    progress = IntegerField('Progress', validators=[Optional()])
    comments_count = IntegerField('Comments Count', validators=[Optional()])
    is_recurring = BooleanField('Is Recurring', validators=[Optional()])