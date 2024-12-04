from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class TaskTypeForm(FlaskForm):
    name = StringField('Название типа', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Сохранить')
