---
phase: 01-foundation
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - app/__init__.py
  - app/extensions.py
  - app/config.py
  - run.py
  - app/templates/base.html
  - app/templates/macros.html
  - app/static/css/app.css
  - requirements.txt
autonomous: true
requirements:
  - AUTH-01
  - AUTH-02
  - CERT-03
  - CERT-11

must_haves:
  truths:
    - "Flask app can start without errors"
    - "Flask extensions (db, login_manager, csrf) are initialized"
    - "Templates extend base layout correctly"
  artifacts:
    - path: "app/extensions.py"
      provides: "Shared Flask extension instances"
      contains: "db = SQLAlchemy(), login_manager = LoginManager(), csrf = CSRFProtect()"
    - path: "app/__init__.py"
      provides: "Application factory with create_app()"
      contains: "def create_app(config=None):"
    - path: "app/config.py"
      provides: "Configuration classes (Dev/Prod)"
      contains: "class Config:, class DevConfig:, class ProdConfig:"
    - path: "run.py"
      provides: "Application entry point"
      contains: "from app import create_app"
    - path: "app/templates/base.html"
      provides: "Base template with Bootstrap 5"
      contains: "{% block content %}, {% endblock %}"
  key_links:
    - from: "app/__init__.py"
      to: "app/extensions.py"
      via: "import db, login_manager, csrf from extensions"
    - from: "run.py"
      to: "app/__init__.py"
      via: "from app import create_app"
---

<objective>
Set up the Flask application factory pattern with shared extensions, configuration classes, and base templates. This is the foundation that all subsequent work depends on.
</objective>

<execution_context>
@/Users/ice/PycharmProjects/CertMgr/.planning/phases/01-foundation/01-RESEARCH.md
@/Users/ice/PycharmProjects/CertMgr/.planning/research/ARCHITECTURE.md
</execution_context>

<context>
# Key patterns from research

From 01-RESEARCH.md - Flask Application Factory Pattern:
```python
# app/__init__.py
def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    return app
```

From 01-RESEARCH.md - Extensions Module:
```python
# app/extensions.py
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
login_manager.login_view = 'auth.login'
```

From 01-RESEARCH.md - Configuration:
```python
# app/config.py
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///certmgr.db'
    UPLOAD_FOLDER = 'instance/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
```
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create directory structure and extensions.py</name>
  <files>
    - app/__init__.py
    - app/extensions.py
    - app/config.py
    - requirements.txt
  </files>
  <read_first>
    - app/__init__.py (will be created - no existing content)
    - app/extensions.py (will be created)
    - app/config.py (will be created)
    - requirements.txt (will be created)
  </read_first>
  <action>
Create the following files with exact content:

**app/extensions.py** - Shared Flask extension instances (prevents circular imports):
```python
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

login_manager.login_view = 'auth.login'
login_manager.session_protection = 'strong'
```

**app/config.py** - Configuration classes:
```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///certmgr.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = BASE_DIR / 'instance' / 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}


class DevConfig(Config):
    DEBUG = True


class ProdConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
```

**app/__init__.py** - Application factory with blueprint registration:
```python
from flask import Flask
from app.extensions import db, login_manager, csrf


def create_app(config_name='dev'):
    app = Flask(__name__, instance_relative_config=True)

    # Load configuration
    if config_name == 'prod':
        app.config.from_object('app.config.ProdConfig')
    elif config_name == 'testing':
        app.config.from_object('app.config.TestingConfig')
    else:
        app.config.from_object('app.config.DevConfig')
    app.config.from_prefixed_env()

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))

    # Register blueprints
    from app.blueprints.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.blueprints.admin import admin_bp
    app.register_blueprint(admin_bp)

    # Import models to register them with SQLAlchemy
    from app.models import user

    # Create instance folder and upload directory
    import os
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Create tables if needed (development only)
    with app.app_context():
        db.create_all()

    return app
```

