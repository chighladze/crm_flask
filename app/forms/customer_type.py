# crm_flask/app/forms/customer_type.py
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

class CustomerTypeForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired(), Length(max=200)])
    shortName = StringField('Короткое название', validators=[DataRequired(), Length(max=50)])
    category_id = IntegerField('ID категории', default=0)
    submit = SubmitField('Сохранить')
