---
phase: 01-foundation
plan: 03
type: execute
wave: 3
depends_on:
  - 01-foundation-02
files_modified:
  - app/services/file_storage_service.py
  - app/decorators.py
  - app/blueprints/admin/routes.py
  - app/blueprints/admin/templates/users.html
autonomous: true
requirements:
  - CERT-03
  - CERT-11

must_haves:
  truths:
    - "Certificate files are stored with UUID-based paths (no original filenames in storage)"
    - "Admin can view all user accounts in the system"
    - "Users can only view and edit their own certificates (permission enforced)"
    - "File upload/download respects permission boundaries"
  artifacts:
    - path: "app/services/file_storage_service.py"
      provides: "UUID-based file storage with date sharding"
      contains: "def save_file", "uuid.uuid4()", "def allowed_file"
    - path: "app/decorators.py"
      provides: "Permission decorators (admin_required, owner_required)"
      contains: "def admin_required", "def owner_required"
    - path: "app/blueprints/admin/routes.py"
      provides: "Admin user management routes"
      contains: "@admin_bp.route('/users')"
    - path: "app/blueprints/admin/templates/users.html"
      provides: "Admin user list template"
      contains: "{% for user in users %}"
  key_links:
    - from: "app/services/file_storage_service.py"
      to: "app/config.py"
      via: "UPLOAD_FOLDER config"
    - from: "app/decorators.py"
      to: "app/models/user.py"
      via: "current_user.is_admin"
    - from: "app/blueprints/admin/routes.py"
      to: "app/models/user.py"
      via: "User.query.order_by()"
---

<objective>
Implement UUID-based file storage service with date sharding, permission decorators (admin_required, owner_required), and admin user management routes. This ensures files are stored securely without original filenames and permission boundaries are enforced.
</objective>

<execution_context>
@/Users/ice/PycharmProjects/CertMgr/.planning/phases/01-foundation/01-RESEARCH.md
@/Users/ice/PycharmProjects/CertMgr/.planning/phases/01-foundation/02-PLAN.md
</execution_context>

<context>
# Key patterns from research

From 01-RESEARCH.md - UUID-Based File Storage:
```python
class FileStorageService:
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in FileStorageService.ALLOWED_EXTENSIONS

    @staticmethod
    def save_file(file, upload_folder):
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{ext}"
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
```

From 01-RESEARCH.md - Admin-Only Routes with Decorator:
```python
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
```

From 01-RESEARCH.md - Secure File Download with Permission Check:
```python
@certificates_bp.route('/download/<int:cert_id>')
@login_required
def download_certificate(cert_id):
    cert = Certificate.query.get_or_404(cert_id)
    if cert.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    return send_from_directory(...)
```
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create FileStorageService with UUID naming</name>
  <files>
    - app/services/file_storage_service.py
    - app/services/__init__.py
  </files>
  <read_first>
    - app/services/file_storage_service.py (will be created)
  </read_first>
  <action>
Create **app/services/file_storage_service.py** with UUID-based file storage:

