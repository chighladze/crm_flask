# crm_flask/app/forms/tariff_plan.py
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, IntegerField, BooleanField, SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, Length, Optional


class TariffPlanForm(FlaskForm):
    name = StringField('სახელი', validators=[DataRequired(), Length(max=100)])
    customer_type_id = SelectField('კლიენტის ტიპი', coerce=int, validators=[DataRequired()])
    price = DecimalField('საფასური', validators=[DataRequired(), NumberRange(min=0)], places=2)
    currency_id = SelectField('ვალუტა', coerce=int, validators=[DataRequired()])
    technology_id = SelectField('ჩართვის ტექნოლოგია', coerce=int, validators=[DataRequired()])

    internet_download_speed = IntegerField('ჩამოტვირთვის სიჩქარე', validators=[NumberRange(min=0)])
    internet_upload_speed = IntegerField('ატვირთვის სიჩქარე', validators=[NumberRange(min=0)])
    internet_min_download_speed = IntegerField('მინ. ჩამოტვირთვის სიჩქარე', validators=[NumberRange(min=0)])
    internet_min_upload_speed = IntegerField('მინ. ატვირთვის სიჩქარე', validators=[NumberRange(min=0)])
    internet_data_limit = IntegerField('მონაცემების ლიმიტი (გბ)', validators=[NumberRange(min=0)])
    internet_unlimited = BooleanField('ულიმიტო ინტერნეტი')

    description = TextAreaField('ტარიფის აღწერილობა', validators=[Optional(), Length(max=2000)])

    created_at = StringField('შექმნის თარიღი', render_kw={'readonly': True})
    updated_at = StringField('განახლების თარიღი', render_kw={'readonly': True})

    submit = SubmitField('შენახვა')
