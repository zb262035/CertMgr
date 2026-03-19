---
phase: 01-foundation
plan: 02
type: execute
wave: 2
depends_on:
  - 01-foundation-01
files_modified:
  - app/blueprints/auth/routes.py
  - app/blueprints/auth/forms.py
  - app/blueprints/auth/templates/login.html
  - app/blueprints/auth/templates/register.html
  - app/services/auth_service.py
autonomous: true
requirements:
  - AUTH-01
  - AUTH-02

must_haves:
  truths:
    - "User can register with email and password"
    - "User can log in and stay logged in across browser sessions"
    - "User can log out from any page"
    - "Auth adapter interface exists for future SSO integration"
  artifacts:
    - path: "app/blueprints/auth/routes.py"
      provides: "Registration, login, logout routes"
      contains: "@auth_bp.route('/register')", "@auth_bp.route('/login')", "@auth_bp.route('/logout')"
    - path: "app/blueprints/auth/forms.py"
      provides: "WTForms validation for auth forms"
      contains: "class RegistrationForm", "class LoginForm"
    - path: "app/services/auth_service.py"
      provides: "Auth adapter interface for pluggable SSO"
      contains: "class AuthAdapter", "class LocalAuthAdapter"
  key_links:
    - from: "app/blueprints/auth/routes.py"
      to: "app/models/user.py"
      via: "User.query.filter_by(email=).first()"
    - from: "app/blueprints/auth/routes.py"
      to: "app/extensions.py"
      via: "login_user(), logout_user()"
    - from: "app/__init__.py"
      to: "app/services/auth_service.py"
      via: "AUTH_BACKEND config selects adapter"
---

<objective>
Implement user registration, login with remember_me functionality, logout, and the auth adapter interface for future SSO integration. Users can register with email/password and maintain sessions across browser sessions.
</objective>

<execution_context>
@/Users/ice/PycharmProjects/CertMgr/.planning/phases/01-foundation/01-RESEARCH.md
@/Users/ice/PycharmProjects/CertMgr/.planning/phases/01-foundation/01-PLAN.md
</execution_context>

<context>
# Key patterns from research

From 01-RESEARCH.md - Auth Blueprint with Flask-WTF Forms:
```python
class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password',
        validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')
```

From 01-RESEARCH.md - Auth Routes:
```python
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('certificates.list'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('certificates.list'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('certificates.list'))
        flash('Invalid email or password.', 'danger')
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
```

From 01-RESEARCH.md - Auth Adapter Interface:
```python
class AuthAdapter(ABC):
    @abstractmethod
    def authenticate(self, username, password):
        pass

    @abstractmethod
    def get_user_by_id(self, user_id):
        pass

class LocalAuthAdapter(AuthAdapter):
    def authenticate(self, username, password):
        user = User.query.filter_by(email=username).first()
        if user and user.check_password(password):
            return user
        return None
```
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create auth forms and routes</name>
  <files>
    - app/blueprints/auth/forms.py
    - app/blueprints/auth/routes.py
  </files>
  <read_first>
    - app/blueprints/auth/routes.py (will be overwritten - was stub)
    - app/blueprints/auth/forms.py (new file)
  </read_first>
  <action>
Read the current stub routes.py and then overwrite with the complete implementation.

**app/blueprints/auth/forms.py** - WTForms for registration and login:
```python
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
```

**app/blueprints/auth/routes.py** - Auth routes (overwrite the stub):
```python
"""Authentication routes: register, login, logout."""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models.user import User
from app.blueprints.auth.forms import RegistrationForm, LoginForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if current_user.is_authenticated:
        return redirect(url_for('certificates.list'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if email already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('该邮箱已被注册 / This email is already registered.', 'danger')
            return render_template('auth/register.html', form=form)
        # Create new user
        user = User(email=form.email.data)
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
        return redirect(url_for('certificates.list'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            # Validate next page is safe (prevent open redirect)
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('certificates.list'))
        flash('邮箱或密码错误 / Invalid email or password.', 'danger')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout."""
    logout_user()
    flash('已退出登录 / You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
```

Note: The redirect to `certificates.list` will fail until Phase 2 creates that blueprint. For now, use `url_for('auth.login')` as the fallback or create a simple index route.
  </action>
  <verify>
    <automated>cd /Users/ice/PycharmProjects/CertMgr && python -c "
from app import create_app
from app.extensions import db
app = create_app('testing')
with app.app_context():
    db.create_all()
    from app.blueprints.auth.routes import auth_bp
    from app.blueprints.auth.forms import RegistrationForm, LoginForm
    print('Auth forms and routes import successfully')
    # Test form instantiation
    reg_form = RegistrationForm()
    login_form = LoginForm()
    print('Forms instantiate:', reg_form is not None, login_form is not None)
