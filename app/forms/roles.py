# crm_flask/app/forms/roles.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class RoleCreateForm(FlaskForm):
    name = StringField('სახელი', validators=[DataRequired(), Length(max=255)])
    description = TextAreaField('აღწერილობა', validators=[Length(max=255)])
    submit = SubmitField('შენახვა')