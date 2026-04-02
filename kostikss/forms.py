from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, IntegerField, SelectField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange, ValidationError
from models import User


class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired()])
    role = SelectField('Роль', choices=[('buyer', 'Покупатель'), ('seller', 'Продавец')])
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Это имя пользователя уже занято')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Этот email уже зарегистрирован')

    def validate_confirm_password(self, confirm_password):
        if confirm_password.data != self.password.data:
            raise ValidationError('Пароли не совпадают')


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя или Email', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class GigForm(FlaskForm):
    title = StringField('Название услуги', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
    basic_price = FloatField('Цена (₽)', validators=[DataRequired(), NumberRange(min=0)])
    basic_delivery = IntegerField('Срок выполнения (дней)', validators=[DataRequired(), NumberRange(min=1)])
    basic_features = TextAreaField('Что входит в услугу', validators=[DataRequired()])
    submit = SubmitField('Создать услугу')