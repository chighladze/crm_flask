# crm_flask/app/forms/customers.py
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from ..models.customers_type import CustomersType


class CustomerForm(FlaskForm):
    type_id = SelectField('კლიენტის ტიპი', coerce=int, validators=[DataRequired()])
    identification_number = StringField('იდ. ნომერი', validators=[DataRequired(), Length(max=50)])
    name = StringField('სახელი და გვარი', validators=[DataRequired(), Length(max=255)])
    director = StringField('Director', validators=[Optional()])
    email = StringField('ელ. ფოსტა', validators=[Length(max=100)])
    mobile = StringField('მობილური ნომერი', validators=[DataRequired(), Length(max=20)])
    mobile_second = StringField('დამატებითი საკონტაქტო', validators=[Optional()])
    resident = SelectField('რეზიდენტი', choices=[(1, 'კი'), (0, 'არა')], coerce=int, default=1)
    legal_address = StringField('იურიდიული მისამართი', validators=[DataRequired(), Length(max=255)])
    actual_address = StringField('ფაქტობრივი მისამართი', validators=[DataRequired(), Length(max=255)])
    contact_person_name = StringField('საკონტაქტო პირი', validators=[Length(max=255)])
    contact_person_mobile = StringField('საკონტაქტო პირის მობილული', validators=[Length(max=20)])
    submit = SubmitField('რეგისტრაცია')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type_id.choices = [(t.id, t.name) for t in CustomersType.query.all()]