"</automated>
  </verify>
  <done>
    User can register with email/password, log in with remember_me, and log out
  </done>
  <acceptance_criteria>
    - File app/blueprints/auth/forms.py exists and contains: `class RegistrationForm`, `class LoginForm`
    - File app/blueprints/auth/routes.py exists and contains: `@auth_bp.route('/register'`, `@auth_bp.route('/login'`, `@auth_bp.route('/logout'`
    - Registration rejects duplicate email
    - Login succeeds with correct credentials
    - Logout invalidates session
  </acceptance_criteria>
</task>

<task type="auto">
  <name>Task 2: Create auth templates</name>
  <files>
    - app/blueprints/auth/templates/login.html
    - app/blueprints/auth/templates/register.html
  </files>
  <read_first>
    - app/templates/base.html
    - app/templates/macros.html
  </read_first>
  <action>
Create the following template files:

**app/blueprints/auth/templates/login.html**:
```html
{% extends "base.html" %}

{% block title %}登录 - CertMgr{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6 col-lg-5">
        <div class="card shadow-sm">
            <div class="card-header bg-primary text-white">
                <h4 class="mb-0">登录 / Login</h4>
            </div>
            <div class="card-body">
                <form method="POST" action="{{ url_for('auth.login') }}">
                    {{ form.hidden_tag() }}

                    <div class="mb-3">
                        {{ form.email.label(class="form-label") }}
                        {{ form.email(class="form-control", placeholder="your@email.com") }}
                        {% if form.email.errors %}
                            {% for error in form.email.errors %}
                                <span class="text-danger">{{ error }}</span>
                            {% endfor %}
                        {% endif %}
                    </div>

                    <div class="mb-3">
                        {{ form.password.label(class="form-label") }}
                        {{ form.password(class="form-control", placeholder="********") }}
                        {% if form.password.errors %}
                            {% for error in form.password.errors %}
                                <span class="text-danger">{{ error }}</span>
                            {% endfor %}
                        {% endif %}
                    </div>

                    <div class="mb-3 form-check">
                        {{ form.remember_me(class="form-check-input") }}
                        {{ form.remember_me.label(class="form-check-label") }}
                    </div>

                    {{ form.submit(class="btn btn-primary w-100") }}
                </form>
            </div>
            <div class="card-footer text-center">
                <span class="text-muted">还没有账户？</span>
                <a href="{{ url_for('auth.register') }}">立即注册</a>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

**app/blueprints/auth/templates/register.html**:
```html
{% extends "base.html" %}

{% block title %}注册 - CertMgr{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6 col-lg-5">
        <div class="card shadow-sm">
            <div class="card-header bg-primary text-white">
                <h4 class="mb-0">注册 / Register</h4>
            </div>
            <div class="card-body">
                <form method="POST" action="{{ url_for('auth.register') }}">
                    {{ form.hidden_tag() }}

                    <div class="mb-3">
                        {{ form.email.label(class="form-label") }}
                        {{ form.email(class="form-control", placeholder="your@email.com") }}
                        {% if form.email.errors %}
                            {% for error in form.email.errors %}
                                <span class="text-danger">{{ error }}</span>
                            {% endfor %}
                        {% endif %}
                    </div>

                    <div class="mb-3">
                        {{ form.password.label(class="form-label") }}
                        {{ form.password(class="form-control", placeholder="至少8个字符") }}
                        {% if form.password.errors %}
                            {% for error in form.password.errors %}
                                <span class="text-danger">{{ error }}</span>
                            {% endfor %}
                        {% endif %}
                    </div>

                    <div class="mb-3">
                        {{ form.confirm_password.label(class="form-label") }}
                        {{ form.confirm_password(class="form-control", placeholder="再次输入密码") }}
                        {% if form.confirm_password.errors %}
                            {% for error in form.confirm_password.errors %}
                                <span class="text-danger">{{ error }}</span>
                            {% endfor %}
                        {% endif %}
                    </div>

                    {{ form.submit(class="btn btn-primary w-100") }}
                </form>
            </div>
            <div class="card-footer text-center">
                <span class="text-muted">已有账户？</span>
                <a href="{{ url_for('auth.login') }}">立即登录</a>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```
  </action>
  <verify>
    <automated>cd /Users/ice/PycharmProjects/CertMgr && python -c "
from app import create_app
app = create_app('testing')
with app.app_context():
    from flask import render_template
    # Check templates exist and are valid Jinja2
    try:
        template_login = app.jinja_env.get_template('auth/login.html')
        template_register = app.jinja_env.get_template('auth/register.html')
        print('Templates load successfully')
    except Exception as e:
        print('Template error:', e)
"</automated>
  </verify>
  <done>
    Login and registration forms render correctly with Bootstrap styling
  </done>
  <acceptance_criteria>
    - File app/blueprints/auth/templates/login.html exists and contains: `{{ form.hidden_tag() }}`, `{{ form.email }}`, `{{ form.password }}`, `{{ form.remember_me }}`
    - File app/blueprints/auth/templates/register.html exists and contains: `{{ form.hidden_tag() }}`, `{{ form.email }}`, `{{ form.password }}`, `{{ form.confirm_password }}`
    - Both templates extend base.html
  </acceptance_criteria>
</task>

<task type="auto">
  <name>Task 3: Create auth adapter interface for SSO</name>
  <files>
    - app/services/__init__.py
    - app/services/auth_service.py
  </files>
  <read_first>
    - app/services/__init__.py (will be created)
    - app/services/auth_service.py (will be created)
  </read_first>
  <action>
Create the following files for the pluggable auth adapter:

**app/services/__init__.py**:
```python
"""Services package for CertMgr."""
from app.services.auth_service import AuthAdapter, LocalAuthAdapter

__all__ = ['AuthAdapter', 'LocalAuthAdapter']
```

**app/services/auth_service.py** - Auth adapter interface:
```python
"""Pluggable authentication adapter interface.

This module defines the AuthAdapter abstract base class that enables
pluggable authentication backends. For Phase 1, only LocalAuthAdapter
(local database) is implemented. Phase 3 will add SSO adapters.
"""
from abc import ABC, abstractmethod
from flask import current_app


class AuthAdapter(ABC):
    """Abstract base class for authentication backends.

    All auth backends (local, OA, WeChat Work, CAS) must implement
    this interface so they can be swapped without changing application code.
    """

    @abstractmethod
    def authenticate(self, username: str, password: str):
        """Authenticate user with username and password.

        Args:
            username: User's email or username
            password: User's password

        Returns:
            User object if authentication successful, None otherwise
        """
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int):
        """Get user by ID.

        Args:
            user_id: User's integer ID

        Returns:
            User object if found, None otherwise
        """
        pass

    @abstractmethod
    def get_user_by_email(self, email: str):
        """Get user by email.

        Args:
            email: User's email address

        Returns:
            User object if found, None otherwise
        """
        pass


