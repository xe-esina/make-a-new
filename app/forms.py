from flask_wtf import FlaskForm
from wtforms import FileField, StringField, TextAreaField, BooleanField, PasswordField, SubmitField, IntegerField, DecimalField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, NumberRange, Length
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Имя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня!', default=False)
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    username = StringField('Имя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField(
        'Повторить пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Это имя уже занято.')


class EditProfileForm(FlaskForm):
    username = StringField('Имя', validators=[DataRequired()])
    about_me = TextAreaField('О себе', validators=[Length(min=0, max=140)])
    password = PasswordField('Пароль')
    password2 = PasswordField('Повторить пароль',
                              validators=[EqualTo('password')])
    submit = SubmitField('Изменить')


class CreatePostForm(FlaskForm):
    headline = StringField('Заголовок', validators=[DataRequired(), Length(min=1, max=100)])
    text = TextAreaField('Текст', validators=[DataRequired()])

    submit = SubmitField('Добавить новость')

