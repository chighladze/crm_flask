# crm_flask/app/forms/tariff_plan.py

from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, IntegerField, BooleanField, SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, Length, Optional


class TariffPlanForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired(), Length(max=100)])
    customer_type_id = SelectField('Тип клиента', coerce=int, validators=[DataRequired()])
    price = DecimalField('Цена', validators=[DataRequired(), NumberRange(min=0)], places=2)
    currency_id = SelectField('Валюта', coerce=int, validators=[DataRequired()])
    technology_id = SelectField('Технология подключения', coerce=int, validators=[DataRequired()])

    internet_download_speed = IntegerField('Скорость скачивания', validators=[NumberRange(min=0)])
    internet_upload_speed = IntegerField('Скорость отправки', validators=[NumberRange(min=0)])
    internet_min_download_speed = IntegerField('Мин. скорость скачивания', validators=[NumberRange(min=0)])
    internet_min_upload_speed = IntegerField('Мин. скорость отправки', validators=[NumberRange(min=0)])
    internet_data_limit = IntegerField('Лимит данных (в ГБ)', validators=[NumberRange(min=0)])
    internet_unlimited = BooleanField('Безлимитный интернет')

    # Новое поле для описания тарифа
    description = TextAreaField('Описание тарифа', validators=[Optional(), Length(max=2000)])

    # Поля только для отображения дат, не обязательны к редактированию
    created_at = StringField('Дата создания', render_kw={'readonly': True})
    updated_at = StringField('Дата обновления', render_kw={'readonly': True})

    submit = SubmitField('Сохранить тариф')
