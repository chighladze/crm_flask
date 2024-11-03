from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, IntegerField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional


class TariffPlanForm(FlaskForm):
    name = StringField('Название тарифа', validators=[DataRequired()])
    client_type_id = SelectField('Тип клиента', coerce=int, validators=[DataRequired()])
    price = DecimalField('Цена', validators=[DataRequired()])
    currency_id = SelectField('Валюта', coerce=int, validators=[DataRequired()])
    technology_id = SelectField('Технология', coerce=int, validators=[DataRequired()])

    internet_download_speed = IntegerField('Скорость скачивания (Мбит/с)', validators=[Optional()])
    internet_upload_speed = IntegerField('Скорость отправки (Мбит/с)', validators=[Optional()])
    internet_data_limit = IntegerField('Лимит данных (ГБ)', validators=[Optional()])
    internet_unlimited = BooleanField('Безлимитный интернет', default=False)

    tv_service = BooleanField('ТВ-сервис', default=False)
    tv_channels = IntegerField('Количество каналов', validators=[Optional()])
    tv_hd_channels = IntegerField('Количество HD-каналов', validators=[Optional()])
    tv_package_id = SelectField('Пакет ТВ', coerce=int, validators=[Optional()])

    phone_service = BooleanField('Телефонный сервис', default=False)
    phone_minutes = IntegerField('Количество минут', validators=[Optional()])

    description = TextAreaField('Описание', validators=[Optional()])

