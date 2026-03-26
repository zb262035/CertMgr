"""Authentication forms with WTForms validation."""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from app.models.department import Department


def get_department_choices():
    """Get active departments as choices for select field."""
    departments = Department.query.filter_by(status='active').order_by(Department.name).all()
    return [(str(d.id), d.name) for d in departments]


class RegistrationForm(FlaskForm):
    """User registration form."""
    email = StringField('邮箱 / Email', validators=[
        DataRequired(message='邮箱不能为空'),
        Email(message='请输入有效的邮箱地址')
    ])
    department = SelectField('部门 / Department', validators=[
        DataRequired(message='请选择部门')
    ], coerce=int)
    password = PasswordField('密码 / Password', validators=[
        DataRequired(message='密码不能为空'),
        Length(min=8, message='密码至少需要8个字符')
    ])
    confirm_password = PasswordField('确认密码 / Confirm Password', validators=[
        DataRequired(message='请确认密码'),
        EqualTo('password', message='两次输入的密码不一致')
    ])
    submit = SubmitField('注册 / Register')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.department.choices = [(0, '请选择部门 / Select Department')] + get_department_choices()


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


class PasswordChangeForm(FlaskForm):
    """Password change form for user profile."""
    current_password = PasswordField('当前密码 / Current Password', validators=[
        DataRequired(message='请输入当前密码')
    ])
    new_password = PasswordField('新密码 / New Password', validators=[
        DataRequired(message='请输入新密码'),
        Length(min=8, message='密码至少需要8个字符')
    ])
    confirm_password = PasswordField('确认新密码 / Confirm New Password', validators=[
        DataRequired(message='请确认新密码'),
        EqualTo('new_password', message='两次输入的密码不一致')
    ])
    submit = SubmitField('修改密码 / Change Password')