# crm_flask/app/forms.py
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired
from ..models.customers import Customers  # Предположим, что это модель типов клиентов
from ..models.customer_type import CustomersType


class CustomerForm(FlaskForm):
    type_id = SelectField('კლიენტის ტიპი', coerce=int, validators=[DataRequired()])
    identification_number = StringField('პირადი ნომერი')
    name = StringField('სახელი და გვარი')
    email = StringField('ელ. ფოსტა', validators=[DataRequired()])
    mobile = StringField('მობილური ნომერი', validators=[DataRequired()])
    mobile_second = StringField('დამატებითი საკონტაქტო')
    submit = SubmitField('რეგისტრაცია')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Получаем все типы клиентов из таблицы и добавляем их в список выбора
        self.type_id.choices = [(t.id, t.name) for t in CustomersType.query.all()]
