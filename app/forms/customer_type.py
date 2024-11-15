# crm_flask/app/forms/customer_type.py
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length

class CustomerTypeForm(FlaskForm):
    name = StringField('სახელი', validators=[DataRequired(), Length(max=200)])
    shortName = StringField('მოკლეს სახელი', validators=[DataRequired(), Length(max=50)])
    category_id = IntegerField('კატეგორიის ID', default=0)
    submit = SubmitField('შენახვა')
