# crm_flask/app/forms/address.py
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, IntegerField, DecimalField
from wtforms.validators import DataRequired, Length, Optional
from ..models import District, BuildingType, Settlement


def coerce_to_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


class AddressForm(FlaskForm):
    district_id = SelectField('District', validators=[DataRequired()], coerce=coerce_to_int)
    settlement_id = SelectField('Settlement', validators=[DataRequired()],
                                coerce=coerce_to_int)
    building_type_id = SelectField('Building Type', validators=[DataRequired()], coerce=coerce_to_int)
    street = StringField('Street', validators=[DataRequired(), Length(max=100)])
    building_number = IntegerField('Building Number', validators=[DataRequired()])
    entrance_number = IntegerField('Entrance Number', validators=[Optional()])
    floor_number = IntegerField('Floor Number', validators=[Optional()])
    apartment_number = IntegerField('Apartment Number', validators=[Optional()])
    house_number = IntegerField('House Number', validators=[Optional()])
    latitude = DecimalField('Latitude', validators=[DataRequired()])
    longitude = DecimalField('Longitude', validators=[DataRequired()])
    registry_code = StringField('Registry Code', validators=[Optional()])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.district_id.choices = [('', 'აირჩიეთ რაიონი')] + [(d.id, d.name) for d in District.query.all()]
        self.settlement_id.choices = [('', 'აირჩიეთ დასახლება')] + [(d.id, d.name) for d in Settlement.query.all()]
        self.building_type_id.choices = [('', 'აირჩიეთ შენობის ტიპი')] + [(bt.id, bt.name) for bt in
                                                                          BuildingType.query.all()]
