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
    customer_id = IntegerField('კლიენტის ID', validators=[Optional()], )
    address = FormField(AddressForm)
    mobile = TelField('მობილური', validators=[DataRequired(), Length(max=20)])
    alt_mobile = TelField('ალტერნატიული მობილური', validators=[Optional()])
    tariff_plan_id = SelectField('სატარიფო გეგმა', validators=[DataRequired()], coerce=coerce_to_int)
    comment = TextAreaField('კომენტარი')
    task_id = IntegerField('დავალების ID', validators=[Optional()])
    submit = SubmitField('შეკვეთის შენახვა')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tariff_plan_id.choices = [('', 'აირჩიეთ სატარიფო გეგმა')] + [(tp.id, tp.name) for tp in TariffPlan.query.all()]
