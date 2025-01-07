# crm_flask/app/forms/order_status.py

from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms.validators import DataRequired
from app.models import OrderStatus


class OrderStatusForm(FlaskForm):
    new_status = SelectField('ახალი სტატუსი', coerce=int, validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(OrderStatusForm, self).__init__(*args, **kwargs)
        # Заполнение списка статусов из базы данных
        self.new_status.choices = [(status.id, status.name) for status in OrderStatus.query.all()]