```python
"""File storage service with UUID-based naming and date sharding.

This module provides secure file storage for certificate files:
- UUID-based filenames prevent path traversal and filename collisions
- Date sharding (year/month) limits files per directory
- Original filename stored in metadata, not filesystem
- File type and size validation before saving
"""
import os
import uuid
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import current_app


class FileStorageService:
    """Service for secure certificate file storage."""

    # Maximum file size: 10MB
    MAX_FILE_SIZE = 10 * 1024 * 1024

    # Allowed file extensions
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}

    @staticmethod
    def allowed_file(filename: str) -> bool:
        """Check if file extension is allowed.

        Args:
            filename: Original filename

        Returns:
            True if extension is in ALLOWED_EXTENSIONS
        """
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in FileStorageService.ALLOWED_EXTENSIONS

    @staticmethod
    def get_upload_folder() -> Path:
        """Get the upload folder path from config.

        Returns:
            Path object for upload folder
        """
        folder = current_app.config.get('UPLOAD_FOLDER')
        if folder is None:
            folder = Path(current_app.instance_path) / 'uploads'
        elif isinstance(folder, str):
            folder = Path(folder)
        return folder

    @staticmethod
    def validate_file(file) -> tuple[bool, str]:
        """Validate file before saving.

        Args:
            file: Werkzeug FileStorage object

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not file or file.filename == '':
            return False, "No file provided"

        if not FileStorageService.allowed_file(file.filename):
            return False, f"File type not allowed. Allowed: {', '.join(FileStorageService.ALLOWED_EXTENSIONS)}"

        # Check file size
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        if size > FileStorageService.MAX_FILE_SIZE:
            max_mb = FileStorageService.MAX_FILE_SIZE / (1024 * 1024)
            return False, f"File too large. Maximum size: {max_mb}MB"

        return True, ""

    @staticmethod
    def save_file(file) -> dict:
        """Save uploaded file with UUID name and date sharding.

        Args:
            file: Werkzeug FileStorage object

        Returns:
            Dict with keys: path, original_filename, size, stored_name

        Raises:
            ValueError: If file validation fails
        """
        is_valid, error = FileStorageService.validate_file(file)
        if not is_valid:
            raise ValueError(error)

        # Generate UUID-based filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{ext}"

        # Directory sharding by year/month
        now = datetime.utcnow()
        date_path = Path(str(now.year)) / f"{now.month:02d}"

        upload_folder = FileStorageService.get_upload_folder()
        full_dir = upload_folder / date_path
        full_dir.mkdir(parents=True, exist_ok=True)

        full_path = full_dir / unique_filename
        file.save(str(full_path))

        return {
            'path': str(date_path / unique_filename),
            'original_filename': secure_filename(file.filename),
            'size': os.path.getsize(full_path),
            'stored_name': unique_filename
        }

    @staticmethod
    def delete_file(path: str) -> bool:
        """Delete file from storage.

        Args:
            path: Relative path from upload folder (e.g., "2024/03/abc123.pdf")

        Returns:
            True if deleted, False if not found
        """
        upload_folder = FileStorageService.get_upload_folder()
        full_path = upload_folder / path

        if full_path.exists():
            full_path.unlink()
            return True
        return False

    @staticmethod
    def file_exists(path: str) -> bool:
        """Check if file exists in storage.

        Args:
            path: Relative path from upload folder

        Returns:
            True if file exists
        """
        upload_folder = FileStorageService.get_upload_folder()
        full_path = upload_folder / path
        return full_path.exists()

    @staticmethod
    def get_file_size(path: str) -> int:
        """Get file size in bytes.

        Args:
            path: Relative path from upload folder

        Returns:
            File size in bytes, or 0 if not found
        """
        upload_folder = FileStorageService.get_upload_folder()
        full_path = upload_folder / path
        if full_path.exists():
            return os.path.getsize(full_path)
        return 0
```

**app/services/__init__.py** - Update to export FileStorageService:
```python
"""Services package for CertMgr."""
from app.services.auth_service import AuthAdapter, LocalAuthAdapter
from app.services.file_storage_service import FileStorageService

__all__ = ['AuthAdapter', 'LocalAuthAdapter', 'FileStorageService']
```
  </action>
  <verify>
    <automated>cd /Users/ice/PycharmProjects/CertMgr && python -c "
from app import create_app
app = create_app('testing')
with app.app_context():
    from app.services.file_storage_service import FileStorageService
    # Test allowed_file
    assert FileStorageService.allowed_file('test.pdf') == True
    assert FileStorageService.allowed_file('test.exe') == False
    assert FileStorageService.allowed_file('test') == False
    print('allowed_file works correctly')
    print('MAX_FILE_SIZE:', FileStorageService.MAX_FILE_SIZE)
    print('FileStorageService imports correctly')
"</automated>
  </verify>
  <done>
    Files are stored with UUID names in year/month directories, original filename preserved in metadata only
  </done>
  <acceptance_criteria>
    - File app/services/file_storage_service.py exists and contains: `class FileStorageService`, `def save_file`, `uuid.uuid4()`, `def allowed_file`, `def delete_file`
    - File uses date sharding: year/month subdirectories
    - Original filename is NOT used for storage (UUID used instead)
    - File size validation rejects files > 10MB
  </acceptance_criteria>
