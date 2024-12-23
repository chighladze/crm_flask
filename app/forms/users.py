# crm_flask/app/forms/users.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, Email, Optional
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
            raise ValidationError('მომხმარებელი ასეთი მეილით უკვე არსებობს.')

    def validate_name(self, field):
        user = Users.query.filter_by(name=field.data).first()
        if user:
            raise ValidationError('მომხმარებელი ასეთი სახელით უკვე არსებობს.')

    def validate_password(form, field):
        password = field.data
        if len(password) < 8:
            raise ValidationError('პაროლი არ უნდა იყოს 8 სიმბოლოზე ნაკლები..')
        if not any(char.isdigit() for char in password):
            raise ValidationError('პაროლი უნდა მოიცავდეს მინიმუმ ერთ ციფრს.')
        if not any(char.isupper() for char in password):
            raise ValidationError('პაროლი უნდა მოიცავდეს მინიმუმ ერთ დიდ ასოს.')


class LoginForm(FlaskForm):
    email = StringField('მეილი', validators=[DataRequired(), Email(), Length(min=2, max=50)])
    password = PasswordField('პაროლი', validators=[DataRequired()])
    remember = BooleanField('დამახსოვრება')
    submit = SubmitField('შესვლა')


class UserEditForm(FlaskForm):
    name = StringField('სახელი და გვარი', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('მეილი', validators=[DataRequired(), Email(message='შეიყვანეთ მეილი სწორი ფორმატით'),
                                             Length(min=2, max=50)])
    status = SelectField('სტატუსი', choices=[('1', 'აქტიური'), ('0', 'პასიური')], validators=[DataRequired()])
    password = PasswordField('ახალი პაროლი', validators=[Optional()])
    confirm_password = PasswordField('გაიმეორეთ ახალი პაროლი',
                                     validators=[EqualTo('password', message='პაროლები უნდა ემთხვეოდეს'), Optional()])
    submit = SubmitField('შენახვა')

    def __init__(self, original_email, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        self.original_email = original_email

    def validate_email(self, field):
        # Check if a user with such email exists
        if field.data != self.original_email:
            user = Users.query.filter_by(email=field.data).first()
            if user:
                raise ValidationError('მომხმარებელი ასეთი მეილით უკვე არსებობს.')