class LocalAuthAdapter(AuthAdapter):
    """Local database authentication adapter.

    This adapter authenticates users against email/password stored
    in the local database using werkzeug.security password hashing.
    """

    def authenticate(self, username: str, password: str):
        """Authenticate against local database."""
        from app.models.user import User
        user = User.query.filter_by(email=username).first()
        if user and user.check_password(password):
            return user
        return None

    def get_user_by_id(self, user_id: int):
        """Get user by ID from local database."""
        from app.models.user import User
        return User.query.get(int(user_id))

    def get_user_by_email(self, email: str):
        """Get user by email from local database."""
        from app.models.user import User
        return User.query.filter_by(email=email).first()


def get_auth_adapter():
    """Factory function to get the configured auth adapter.

    Returns the auth adapter based on AUTH_BACKEND config:
    - 'local' or unset: LocalAuthAdapter
    - 'sso': SSOAuthAdapter (Phase 3)
    """
    backend = current_app.config.get('AUTH_BACKEND', 'local')
    if backend == 'sso':
        from app.services.auth_backends import SSOAuthAdapter
        return SSOAuthAdapter()
    return LocalAuthAdapter()
```
  </action>
  <verify>
    <automated>cd /Users/ice/PycharmProjects/CertMgr && python -c "
from app import create_app
app = create_app('testing')
with app.app_context():
    from app.services.auth_service import AuthAdapter, LocalAuthAdapter, get_auth_adapter
    from app.extensions import db
    db.create_all()
    # Test LocalAuthAdapter
    adapter = get_auth_adapter()
    print('Adapter type:', type(adapter).__name__)
    # Create test user
    from app.models.user import User
    user = User(email='test@test.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    # Test authentication
    result = adapter.authenticate('test@test.com', 'password123')
    print('Auth success:', result is not None and result.email == 'test@test.com')
    # Test wrong password
    result2 = adapter.authenticate('test@test.com', 'wrong')
    print('Auth failure:', result2 is None)
"</automated>
  </verify>
  <done>
    Auth adapter interface exists for future SSO integration, LocalAuthAdapter works for Phase 1
  </done>
  <acceptance_criteria>
    - File app/services/auth_service.py exists and contains: `class AuthAdapter(ABC):`, `class LocalAuthAdapter(AuthAdapter):`
    - LocalAuthAdapter.authenticate() verifies correct password
    - LocalAuthAdapter.authenticate() returns None for wrong password
    - get_auth_adapter() returns LocalAuthAdapter by default
  </acceptance_criteria>
</task>

</tasks>

<verification>
- Registration creates new user in database
- Login with correct credentials sets session
- Login with wrong credentials shows error
- Logout clears session
- Remember me checkbox persists session across browser close
</verification>

<success_criteria>
Phase 1 Plan 2 complete when:
- User can register with email and password
- User can log in and stay logged in (remember_me works)
- User can log out
- Auth adapter interface exists for SSO (Phase 3)
</success_criteria>

<output>
After completion, create `.planning/phases/01-foundation/02-SUMMARY.md`
</output>