</task>

<task type="auto">
  <name>Task 2: Create permission decorators</name>
  <files>
    - app/decorators.py
  </files>
  <read_first>
    - app/decorators.py (will be created)
  </read_first>
  <action>
Create **app/decorators.py** with permission decorators:

```python
"""Permission decorators for access control.

This module provides decorators for enforcing access control:
- @admin_required: Only admin users can access
- @owner_required: Only the owner of a resource can access
"""
from functools import wraps
from flask import abort
from flask_login import current_user


def admin_required(f):
    """Decorator that requires the current user to be an admin.

    Usage:
        @admin_required
        def admin_only_route():
            ...

    Returns:
        403 Forbidden if user is not authenticated or not admin
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)  # Unauthorized
        if not current_user.is_admin:
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function


def owner_required(get_owner_id):
    """Decorator factory that requires the current user to own the resource.

    Args:
        get_owner_id: Function that takes the resource and returns owner_id

    Usage:
        @owner_required(lambda cert: cert.user_id)
        def edit_certificate(cert_id):
            ...

    Returns:
        403 Forbidden if user is not authenticated or not owner
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)  # Unauthorized
            # Store the callable for later evaluation in the view
            decorated_function._owner_check = get_owner_id
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def check_resource_permission(resource, owner_id):
    """Check if current user has permission to access a resource.

    Args:
        resource: The resource object (must have user_id or owner_id attribute)
        owner_id: The ID of the owner (or callable that takes resource)

    Returns:
        True if current user is admin or owner

    Raises:
        403 Forbidden if user does not have permission
    """
    if current_user.is_admin:
        return True

    # Handle callable owner_id (from @owner_required decorator)
    if callable(owner_id):
        owner_id = owner_id(resource)

    # Get owner ID from resource
    resource_owner_id = getattr(resource, 'user_id', None) or getattr(resource, 'owner_id', None)

    if resource_owner_id != current_user.id:
        abort(403)

    return True
```
  </action>
  <verify>
    <automated>cd /Users/ice/PycharmProjects/CertMgr && python -c "
from app import create_app
app = create_app('testing')
with app.app_context():
    from app.decorators import admin_required, owner_required, check_resource_permission
    print('Decorators import correctly')
    print('admin_required is a decorator:', hasattr(admin_required, '__call__'))
    print('owner_required is a decorator factory:', hasattr(owner_required, '__call__'))
"</automated>
  </verify>
  <done>
    Admin routes are protected, owner-based access control is available for future use
  </done>
  <acceptance_criteria>
    - File app/decorators.py exists and contains: `def admin_required`, `def owner_required`, `def check_resource_permission`
    - admin_required returns 401 if not authenticated
    - admin_required returns 403 if authenticated but not admin
  </acceptance_criteria>
</task>

<task type="auto">
  <name>Task 3: Create admin blueprint for user management</name>
  <files>
    - app/blueprints/admin/routes.py
    - app/blueprints/admin/templates/users.html
  </files>
  <read_first>
    - app/blueprints/admin/routes.py (was stub - will overwrite)
  </read_first>
  <action>
Read the current admin routes.py stub, then overwrite with:

**app/blueprints/admin/routes.py** - Admin routes for user management:
```python
"""Admin routes for user management and system administration."""
from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models.user import User
from app.decorators import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/users')
@login_required
@admin_required
def list_users():
    """List all users in the system (admin only).

    Displays all registered users with their email, admin status,
    and registration date.
    """
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)


@admin_bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    """Toggle admin status for a user (admin only).

    Cannot toggle admin status on yourself to prevent lockout.
    """
    if user_id == current_user.id:
        abort(400, "Cannot modify your own admin status")

    user = User.query.get_or_404(user_id)
    user.is_admin = not user.is_admin
    db.session.commit()
    return {'success': True, 'is_admin': user.is_admin}


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user account (admin only).

    Cannot delete yourself to prevent lockout.
    """
    if user_id == current_user.id:
        abort(400, "Cannot delete your own account")

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return {'success': True}
```

