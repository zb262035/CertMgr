"""Authentication routes: register, login, logout."""
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models.user import User
from app.blueprints.auth.forms import RegistrationForm, LoginForm, PasswordChangeForm

from app.blueprints.auth import auth_bp


@auth_bp.route('/')
@login_required
def home():
    """Home page after login."""
    return render_template('home.html')


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page for changing password."""
    form = PasswordChangeForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('当前密码错误 / Current password is incorrect.', 'danger')
            return render_template('auth/profile.html', form=form)
        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash('密码修改成功 / Password changed successfully.', 'success')
        return redirect(url_for('auth.profile'))
    return render_template('auth/profile.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    form = RegistrationForm()

    # Validate department on submit
    if form.validate_on_submit():
        if form.department.data == 0:
            flash('请选择部门 / Please select a department.', 'danger')
            return render_template('auth/register.html', form=form)

        # Check if email already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('该邮箱已被注册 / This email is already registered.', 'danger')
            return render_template('auth/register.html', form=form)

        # Create new user with department
        user = User(
            email=form.email.data,
            department_id=form.department.data,
            role=User.ROLE_USER,
            must_change_password=False  # User chose their own password
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('注册成功，请登录 / Registration successful. Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login with remember_me support."""
    if current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            if user.is_disabled:
                flash('账号已被禁用，请联系管理员 / Account is disabled. Please contact admin.', 'danger')
                return render_template('auth/login.html', form=form)
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            # Validate next page is safe (prevent open redirect)
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('auth.home'))
        flash('邮箱或密码错误 / Invalid email or password.', 'danger')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout."""
    logout_user()
    flash('已退出登录 / You have been logged out.', 'info')
    return redirect(url_for('auth.login'))