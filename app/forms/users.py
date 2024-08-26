from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, SubmitField, FileField, ValidationError, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, Email
from ..models.users import Users


class UserCreateForm(FlaskForm):
    name = StringField('სახელი და გვარი', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('მეილი', validators=[DataRequired(), Email(message='შეიყვანეთ მეილი სწორი ფორმატით'),
                                             Length(min=2, max=50)])
    password = PasswordField('პაროლი', validators=[DataRequired()])
    confirm_password = PasswordField('გაიმეორეთ პაროლი', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('შენახვა')

    def validate_email(self, field):
        user = Users.query.filter_by(email=field.data).first()
        if user:
            raise ValidationError('მომხმარებელი ასეთი მეილთ უკვე არსებობს.')


class LoginForm(FlaskForm):
    email = StringField('მეილი', validators=[DataRequired(), Email(), Length(min=2, max=50)])
    password = PasswordField('პაროლი', validators=[DataRequired()])
    remember = BooleanField('დამახსოვრება')
    submit = SubmitField('შესვლა')