**requirements.txt** - Core dependencies:
```
Flask==3.1.3
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.1.0
Flask-Login==0.6.3
Flask-WTF==1.2.2
WTForms==3.2.1
SQLAlchemy==2.0.48
psycopg2-binary==2.9.11
Pillow==11.3.0
python-dotenv==1.2.1
waitress==3.0.2
pytest==8.3.5
pytest-flask==1.3.0
```
  </action>
  <verify>
    <automated>cd /Users/ice/PycharmProjects/CertMgr && python -c "from app import create_app; app = create_app('testing'); print('App factory works:', app is not None)"</automated>
  </verify>
  <done>
    App factory creates Flask app instance, extensions are initialized, database tables can be created
  </done>
  <acceptance_criteria>
    - File app/extensions.py exists and contains: `db = SQLAlchemy()`, `login_manager = LoginManager()`, `csrf = CSRFProtect()`
    - File app/config.py exists and contains: `class Config:`, `class DevConfig:`, `class ProdConfig:`, `class TestingConfig:`
    - File app/__init__.py exists and contains: `def create_app(config_name='dev'):`, `db.init_app(app)`, `login_manager.init_app(app)`, `@login_manager.user_loader`
    - File requirements.txt exists and contains: `Flask==3.1.3`, `Flask-Login==0.6.3`, `Flask-SQLAlchemy==3.1.1`
  </acceptance_criteria>
</task>

<task type="auto">
  <name>Task 2: Create run.py entry point and base templates</name>
  <files>
    - run.py
    - app/templates/base.html
    - app/templates/macros.html
    - app/static/css/app.css
    - instance/.gitkeep
  </files>
  <read_first>
    - run.py (will be created)
    - app/templates/base.html (will be created)
  </read_first>
  <action>
Create the following files with exact content:

**run.py** - Application entry point:
```python
#!/usr/bin/env python
"""Application entry point for CertMgr."""
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

**instance/.gitkeep** - Ensures instance directory exists in git:
```
# This file ensures the instance directory is tracked by git
```

**app/templates/base.html** - Base template with Bootstrap 5:
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}CertMgr - 证书管理系统{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/app.css') }}">
    {% block extra_css %}{% endblock %}
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('certificates.list') if current_user.is_authenticated else url_for('auth.login') }}">
                CertMgr - 证书管理系统
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    {% if current_user.is_authenticated %}
                        <li class="nav-item">
                            <span class="navbar-text me-3"> {{ current_user.email }}</span>
                        </li>
                        {% if current_user.is_admin %}
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('admin.list_users') }}">用户管理</a>
                        </li>
                        {% endif %}
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('auth.logout') }}">退出</a>
                        </li>
                    {% else %}
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('auth.login') }}">登录</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('auth.register') }}">注册</a>
                        </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <main class="container my-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        {% block content %}{% endblock %}
    </main>

    <footer class="text-center text-muted py-4">
        <small>CertMgr - 教职工证书管理系统</small>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

**app/templates/macros.html** - Jinja2 macros for forms:
```html
{% macro render_field(field, class='form-control') %}
    <div class="mb-3">
        {{ field.label(class="form-label") }}
        {{ field(class=class, **kwargs) }}
        {% if field.errors %}
            {% for error in field.errors %}
                <span class="text-danger">{{ error }}</span>
            {% endfor %}
        {% endif %}
    </div>
{% endmacro %}

{% macro render_checkbox(field) %}
    <div class="mb-3 form-check">
        {{ field(class="form-check-input") }}
        {{ field.label(class="form-check-label") }}
    </div>
{% endmacro %}
```

**app/static/css/app.css** - Custom CSS:
```css
/* Custom styles for CertMgr */
:root {
    --primary-color: #0d6efd;
}

