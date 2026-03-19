# Phase 1: Foundation / 基础架构 - Research

**Researched:** 2026-03-19
**Domain:** Flask application factory, authentication, file storage, permission control
**Confidence:** HIGH (based on verified PyPI versions + Pallets official documentation)

## Summary

Phase 1 establishes the Flask application foundation with authentication and file storage infrastructure. The core technologies (Flask 3.1.3, Flask-Login 0.6.3, Flask-SQLAlchemy 3.1.1) are stable and well-documented. The app factory pattern with `extensions.py` is the standard approach recommended by Pallets Projects. Key implementation decisions include: UUID-based file storage to prevent path traversal and filename collisions, a simple admin flag on User model for Phase 1 permission control, and Flask-Login for session management with "remember me" functionality.

Primary recommendation: Use the Flask application factory pattern from day one, keep extensions in `extensions.py` to avoid circular imports, and implement the auth adapter interface to prepare for Phase 3 SSO integration.

## Standard Stack

### Core Dependencies (Verified from PyPI)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Flask | 3.1.3 | Web framework | Pallets Projects flagship, Python >=3.9 |
| Flask-SQLAlchemy | 3.1.1 | ORM | Official Flask ORM extension, SQLAlchemy 2.x |
| Flask-Migrate | 4.1.0 | Database migrations | Alembic wrapper, schema changes without data loss |
| Flask-Login | 0.6.3 | Session management | Standard for Flask auth, login_required decorator |
| Flask-WTF | 1.2.2 | Form validation + CSRF | Integrates WTForms, CSRF required for file uploads |
| WTForms | 3.2.1 | Form handling | Required by Flask-WTF, Python >=3.9 |
| SQLAlchemy | 2.0.48 | ORM core | Powers Flask-SQLAlchemy |
| psycopg2-binary | 2.9.11 | PostgreSQL adapter | Production database driver |
| Pillow | 11.3.0 | Image processing | Already installed, thumbnail generation |
| python-dotenv | 1.2.1 | Environment config | Load .env files in development |
| waitress | 3.0.2 | WSGI server | Windows-compatible, pure Python |

**Installation:**
```bash
pip install Flask==3.1.3 Flask-SQLAlchemy==3.1.1 Flask-Migrate==4.1.0 Flask-Login==0.6.3 Flask-WTF==1.2.2 WTForms==3.2.1 SQLAlchemy==2.0.48 psycopg2-binary==2.9.11 Pillow==11.3.0 python-dotenv==1.2.1 waitress==3.0.2
```

### Frontend (CDN)

| Library | Version | Purpose |
|---------|---------|---------|
| Bootstrap | 5.3.8 | UI framework, responsive grid |
| DataTables | 1.11+ | Server-side pagination (Phase 2) |

## Architecture Patterns

### Recommended Project Structure

```
CertMgr/
├── app/
│   ├── __init__.py          # Application factory, blueprint registration
│   ├── config.py            # Configuration classes (Dev/Prod/Testing)
│   ├── extensions.py        # Shared Flask extension instances
│   │
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py          # User model with password hashing
│   │   ├── certificate.py   # Certificate model (Phase 2)
│   │   └── certificate_type.py  # Certificate types (Phase 2)
│   │
│   ├── blueprints/          # Modular route containers
│   │   ├── __init__.py
│   │   ├── auth/            # Authentication module
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   ├── forms.py
│   │   │   └── templates/
│   │   ├── admin/           # Admin management module
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── templates/
│   │   └── certificates/    # Certificate CRUD (Phase 2)
│   │       ├── __init__.py
│   │       ├── routes.py
│   │       └── services.py
│   │
│   ├── services/            # Business logic layer
│   │   ├── __init__.py
│   │   ├── file_storage_service.py  # UUID-based file storage
│   │   └── auth_service.py  # Auth adapter interface (Phase 3 SSO)
│   │
│   ├── templates/           # Base templates
│   │   ├── base.html
│   │   └── macros.html
│   │
│   └── static/
│       ├── css/
│       └── js/
│
├── instance/                # Instance-specific files (NOT in git)
│   ├── config.py            # Local overrides
│   └── uploads/             # Certificate file storage
│
├── migrations/              # Alembic database migrations
├── tests/                   # pytest
├── requirements.txt
└── run.py                   # Application entry point
```

