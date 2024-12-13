# crm_flask/app/forms/address.py
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, IntegerField, DecimalField
from wtforms.validators import DataRequired, Length, Optional, ValidationError
from ..models import District, BuildingType, Settlement


def coerce_to_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def validate_latitude(form, field):
    if field.data is not None and not (-90 <= field.data <= 90):
        raise ValidationError("განედი უნდა იყოს -90 და 90 შორის.")


def validate_longitude(form, field):
    if field.data is not None and not (-180 <= field.data <= 180):
        raise ValidationError("გრძედი უნდა იყოს -180 და 180 შორის.")


class AddressForm(FlaskForm):
    district_id = SelectField('რაიონი', validators=[DataRequired()], coerce=coerce_to_int)
    settlement_id = SelectField('დასახლება', validators=[DataRequired()], coerce=coerce_to_int, choices=[])
    building_type_id = SelectField('შენობის ტიპი', validators=[DataRequired()], coerce=coerce_to_int)
    street = StringField('ქუჩა', validators=[DataRequired(), Length(max=100)])
    building_number = IntegerField('შენობის ნომერი', validators=[DataRequired()])
    entrance_number = IntegerField('კარიბჭის ნომერი', validators=[Optional()])
    floor_number = IntegerField('სართულების ნომერი', validators=[Optional()])
    apartment_number = IntegerField('ბინა ნომერი', validators=[Optional()])
    house_number = IntegerField('სახლის ნომერი', validators=[Optional()])
    latitude = DecimalField('სიგრძე', validators=[Optional(), validate_latitude])
    longitude = DecimalField('გრძელი', validators=[Optional(), validate_longitude])
    registry_code = StringField('რეგისტრაციის კოდი', validators=[Optional()])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.district_id.choices = [('', 'აირჩიეთ რაიონი')] + [(d.id, d.name) for d in District.query.all()]
        # self.settlement_id.choices = [('', 'აირჩიეთ დასახლება')]  # Set empty options initially
        self.building_type_id.choices = [('', 'აირჩიეთ შენობის ტიპი')] + [(bt.id, bt.name) for bt in
                                                                          BuildingType.query.all()]

    def validate_settlement_id(self, field):
        if not field.data:
            raise ValidationError("თქვენ უნდა აირჩიეთ დასახლება.")
        settlement = Settlement.query.filter_by(id=field.data).first()
        if not settlement:
            raise ValidationError("შემოთავაზებული დასახლება არ არსებობს.")