**app/blueprints/admin/templates/users.html** - User list template:
```html
{% extends "base.html" %}

{% block title %}用户管理 - CertMgr{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <h1 class="mb-4">用户管理 / User Management</h1>

        <div class="card">
            <div class="card-header bg-primary text-white">
                <h4 class="mb-0">所有用户 / All Users</h4>
            </div>
            <div class="card-body">
                <table class="table table-striped table-hover">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>邮箱 / Email</th>
                            <th>角色 / Role</th>
                            <th>注册时间 / Registered</th>
                            <th>操作 / Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for user in users %}
                        <tr>
                            <td>{{ user.id }}</td>
                            <td>{{ user.email }}</td>
                            <td>
                                {% if user.is_admin %}
                                    <span class="badge bg-danger">管理员 / Admin</span>
                                {% else %}
                                    <span class="badge bg-secondary">用户 / User</span>
                                {% endif %}
                            </td>
                            <td>{{ user.created_at.strftime('%Y-%m-%d %H:%M') }}</td>
                            <td>
                                {% if user.id != current_user.id %}
                                    <button class="btn btn-sm btn-warning toggle-admin"
                                            data-user-id="{{ user.id }}"
                                            data-is-admin="{{ user.is_admin|lower }}">
                                        {% if user.is_admin %}撤销管理员{% else %}设为管理员{% endif %}
                                    </button>
                                    <button class="btn btn-sm btn-danger delete-user"
                                            data-user-id="{{ user.id }}">
                                        删除 / Delete
                                    </button>
                                {% else %}
                                    <span class="text-muted">当前用户 / Current</span>
                                {% endif %}
                            </td>
                        </tr>
                        {% else %}
                        <tr>
                            <td colspan="5" class="text-center text-muted">暂无用户 / No users yet</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Toggle admin status
    document.querySelectorAll('.toggle-admin').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const userId = this.dataset.userId;
            const isAdmin = this.dataset.isAdmin === 'true';
            if (!confirm(isAdmin ? '撤销管理员权限？' : '设为管理员？')) return;

            fetch('/admin/users/' + userId + '/toggle-admin', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.content || ''
                }
            }).then(r => r.json()).then(data => {
                if (data.success) location.reload();
            });
        });
    });

    // Delete user
    document.querySelectorAll('.delete-user').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const userId = this.dataset.userId;
            if (!confirm('删除此用户？此操作不可撤销。')) return;

            fetch('/admin/users/' + userId + '/delete', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.content || ''
                }
            }).then(r => r.json()).then(data => {
                if (data.success) location.reload();
            });
        });
    });
});
</script>
{% endblock %}
```
  </action>
  <verify>
    <automated>cd /Users/ice/PycharmProjects/CertMgr && python -c "
from app import create_app
from app.extensions import db
app = create_app('testing')
with app.app_context():
    db.create_all()
    from app.blueprints.admin.routes import admin_bp
    print('Admin blueprint routes load correctly')
"</automated>
  </verify>
  <done>
    Admin can view all users, toggle admin status, and delete users
  </done>
  <acceptance_criteria>
    - File app/blueprints/admin/routes.py exists and contains: `@admin_bp.route('/users')`, `@admin_required`
    - File app/blueprints/admin/templates/users.html exists and contains: `{% for user in users %}`, `{{ user.email }}`
    - Admin users list shows all users
    - Non-admin users get 403 when accessing /admin/users
  </acceptance_criteria>
</task>

</tasks>

<verification>
- FileStorageService saves files with UUID names
- FileStorageService rejects disallowed file types
- FileStorageService rejects files > 10MB
- Admin routes return 403 for non-admin users
- /admin/users accessible only by admin
</verification>

<success_criteria>
Phase 1 Plan 3 complete when:
- FileStorageService stores files with UUID paths
- Permission decorators work (admin_required blocks non-admins)
- Admin can view all users in system
- Users cannot access admin routes
</success_criteria>

<output>
After completion, create `.planning/phases/01-foundation/03-SUMMARY.md`
</output>
