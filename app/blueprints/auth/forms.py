"""Authentication forms with WTForms validation."""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class RegistrationForm(FlaskForm):
    """User registration form."""
    email = StringField('邮箱 / Email', validators=[
        DataRequired(message='邮箱不能为空'),
        Email(message='请输入有效的邮箱地址')
    ])
    password = PasswordField('密码 / Password', validators=[
        DataRequired(message='密码不能为空'),
        Length(min=8, message='密码至少需要8个字符')
    ])
    confirm_password = PasswordField('确认密码 / Confirm Password', validators=[
        DataRequired(message='请确认密码'),
        EqualTo('password', message='两次输入的密码不一致')
    ])
    submit = SubmitField('注册 / Register')


class LoginForm(FlaskForm):
    """User login form."""
    email = StringField('邮箱 / Email', validators=[
        DataRequired(message='邮箱不能为空'),
        Email(message='请输入有效的邮箱地址')
    ])
    password = PasswordField('密码 / Password', validators=[
        DataRequired(message='密码不能为空')
    ])
    remember_me = BooleanField('记住我 / Remember Me')
    submit = SubmitField('登录 / Login')