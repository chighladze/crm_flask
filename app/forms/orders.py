# crm_flask/app/forms/orders.py
from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, TelField, SubmitField, SelectField, FormField, DecimalField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional
from ..models import TariffPlan, District, BuildingType
from .address import AddressForm


def coerce_to_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None

class OrderForm(FlaskForm):
    customer_id = IntegerField('Customer ID', validators=[DataRequired()], )
    address = FormField(AddressForm)
    mobile = TelField('Mobile', validators=[DataRequired(), Length(max=20)])
    alt_mobile = TelField('Alternative Mobile', validators=[Optional()])
    tariff_plan_id = SelectField('Tariff Plan', validators=[DataRequired()], coerce=coerce_to_int)
    comment = TextAreaField('Comment')
    task_id = IntegerField('Task ID', validators=[Optional()])
    submit = SubmitField('Create Order')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tariff_plan_id.choices = [('', 'აირჩიეთ სატარიფო გეგმა')] + [(tp.id, tp.name) for tp in TariffPlan.query.all()]