body {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

main {
    flex: 1;
}

.navbar-brand {
    font-weight: 600;
}

/* Flash messages */
.alert {
    border-radius: 0.375rem;
}

/* Form styles */
.form-label {
    font-weight: 500;
}

.required::after {
    content: " *";
    color: red;
}

/* Card hover effect */
.card {
    transition: box-shadow 0.2s;
}

.card:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
```
  </action>
  <verify>
    <automated>cd /Users/ice/PycharmProjects/CertMgr && python -c "
from app import create_app
app = create_app('testing')
with app.app_context():
    from flask import render_template_string
    template = app.jinja_env.get_template('base.html')
    print('Base template loads successfully')
"</automated>
  </verify>
  <done>
    run.py starts Flask app on port 5000, base.html extends Bootstrap 5 layout
  </done>
  <acceptance_criteria>
    - File run.py exists and contains: `from app import create_app`, `app.run(host='0.0.0.0', port=5000)`
    - File app/templates/base.html exists and contains: `<!DOCTYPE html>`, `{% block content %}`, `{% endblock %}`, Bootstrap 5 CDN link
    - File app/templates/macros.html exists and contains: `{% macro render_field %}`, `{% macro render_checkbox %}`
    - File app/static/css/app.css exists (non-empty)
    - File instance/.gitkeep exists
  </acceptance_criteria>
</task>

<task type="auto">
  <name>Task 3: Create blueprints __init__ files and User model</name>
  <files>
    - app/blueprints/__init__.py
    - app/blueprints/auth/__init__.py
    - app/blueprints/admin/__init__.py
    - app/models/__init__.py
    - app/models/user.py
  </files>
  <read_first>
    - app/blueprints/__init__.py (will be created)
    - app/models/user.py (will be created)
  </read_first>
  <action>
Create the following files with exact content:

**app/blueprints/__init__.py** - Package init:
```python
"""Blueprints package for CertMgr."""
```

**app/blueprints/auth/__init__.py** - Auth blueprint:
```python
"""Authentication blueprint."""
from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

from app.blueprints.auth import routes
```

**app/blueprints/auth/routes.py** - Auth routes (empty for now, will be implemented in Plan 2):
```python
"""Authentication routes - implemented in Plan 2."""
from app.blueprints.auth import auth_bp

__all__ = ['auth_bp']
```

**app/blueprints/admin/__init__.py** - Admin blueprint:
```python
"""Admin blueprint."""
from flask import Blueprint

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

from app.blueprints.admin import routes
```

**app/blueprints/admin/routes.py** - Admin routes (empty for now, will be implemented in Plan 3):
```python
"""Admin routes - implemented in Plan 3."""
from app.blueprints.admin import admin_bp

__all__ = ['admin_bp']
```

**app/models/__init__.py** - Models package:
```python
"""Models package for CertMgr."""
from app.models.user import User

__all__ = ['User']
```

**app/models/user.py** - User model with Flask-Login:
```python
"""User model with Flask-Login integration."""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db


class User(UserMixin, db.Model):
    """User account model."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify the password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'
```
  </action>
  <verify>
    <automated>cd /Users/ice/PycharmProjects/CertMgr && python -c "
from app import create_app
app = create_app('testing')
with app.app_context():
    from app.models.user import User
    from app.extensions import db
    db.create_all()
    user = User(email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    print('User model works:', user.check_password('password123'))
    print('Admin flag:', user.is_admin)
"</automated>
  </verify>
  <done>
    User model exists with email/password, is_admin flag, and Flask-Login UserMixin
  </done>
  <acceptance_criteria>
    - File app/blueprints/__init__.py exists (contains docstring)
    - File app/blueprints/auth/__init__.py exists and contains: `auth_bp = Blueprint('auth', __name__)`
    - File app/blueprints/admin/__init__.py exists and contains: `admin_bp = Blueprint('admin', __name__)`
    - File app/models/__init__.py exists and contains: `from app.models.user import User`
    - File app/models/user.py exists and contains: `class User(UserMixin, db.Model):`, `def set_password`, `def check_password`, `is_admin = db.Column(db.Boolean`
  </acceptance_criteria>
</task>

</tasks>

<verification>
- All Python imports resolve without circular import errors
- `python run.py` starts Flask app on port 5000 (manual test)
- `python -c "from app import create_app; app = create_app()"` runs without errors
</verification>

<success_criteria>
Phase 1 Plan 1 complete when:
- App factory pattern implemented with extensions.py
- Configuration classes (Dev/Prod/Testing) exist
- User model with Flask-Login integration exists
- Base templates with Bootstrap 5 exist
- run.py entry point exists
</success_criteria>

<output>
After completion, create `.planning/phases/01-foundation/01-SUMMARY.md`
</output>