### Pattern 1: Flask Application Factory

**What:** `create_app()` function that instantiates Flask app with configuration

**When to use:** All Flask projects, especially those with blueprints, testing, or multiple environments

**Source:** [Flask Application Factory Pattern](https://flask.palletsprojects.com/en/stable/tutorial/factory/)

```python
# app/__init__.py
from flask import Flask
from app.extensions import db, login_manager

def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)

    # Load config
    if config:
        app.config.from_object(config)
    app.config.from_prefixed_env()

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from app.blueprints.auth import auth_bp
    app.register_blueprint(auth_bp)

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))

    return app

# run.py
from app import create_app
app = create_app()

if __name__ == '__main__':
    app.run()
```

### Pattern 2: Extensions Module (Avoid Circular Imports)

**What:** Centralized extension instances in `extensions.py`

**When to use:** Always, to avoid circular import problems

**Source:** [Flask Extension Development](https://flask.palletsprojects.com/en/stable/extensiondev/)

```python
# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

login_manager.login_view = 'auth.login'  # Redirect here if unauthorized
```

### Pattern 3: User Model with Flask-Login

**What:** User model implementing `UserMixin` for Flask-Login compatibility

**When to use:** User authentication is needed

**Source:** [Flask-Login Documentation](https://flask-login.readthedocs.io/en/stable/)

```python
# app/models/user.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to certificates (Phase 2)
    # certificates = db.relationship('Certificate', backref='owner', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'
```

### Pattern 4: Auth Blueprint with Flask-WTF Forms

**What:** Registration and login forms with WTForms validation

**When to use:** User registration and login flows

```python
# app/blueprints/auth/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

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

```python
# app/blueprints/auth/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models.user import User
from app.blueprints.auth.forms import RegistrationForm, LoginForm

auth_bp = Blueprint('auth', __name__)

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

### Pattern 5: Admin-Only Routes with Decorator

**What:** Custom decorator for admin-only access control

**When to use:** Routes that only admins can access

```python
# app/decorators.py
from functools import wraps
from flask import abort
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function
```

### Pattern 6: UUID-Based File Storage

**What:** Files stored with UUID names, original filename in database metadata

**When to use:** Certificate file uploads

**Source:** [Flask File Uploads Pattern](https://flask.palletsprojects.com/en/stable/patterns/fileuploads/)

```python
# app/services/file_storage_service.py
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename

class FileStorageService:
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in FileStorageService.ALLOWED_EXTENSIONS

    @staticmethod
    def save_file(file, upload_folder):
        """Save uploaded file with UUID name, return metadata dict."""
        if not file or file.filename == '':
            raise ValueError("No file provided")

        if not FileStorageService.allowed_file(file.filename):
            raise ValueError(f"File type not allowed: {file.filename}")

        # Generate UUID-based filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{ext}"

        # Directory sharding by year/month
        now = datetime.utcnow()
        date_path = os.path.join(str(now.year), f"{now.month:02d}")

        full_dir = os.path.join(upload_folder, date_path)
        os.makedirs(full_dir, exist_ok=True)

        full_path = os.path.join(full_dir, unique_filename)
        file.save(full_path)

        return {
            'path': os.path.join(date_path, unique_filename),
            'original_filename': secure_filename(file.filename),
            'size': os.path.getsize(full_path),
            'stored_name': unique_filename
        }

    @staticmethod
    def delete_file(path, upload_folder):
        """Delete file from storage."""
        full_path = os.path.join(upload_folder, path)
        if os.path.exists(full_path):
            os.remove(full_path)
```

### Pattern 7: Secure File Download with Permission Check

**What:** File download through Flask route with ownership verification

**When to use:** Serving certificate files

```python
# app/blueprints/certificates/routes.py
from flask import send_from_directory, abort
from flask_login import login_required, current_user
from app.decorators import admin_required

@certificates_bp.route('/download/<int:cert_id>')
@login_required
def download_certificate(cert_id):
    cert = Certificate.query.get_or_404(cert_id)

    # Permission check: owner or admin only
    if cert.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        cert.file_path,
        as_attachment=True,
        download_name=cert.original_filename  # Use stored original name
    )
```

### Anti-Patterns to Avoid

- **Global Flask app instance:** Creates circular imports and prevents testing. Always use `create_app()` factory.

- **Circular imports via models:** Never import `db` from `app/__init__.py` in models. Use `from app.extensions import db` instead.

- **Preserving original filenames in storage:** Enables path traversal, collisions, and Unicode issues. Always rename to UUID.

- **Auth checks inline in routes:** Repetitive and error-prone. Use `@admin_required` or `@owner_required` decorators.

- **Storing files without size limits:** Server resource exhaustion. Always validate `MAX_CONTENT_LENGTH` and check file size before saving.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Password hashing | Custom salt+hash | `werkzeug.security` | Properly handles salt, pepper, timing attacks |
| Session management | Custom session cookies | Flask-Login | Handles remember_me, session fixation protection |
| CSRF protection | Double-submit cookie | Flask-WTF CSRFProtect | Validated, tested implementation |
| File type validation | Extension blacklist | `mimetypes` + content sniffing | Extension alone is trivially bypassed |
| Permission decorators | Inline if statements | Custom decorators | Consistent, testable, DRY |
| Auth adapter interface | Hard-coded local auth | Abstract base class | Enables Phase 3 SSO swap without code changes |

## Common Pitfalls

### Pitfall 1: Circular Import Hell

**What goes wrong:** `ImportError: cannot import name 'db' from 'app'` or similar errors on startup.

**Why it happens:** `app/__init__.py` imports models, models import `db` from `app/__init__.py`.

**How to avoid:** Put all shared extension instances in `app/extensions.py`. Import from `extensions.py` in both `__init__.py` and models.

**Warning signs:** Any import error mentioning your own modules.

### Pitfall 2: CSRF Token Missing on Forms

**What goes wrong:** Form submissions rejected with 400 error.

**Why it happens:** Flask-WTF requires `{{ csrf_token() }}` in forms.

**How to avoid:** Use `{{ form.hidden_tag() }}` instead of manually adding fields - it includes both CSRF token and any other hidden fields.

### Pitfall 3: File Path Traversal via Upload

**What goes wrong:** Malicious user uploads file to arbitrary path (e.g., `../../etc/passwd`).

**Why it happens:** Trusting user-provided filename.

**How to avoid:** Always generate UUID filenames server-side. Never use `secure_filename()` alone - it doesn't prevent all traversal.

### Pitfall 4: Session Fixation After Login

**What goes wrong:** Attacker can hijack session after user logs in.

**Why it happens:** Not regenerating session ID after authentication.

**How to avoid:** Flask-Login's `login_user()` regenerates session ID automatically. Don't disable this.

### Pitfall 5: Missing `UPLOAD_FOLDER` Instance Path

**What goes wrong:** Files saved to git-tracked directory, accidentally committed, or deleted on redeploy.

**Why it happens:** Using relative path or path inside project directory.

**How to avoid:** Use `instance_relative_config=True` in Flask constructor and store uploads in `instance/uploads/`. Add `instance/` to `.gitignore`.

## Code Examples

### Flask Application Factory Complete Setup

```python
# app/__init__.py
from flask import Flask
from app.extensions import db, login_manager, csrf
from app.models import user  # Import models to register them

def create_app(config_name='default'):
    app = Flask(__name__, instance_relative_config=True)

    # Load configuration
    app.config.from_object(f'app.config.{config_name.title()}Config')
    app.config.from_prefixed_env()  # Load .env file

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Configure login
    login_manager.session_protection = 'strong'

    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))

    # Register blueprints
    from app.blueprints.auth import auth_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.certificates import certificates_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(certificates_bp)

    # Create tables if needed (development only)
    with app.app_context():
        db.create_all()

    return app
```

### WTForms Login Form with CSRF

```html
<!-- app/blueprints/auth/templates/login.html -->
{% extends "base.html" %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">Login</div>
            <div class="card-body">
                <form method="POST" action="{{ url_for('auth.login') }}">
                    {{ form.hidden_tag() }}  <!-- CSRF token included -->

                    <div class="mb-3">
                        {{ form.email.label(class="form-label") }}
                        {{ form.email(class="form-control") }}
                        {% if form.email.errors %}
                            <span class="text-danger">{{ form.email.errors[0] }}</span>
                        {% endif %}
                    </div>

                    <div class="mb-3">
                        {{ form.password.label(class="form-label") }}
                        {{ form.password(class="form-control") }}
                        {% if form.password.errors %}
                            <span class="text-danger">{{ form.password.errors[0] }}</span>
                        {% endif %}
                    </div>

                    <div class="mb-3 form-check">
                        {{ form.remember_me(class="form-check-input") }}
                        {{ form.remember_me.label(class="form-check-label") }}
                    </div>

                    {{ form.submit(class="btn btn-primary") }}
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### Admin Route with Permission Check

```python
# app/blueprints/admin/routes.py
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.decorators import admin_required
from app.models.user import User

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/users')
@login_required
@admin_required
def list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)
```

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| AUTH-01 | User can register account with email and password | Flask-Login session management, User model with password hashing, Registration form/flow |
| AUTH-02 | Auth adapter interface (pluggable SSO) | Auth service abstract base class pattern, `AUTH_BACKEND` config variable, Phase 3 locked to use this |
| CERT-03 | File storage with UUID-based paths | FileStorageService with UUID naming, date sharding, `secure_filename()` for original name |
| CERT-11 | Permission control (user vs admin) | `is_admin` flag on User, `@admin_required` decorator, ownership check in download route |

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Global `app = Flask(__name__)` | App factory `create_app()` | Flask 0.7+ (2009) | Enables testing, multiple configs, blueprints |
| Plain `request.form` forms | Flask-WTF with WTForms | 2013 | CSRF protection, validation, reusability |
| Session cookies without signing | Flask session with `SECRET_KEY` | Flask 1.0 (2013) | Prevents session tampering |
| EAV for dynamic fields | JSONB column with schema | PostgreSQL 9.2+ (2012) | Flexible, indexable, no migrations for new fields |
| Gunicorn on Windows | Waitress | Waitress 1.0 (2016) | Native Windows support, no C extensions |

**Deprecated/outdated:**
- Flask-Login 0.4.x: `login_user(user, remember=True)` deprecated `remember` param, use `remember=True` as keyword
- SQLAlchemy 1.x: Declarative base changed in 2.0, use `db.Model` from Flask-SQLAlchemy
- Bootstrap 3/4: Security updates ended, migration to 5.3 needed

## Open Questions

1. **Database choice (SQLite vs PostgreSQL)**
   - What we know: STACK.md recommends PostgreSQL for production; ARCHITECTURE.md shows PostgreSQL JSONB schema
   - What's unclear: Has the school IT environment been determined?
   - Recommendation: Default to PostgreSQL for production, but Phase 1 can start with SQLite for dev simplicity if migration path is documented

2. **Email delivery for password reset**
   - What we know: Phase 1 success criteria don't include password reset
   - What's unclear: Should AUTH-02 include password reset as part of auth adapter?
   - Recommendation: Defer password reset to Phase 2 or later; implement now only if critical for Phase 1 demo

3. **Initial admin user creation**
   - What we know: Need admin accounts for testing
   - What's unclear: How should first admin be created? CLI command? Self-registration with email domain whitelist?
   - Recommendation: Create admin via CLI command: `flask admin create-superuser --email admin@school.edu`

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.x + pytest-flask |
| Config file | `pytest.ini` or `pyproject.toml` |
| Quick run command | `pytest tests/ -x -q` |
| Full suite command | `pytest tests/ -v` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| AUTH-01 | User can register with email/password | integration | `pytest tests/test_auth.py::test_register -x` | no |
| AUTH-01 | Registration rejects duplicate email | unit | `pytest tests/test_auth.py::test_register_duplicate -x` | no |
| AUTH-01 | Registration validates email format | unit | `pytest tests/test_auth.py::test_register_invalid_email -x` | no |
| AUTH-01 | Registration requires password >= 8 chars | unit | `pytest tests/test_auth.py::test_register_short_password -x` | no |
| AUTH-01 | Login succeeds with correct credentials | integration | `pytest tests/test_auth.py::test_login -x` | no |
| AUTH-01 | Login fails with wrong password | unit | `pytest tests/test_auth.py::test_login_wrong_password -x` | no |
| AUTH-01 | Remember-me persists session | integration | `pytest tests/test_auth.py::test_remember_me -x` | no |
| AUTH-02 | Auth adapter interface defined | unit | `pytest tests/test_auth.py::test_auth_adapter_interface -x` | no |
| CERT-03 | File saved with UUID name, not original | unit | `pytest tests/test_file_storage.py::test_uuid_naming -x` | no |
| CERT-03 | File stored in year/month directory | unit | `pytest tests/test_file_storage.py::test_date_sharding -x` | no |
| CERT-03 | Upload rejects disallowed file types | unit | `pytest tests/test_file_storage.py::test_disallowed_extension -x` | no |
| CERT-03 | Upload rejects files > 10MB | unit | `pytest tests/test_file_storage.py::test_file_size_limit -x` | no |
| CERT-11 | Non-owner cannot download certificate | integration | `pytest tests/test_permissions.py::test_download_forbidden -x` | no |
| CERT-11 | Admin can view all users | integration | `pytest tests/test_admin.py::test_admin_list_users -x` | no |
| CERT-11 | Non-admin cannot access admin routes | integration | `pytest tests/test_admin.py::test_non_admin_forbidden -x` | no |
| CERT-11 | File download checks ownership | unit | `pytest tests/test_permissions.py::test_download_checks_owner -x` | no |

### Sampling Rate
- **Per task commit:** `pytest tests/ -x -q` (fail fast)
- **Per wave merge:** `pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/conftest.py` - pytest fixtures (app, db, client, authenticated_client)
- [ ] `tests/test_auth.py` - AUTH-01 tests
- [ ] `tests/test_file_storage.py` - CERT-03 tests
- [ ] `tests/test_permissions.py` - CERT-11 tests
- [ ] `tests/test_admin.py` - admin route tests
- [ ] `pytest.ini` or `pyproject.toml` - test configuration
- [ ] Install: `pip install pytest pytest-flask`

## Sources

### Primary (HIGH confidence)
- [Flask 3.1.x PyPI](https://pypi.org/project/Flask/) - verified version 3.1.3
- [Flask-Login 0.6.x PyPI](https://pypi.org/project/Flask-Login/) - verified version 0.6.3
- [Flask-SQLAlchemy 3.1.x PyPI](https://pypi.org/project/Flask-SQLAlchemy/) - verified version 3.1.1
- [Flask-Migrate 4.1.x PyPI](https://pypi.org/project/Flask-Migrate/) - verified version 4.1.0
- [Flask-WTF 1.2.x PyPI](https://pypi.org/project/Flask-WTF/) - verified version 1.2.2
- [waitress 3.0.x PyPI](https://pypi.org/project/waitress/) - verified version 3.0.2
- [Flask Application Factory](https://flask.palletsprojects.com/en/stable/tutorial/factory/) - official pattern
- [Flask Extension Development](https://flask.palletsprojects.com/en/stable/extensiondev/) - extensions.py pattern
- [Flask File Uploads](https://flask.palletsprojects.com/en/stable/patterns/fileuploads/) - secure file handling

### Secondary (MEDIUM-HIGH confidence)
- [Flask-Login Documentation](https://flask-login.readthedocs.io/en/stable/) - user loader pattern, session protection
- [WTForms Documentation](https://wtforms.readthedocs.io/en/stable/) - form validation
- [Flask Deployment](https://flask.palletsprojects.com/en/stable/deploying/) - ProxyFix for IIS

### From Project Research (MEDIUM-HIGH confidence)
- `.planning/research/ARCHITECTURE.md` - project structure, auth adapter pattern, file storage strategy
- `.planning/research/STACK.md` - verified library versions, Windows Server considerations
- `.planning/research/PITFALLS.md` - UUID naming, CSRF, circular imports, path traversal

## Metadata

**Confidence breakdown:**
- Standard Stack: HIGH - all versions verified from PyPI
- Architecture: HIGH - Flask app factory is well-established Pallets pattern
- Pitfalls: HIGH - documented from official Flask docs and common community knowledge

**Research date:** 2026-03-19
**Valid until:** 2026-04-19 (30 days for stable libraries)
