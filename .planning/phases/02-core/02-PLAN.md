---
phase: 02-core
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - app/models/certificate.py
  - app/blueprints/certificates/__init__.py
  - app/blueprints/certificates/routes.py
  - app/blueprints/certificates/forms.py
  - app/blueprints/certificates/services.py
  - app/blueprints/certificates/templates/list.html
  - app/blueprints/certificates/templates/detail.html
  - app/blueprints/certificates/templates/upload.html
  - app/blueprints/certificates/templates/edit.html
  - app/__init__.py
autonomous: true
requirements:
  - CERT-01
  - CERT-02
  - CERT-04
  - CERT-05

must_haves:
  truths:
    - "User can upload certificate file (image/PDF) and associate with their account"
    - "User can view list of their own certificates displayed as cards with thumbnail, title, type, date"
    - "User can view certificate detail page and edit/delete from there"
    - "Different certificate types show different dynamic fields in upload/edit forms"
    - "Admin can view all certificates in the system"
    - "Admin can edit/delete any certificate"
  artifacts:
    - path: "app/models/certificate.py"
      provides: "Certificate and CertificateType models with JSONB dynamic fields"
      contains: "class CertificateType", "class Certificate", "fields = db.Column(db.JSON)"
    - path: "app/blueprints/certificates/routes.py"
      provides: "CRUD routes for certificates"
      contains: "@certificates_bp.route('/upload')", "@certificates_bp.route('/<int:cert_id>')", "@certificates_bp.route('/<int:cert_id>/edit')"
    - path: "app/blueprints/certificates/templates/list.html"
      provides: "Card grid display of certificates"
      contains: "card layout", "card-img-top", "card-body"
    - path: "app/blueprints/certificates/templates/detail.html"
      provides: "Certificate detail with edit/delete buttons"
      contains: "detail view", "edit button", "delete button"
    - path: "app/blueprints/certificates/templates/upload.html"
      provides: "Upload form with dynamic fields"
      contains: "certificate_type_id", "dynamic-fields-container", "FIELD_SCHEMAS"
  key_links:
    - from: "app/__init__.py"
      to: "certificates_bp"
      via: "register_blueprint(certificates_bp)"
    - from: "app/blueprints/certificates/routes.py"
      to: "app/models/certificate.py"
      via: "import Certificate, CertificateType"
    - from: "app/blueprints/certificates/templates/upload.html"
      to: "app/blueprints/certificates/forms.py"
      via: "form.certificate_type_id"
---

<objective>
Wave 1: Create Certificate model with JSONB dynamic fields, implement full CRUD routes (upload, list, detail, edit, delete), and build card-based templates. Certificate types: 比赛获奖证书, 荣誉证书, 资格证, 职业技能等级证书. Dynamic fields switch on same page based on selected type.
</objective>

<execution_context>
@/Users/ice/PycharmProjects/CertMgr/.planning/phases/02-core/02-RESEARCH.md
@/Users/ice/PycharmProjects/CertMgr/.planning/phases/02-core/02-CONTEXT.md
@/Users/ice/PycharmProjects/CertMgr/app/models/user.py
@/Users/ice/PycharmProjects/CertMgr/app/extensions.py
</execution_context>

<context>
# User Decisions (locked - MUST implement per CONTEXT.md)

| Decision | Value |
|----------|-------|
| Certificate List Layout | Card layout with thumbnail preview, title, type, date |
| Dynamic Fields Switching | Single page dynamic switching - same form/page, fields change based on selected certificate type |
| Certificate Types | 比赛获奖证书, 荣誉证书, 资格证, 职业技能等级证书 |
| Certificate Edit/Delete | Detail page operation - open certificate detail page first, then edit/delete |

# Certificate Model Pattern (from 02-RESEARCH.md)

```python
class CertificateType(db.Model):
    __tablename__ = 'certificate_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    fields_schema = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Certificate(db.Model):
    __tablename__ = 'certificates'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    certificate_type_id = db.Column(db.Integer, db.ForeignKey('certificate_types.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    original_filename = db.Column(db.String(255))
    file_size = db.Column(db.Integer)
    file_mime_type = db.Column(db.String(100))
    fields = db.Column(db.JSON)  # Dynamic fields stored as JSONB
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

# Dynamic Field Schemas (from 02-RESEARCH.md)

```python
FIELD_SCHEMAS = {
    '比赛获奖证书': [
        {'name': 'competition_name', 'label': '比赛名称', 'type': 'string', 'required': True},
        {'name': 'award_level', 'label': '获奖等级', 'type': 'select', 'options': ['一等奖', '二等奖', '三等奖', '优秀奖'], 'required': True},
        {'name': 'award_date', 'label': '获奖日期', 'type': 'date', 'required': True},
        {'name': 'organizer', 'label': '主办单位', 'type': 'string', 'required': True},
        {'name': 'certificate_number', 'label': '证书编号', 'type': 'string', 'required': False},
    ],
    '荣誉证书': [
        {'name': 'honor_title', 'label': '荣誉名称', 'type': 'string', 'required': True},
        {'name': 'grant_date', 'label': '授予日期', 'type': 'date', 'required': True},
        {'name': 'grantor', 'label': '授予单位', 'type': 'string', 'required': True},
        {'name': 'reason', 'label': '获得原因', 'type': 'text', 'required': False},
    ],
    '资格证': [
        {'name': 'certificate_name', 'label': '证书名称', 'type': 'string', 'required': True},
        {'name': 'certificate_number', 'label': '证书编号', 'type': 'string', 'required': True},
        {'name': 'issue_date', 'label': '发证日期', 'type': 'date', 'required': True},
        {'name': 'expiry_date', 'label': '有效期至', 'type': 'date', 'required': False},
        {'name': 'issuing_authority', 'label': '发证机构', 'type': 'string', 'required': True},
    ],
    '职业技能等级证书': [
        {'name': 'skill_name', 'label': '职业技能名称', 'type': 'string', 'required': True},
        {'name': 'skill_level', 'label': '等级', 'type': 'select', 'options': ['五级/初级工', '四级/中级工', '三级/高级工', '二级/技师', '一级/高级技师'], 'required': True},
        {'name': 'certificate_number', 'label': '证书编号', 'type': 'string', 'required': True},
        {'name': 'issue_date', 'label': '发证日期', 'type': 'date', 'required': True},
        {'name': 'issuing_authority', 'label': '发证机构', 'type': 'string', 'required': True},
    ],
}
```

# Card Layout Pattern (Bootstrap 5)

```html
<div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
    {% for cert in certificates %}
    <div class="col">
        <div class="card h-100">
            <img src="..." class="card-img-top" style="height: 180px; object-fit: cover;">
            <div class="card-body">
                <h5 class="card-title">{{ cert.title }}</h5>
                <span class="badge bg-primary">{{ cert.certificate_type.name }}</span>
            </div>
            <div class="card-footer">
                <a href="{{ url_for('certificates.detail', cert_id=cert.id) }}" class="btn btn-sm btn-outline-primary">查看详情</a>
            </div>
        </div>
    </div>
    {% endfor %}
</div>
```

# Existing Patterns to Follow

From app/models/user.py:
- `db.Model` base class, `datetime.utcnow` for timestamps
- Relationship pattern: `db.relationship('User', backref=db.backref('certificates', lazy='dynamic'))`

From app/blueprints/admin/routes.py:
- Use `@login_required` and `@admin_required` decorators
- Use `db.session.commit()` after modifications
- Use `flash()` for user feedback
- Permission pattern: `if not admin and owner_id != current_user.id: abort(403)`
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create Certificate and CertificateType models</name>
  <files>
    - app/models/certificate.py
    - app/models/__init__.py
  </files>
  <read_first>
    - app/models/user.py (pattern reference)
    - app/extensions.py (db instance)
  </read_first>
  <action>
Create app/models/certificate.py:

```python
"""Certificate models with JSONB dynamic fields."""
from datetime import datetime
from app.extensions import db

class CertificateType(db.Model):
    """Certificate type lookup table."""
    __tablename__ = 'certificate_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    fields_schema = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<CertificateType {self.name}>'


class Certificate(db.Model):
    """Certificate record with dynamic fields stored in JSONB."""
    __tablename__ = 'certificates'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    certificate_type_id = db.Column(db.Integer, db.ForeignKey('certificate_types.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    original_filename = db.Column(db.String(255))
    file_size = db.Column(db.Integer)
    file_mime_type = db.Column(db.String(100))
    fields = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = db.relationship('User', backref=db.backref('certificates', lazy='dynamic'))
    certificate_type = db.relationship('CertificateType', backref=db.backref('certificates', lazy='dynamic'))

    def __repr__(self):
        return f'<Certificate {self.id}: {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'type': self.certificate_type.name if self.certificate_type else None,
            'type_id': self.certificate_type_id,
            'file_path': self.file_path,
            'file_mime_type': self.file_mime_type,
            'fields': self.fields or {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
```

Update app/models/__init__.py:
```python
"""Models package for CertMgr."""
from app.models.user import User
from app.models.certificate import Certificate, CertificateType

__all__ = ['User', 'Certificate', 'CertificateType']
```

Update app/__init__.py - add this inside create_app() after db.create_all():
```python
# Seed certificate types if they don't exist
from app.models.certificate import CertificateType
CERT_TYPES = [
    {'name': '比赛获奖证书', 'fields_schema': []},
    {'name': '荣誉证书', 'fields_schema': []},
    {'name': '资格证', 'fields_schema': []},
    {'name': '职业技能等级证书', 'fields_schema': []},
]
for ct_data in CERT_TYPES:
    if not CertificateType.query.filter_by(name=ct_data['name']).first():
        ct = CertificateType(name=ct_data['name'], fields_schema=ct_data['fields_schema'])
        db.session.add(ct)
db.session.commit()
```
  </action>
  <verify>
    <automated>cd /Users/ice/PycharmProjects/CertMgr && python -c "
from app import create_app
app = create_app('testing')
with app.app_context():
    from app.extensions import db
    from app.models.certificate import Certificate, CertificateType
    db.create_all()
    types = CertificateType.query.all()
    print('CertificateType count:', len(types))
    print('Types:', [t.name for t in types])
    cert = Certificate(title='Test', file_path='/test', user_id=1, certificate_type_id=1)
    db.session.add(cert)
    db.session.commit()
    print('Certificate to_dict:', cert.to_dict())
"</automated>
  </verify>
  <done>
    Certificate and CertificateType models exist with JSONB fields, seeded with 4 types
  </done>
  <acceptance_criteria>
    - File app/models/certificate.py exists and contains: `class CertificateType`, `class Certificate`, `fields = db.Column(db.JSON)`
    - File app/models/__init__.py contains: `from app.models.certificate import Certificate, CertificateType`
    - Running create_app() seeds 4 certificate types
    - Certificate.to_dict() returns JSON-serializable dict
  </acceptance_criteria>
</task>

<task type="auto">
  <name>Task 2: Create certificate forms with dynamic fields</name>
  <files>
    - app/blueprints/certificates/forms.py
  </files>
  <read_first>
    - app/blueprints/auth/forms.py (existing form pattern)
  </read_first>
  <action>
Create app/blueprints/certificates/forms.py:

```python
"""Certificate forms with dynamic field support."""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SelectField, TextAreaField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Optional

FIELD_SCHEMAS = {
    '比赛获奖证书': [
        {'name': 'competition_name', 'label': '比赛名称', 'type': 'string', 'required': True},
        {'name': 'award_level', 'label': '获奖等级', 'type': 'select', 'options': ['一等奖', '二等奖', '三等奖', '优秀奖'], 'required': True},
        {'name': 'award_date', 'label': '获奖日期', 'type': 'date', 'required': True},
        {'name': 'organizer', 'label': '主办单位', 'type': 'string', 'required': True},
        {'name': 'certificate_number', 'label': '证书编号', 'type': 'string', 'required': False},
    ],
    '荣誉证书': [
        {'name': 'honor_title', 'label': '荣誉名称', 'type': 'string', 'required': True},
        {'name': 'grant_date', 'label': '授予日期', 'type': 'date', 'required': True},
        {'name': 'grantor', 'label': '授予单位', 'type': 'string', 'required': True},
        {'name': 'reason', 'label': '获得原因', 'type': 'text', 'required': False},
    ],
    '资格证': [
        {'name': 'certificate_name', 'label': '证书名称', 'type': 'string', 'required': True},
        {'name': 'certificate_number', 'label': '证书编号', 'type': 'string', 'required': True},
        {'name': 'issue_date', 'label': '发证日期', 'type': 'date', 'required': True},
        {'name': 'expiry_date', 'label': '有效期至', 'type': 'date', 'required': False},
        {'name': 'issuing_authority', 'label': '发证机构', 'type': 'string', 'required': True},
    ],
    '职业技能等级证书': [
        {'name': 'skill_name', 'label': '职业技能名称', 'type': 'string', 'required': True},
        {'name': 'skill_level', 'label': '等级', 'type': 'select', 'options': ['五级/初级工', '四级/中级工', '三级/高级工', '二级/技师', '一级/高级技师'], 'required': True},
        {'name': 'certificate_number', 'label': '证书编号', 'type': 'string', 'required': True},
        {'name': 'issue_date', 'label': '发证日期', 'type': 'date', 'required': True},
        {'name': 'issuing_authority', 'label': '发证机构', 'type': 'string', 'required': True},
    ],
}


class CertificateBaseForm(FlaskForm):
    """Base form with fixed certificate fields."""
    certificate_type_id = SelectField('证书类型 / Certificate Type', coerce=int, validators=[DataRequired(message='请选择证书类型')])
    title = StringField('证书标题 / Title', validators=[DataRequired(message='请输入证书标题')])
    file = FileField('证书文件 / Certificate File', validators=[
        FileRequired(message='请选择证书文件'),
        FileAllowed(['pdf', 'png', 'jpg', 'jpeg', 'gif'], '只能是 PDF 或图片文件')
    ])
    submit = SubmitField('提交 / Submit')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from app.models.certificate import CertificateType
        self.certificate_type_id.choices = [
            (ct.id, ct.name) for ct in CertificateType.query.order_by('name').all()
        ]


class CertificateEditForm(FlaskForm):
    """Form for editing existing certificate (file optional)."""
    certificate_type_id = SelectField('证书类型 / Certificate Type', coerce=int, validators=[DataRequired(message='请选择证书类型')])
    title = StringField('证书标题 / Title', validators=[DataRequired(message='请输入证书标题')])
    file = FileField('证书文件 / Certificate File', validators=[Optional()])
    submit = SubmitField('保存 / Save')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from app.models.certificate import CertificateType
        self.certificate_type_id.choices = [
            (ct.id, ct.name) for ct in CertificateType.query.order_by('name').all()
        ]
```
  </action>
  <verify>
    <automated>cd /Users/ice/PycharmProjects/CertMgr && python -c "
from app import create_app
app = create_app()
with app.app_context():
    from app.blueprints.certificates.forms import CertificateBaseForm, FIELD_SCHEMAS
    from app.models.certificate import CertificateType
    print('FIELD_SCHEMAS keys:', list(FIELD_SCHEMAS.keys()))
    form = CertificateBaseForm()
    print('Form certificate_type_id choices:', [(c.id, c.name) for c in CertificateType.query.all()])
"</automated>
  </verify>
  <done>
    CertificateBaseForm and CertificateEditForm exist with certificate_type_id select populated from database
  </done>
  <acceptance_criteria>
    - File app/blueprints/certificates/forms.py exists
    - FIELD_SCHEMAS contains all 4 types
    - CertificateBaseForm has certificate_type_id, title, file, submit fields
    - CertificateEditForm has optional file field for updates
  </acceptance_criteria>
</task>

<task type="auto">
  <name>Task 3: Implement certificate CRUD routes and services</name>
  <files>
    - app/blueprints/certificates/routes.py
    - app/blueprints/certificates/services.py
    - app/blueprints/certificates/__init__.py
  </files>
  <read_first>
    - app/blueprints/certificates/__init__.py (stub to replace)
    - app/blueprints/auth/routes.py (route pattern)
    - app/blueprints/admin/routes.py (admin pattern)
    - app/services/file_storage_service.py (existing file storage)
  </read_first>
  <action>
Replace app/blueprints/certificates/__init__.py:
```python
"""Certificates blueprint - Phase 2 implementation."""
from flask import Blueprint

certificates_bp = Blueprint('certificates', __name__, url_prefix='/certificates')

from app.blueprints.certificates import routes
```

Create app/blueprints/certificates/services.py:
```python
"""Certificate business logic services."""
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models.certificate import Certificate
from app.services.file_storage_service import FileStorageService


class CertificateService:
    """Service for certificate CRUD operations."""

    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in CertificateService.ALLOWED_EXTENSIONS

    @staticmethod
    def create_certificate(user_id, title, certificate_type_id, file, dynamic_fields):
        """Create a new certificate with file upload."""
        if not file or not CertificateService.allowed_file(file.filename):
            raise ValueError('Invalid file type')

        original_filename = secure_filename(file.filename)
        file_path = FileStorageService.save_file(file)

        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        file_mime_type = file.content_type

        certificate = Certificate(
            user_id=user_id,
            title=title,
            certificate_type_id=certificate_type_id,
            file_path=file_path,
            original_filename=original_filename,
            file_size=file_size,
            file_mime_type=file_mime_type,
            fields=dynamic_fields
        )
        db.session.add(certificate)
        db.session.commit()
        return certificate

    @staticmethod
    def update_certificate(certificate, title, certificate_type_id, file=None, dynamic_fields=None):
        """Update existing certificate."""
        certificate.title = title
        certificate.certificate_type_id = certificate_type_id

        if file and CertificateService.allowed_file(file.filename):
            FileStorageService.delete_file(certificate.file_path)
            certificate.original_filename = secure_filename(file.filename)
            certificate.file_path = FileStorageService.save_file(file)
            certificate.file_size = file.seek(0, os.SEEK_END) or 0
            certificate.file_mime_type = file.content_type
            file.seek(0)

        if dynamic_fields is not None:
            certificate.fields = dynamic_fields

        certificate.updated_at = datetime.utcnow()
        db.session.commit()
        return certificate

    @staticmethod
    def delete_certificate(certificate):
        """Delete certificate and its file."""
        FileStorageService.delete_file(certificate.file_path)
        db.session.delete(certificate)
        db.session.commit()
```

Replace app/blueprints/certificates/routes.py:
```python
"""Certificate CRUD routes."""
import os
from flask import render_template, redirect, url_for, flash, send_file, abort, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.certificate import Certificate
from app.blueprints.certificates import certificates_bp
from app.blueprints.certificates.forms import CertificateBaseForm, CertificateEditForm, FIELD_SCHEMAS
from app.blueprints.certificates.services import CertificateService
from app.decorators import admin_required


@certificates_bp.route('/')
@login_required
def list():
    """List user's certificates (card layout)."""
    if current_user.is_admin:
        certificates = Certificate.query.order_by(Certificate.created_at.desc()).all()
    else:
        certificates = Certificate.query.filter_by(user_id=current_user.id).order_by(Certificate.created_at.desc()).all()
    return render_template('certificates/list.html', certificates=certificates)


@certificates_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Upload new certificate with dynamic fields (same-page switching)."""
    form = CertificateBaseForm()
    if form.validate_on_submit():
        try:
            import json
            dynamic_fields_json = request.form.get('dynamic_fields_json', '{}')
            dynamic_fields = json.loads(dynamic_fields_json) if dynamic_fields_json else {}

            certificate = CertificateService.create_certificate(
                user_id=current_user.id,
                title=form.title.data,
                certificate_type_id=form.certificate_type_id.data,
                file=form.file.data,
                dynamic_fields=dynamic_fields
            )
            flash('证书上传成功 / Certificate uploaded successfully.', 'success')
            return redirect(url_for('certificates.detail', cert_id=certificate.id))
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash(f'上传失败 / Upload failed: {str(e)}', 'danger')

    return render_template('certificates/upload.html', form=form, FIELD_SCHEMAS=FIELD_SCHEMAS)


@certificates_bp.route('/<int:cert_id>')
@login_required
def detail(cert_id):
    """View certificate detail (edit/delete from here per user decision)."""
    certificate = Certificate.query.get_or_404(cert_id)
    if not current_user.is_admin and certificate.user_id != current_user.id:
        abort(403)
    return render_template('certificates/detail.html', certificate=certificate)


@certificates_bp.route('/<int:cert_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(cert_id):
    """Edit certificate."""
    certificate = Certificate.query.get_or_404(cert_id)
    if not current_user.is_admin and certificate.user_id != current_user.id:
        abort(403)

    form = CertificateEditForm()

    if form.validate_on_submit():
        try:
            import json
            dynamic_fields_json = request.form.get('dynamic_fields_json', '{}')
            dynamic_fields = json.loads(dynamic_fields_json) if dynamic_fields_json else {}

            CertificateService.update_certificate(
                certificate=certificate,
                title=form.title.data,
                certificate_type_id=form.certificate_type_id.data,
                file=form.file.data if form.file.data else None,
                dynamic_fields=dynamic_fields
            )
            flash('证书更新成功 / Certificate updated successfully.', 'success')
            return redirect(url_for('certificates.detail', cert_id=certificate.id))
        except Exception as e:
            flash(f'更新失败 / Update failed: {str(e)}', 'danger')

    if request.method == 'GET':
        form.title.data = certificate.title
        form.certificate_type_id.data = certificate.certificate_type_id

    return render_template('certificates/edit.html', form=form, certificate=certificate, FIELD_SCHEMAS=FIELD_SCHEMAS)


@certificates_bp.route('/<int:cert_id>/delete', methods=['POST'])
@login_required
def delete(cert_id):
    """Delete certificate."""
    certificate = Certificate.query.get_or_404(cert_id)
    if not current_user.is_admin and certificate.user_id != current_user.id:
        abort(403)

    try:
        CertificateService.delete_certificate(certificate)
        flash('证书已删除 / Certificate deleted.', 'success')
    except Exception as e:
        flash(f'删除失败 / Delete failed: {str(e)}', 'danger')

    return redirect(url_for('certificates.list'))


@certificates_bp.route('/<int:cert_id>/file')
@login_required
def file(cert_id):
    """Serve certificate file."""
    certificate = Certificate.query.get_or_404(cert_id)
    if not current_user.is_admin and certificate.user_id != current_user.id:
        abort(403)

    from flask import current_app
    file_full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], certificate.file_path)
    return send_file(file_full_path, mimetype=certificate.file_mime_type)
```
  </action>
  <verify>
    <automated>cd /Users/ice/PycharmProjects/CertMgr && python -c "
from app import create_app
app = create_app('testing')
with app.app_context():
    from app.blueprints.certificates.routes import certificates_bp
    from app.blueprints.certificates.services import CertificateService
    print('Routes loads:', certificates_bp is not None)
    print('Service methods:', [m for m in dir(CertificateService) if not m.startswith('_')])
"</automated>
  </verify>
  <done>
    All CRUD routes: list, upload, detail, edit, delete, file
  </done>
  <acceptance_criteria>
    - File app/blueprints/certificates/routes.py contains: list, upload, detail, edit, delete, file routes
    - File app/blueprints/certificates/services.py contains: CertificateService.create/update/delete_certificate
    - Routes use @login_required decorator
    - Admin can access all, regular users only their own
    - abort(403) if unauthorized
  </acceptance_criteria>
</task>

<task type="auto">
  <name>Task 4: Create certificate templates (list, detail, upload, edit)</name>
  <files>
    - app/blueprints/certificates/templates/list.html
    - app/blueprints/certificates/templates/detail.html
    - app/blueprints/certificates/templates/upload.html
    - app/blueprints/certificates/templates/edit.html
  </files>
  <read_first>
    - app/templates/base.html
  </read_first>
  <action>
Create app/blueprints/certificates/templates/list.html (card layout):
```html
{% extends "base.html" %}

{% block title %}我的证书 - CertMgr{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <h1>我的证书 / My Certificates</h1>
    <a href="{{ url_for('certificates.upload') }}" class="btn btn-primary">
        上传证书 / Upload
    </a>
</div>

{% if certificates %}
<div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
    {% for cert in certificates %}
    <div class="col">
        <div class="card h-100 shadow-sm">
            {% if cert.file_mime_type and 'image' in cert.file_mime_type %}
            <img src="{{ url_for('certificates.file', cert_id=cert.id) }}"
                 class="card-img-top" alt="{{ cert.title }}" style="height: 180px; object-fit: cover;">
            {% else %}
            <div class="card-img-top bg-secondary text-white d-flex align-items-center justify-content-center"
                 style="height: 180px;">
                <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M14 4.5V14a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V2a2 2 0 0 1 2-2h5.5L14 4.5zm-3 0A1.5 1.5 0 0 1 9.5 3V1H4a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V4.5h-2z"/>
                </svg>
            </div>
            {% endif %}
            <div class="card-body">
                <h5 class="card-title text-truncate" title="{{ cert.title }}">{{ cert.title }}</h5>
                <p class="card-text">
                    <span class="badge bg-primary">{{ cert.certificate_type.name if cert.certificate_type else 'Unknown' }}</span>
                </p>
                <p class="card-text">
                    <small class="text-muted">{{ cert.created_at.strftime('%Y-%m-%d') if cert.created_at else 'N/A' }}</small>
                </p>
            </div>
            <div class="card-footer bg-transparent">
                <a href="{{ url_for('certificates.detail', cert_id=cert.id) }}" class="btn btn-sm btn-outline-primary w-100">
                    查看详情 / View Details
                </a>
            </div>
        </div>
    </div>
    {% endfor %}
</div>
{% else %}
<div class="alert alert-info">
    暂无证书 / No certificates yet. <a href="{{ url_for('certificates.upload') }}">上传第一个证书</a>
</div>
{% endif %}
{% endblock %}
```

Create app/blueprints/certificates/templates/detail.html (edit/delete from here):
```html
{% extends "base.html" %}

{% block title %}{{ certificate.title }} - CertMgr{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-4">
        {% if certificate.file_mime_type and 'image' in certificate.file_mime_type %}
        <img src="{{ url_for('certificates.file', cert_id=certificate.id) }}" class="img-fluid rounded" alt="{{ certificate.title }}">
        {% else %}
        <div class="bg-secondary text-white rounded p-5 text-center">
            <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" fill="currentColor" viewBox="0 0 16 16">
                <path d="M14 4.5V14a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V2a2 2 0 0 1 2-2h5.5L14 4.5zm-3 0A1.5 1.5 0 0 1 9.5 3V1H4a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V4.5h-2z"/>
            </svg>
            <div class="mt-2">PDF 文件</div>
        </div>
        {% endif %}
    </div>
    <div class="col-md-8">
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h4 class="mb-0">{{ certificate.title }}</h4>
                <span class="badge bg-primary">{{ certificate.certificate_type.name if certificate.certificate_type else 'Unknown' }}</span>
            </div>
            <div class="card-body">
                <dl class="row">
                    <dt class="col-sm-3">标题:</dt>
                    <dd class="col-sm-9">{{ certificate.title }}</dd>
                    <dt class="col-sm-3">类型:</dt>
                    <dd class="col-sm-9">{{ certificate.certificate_type.name if certificate.certificate_type else 'Unknown' }}</dd>
                    <dt class="col-sm-3">上传时间:</dt>
                    <dd class="col-sm-9">{{ certificate.created_at.strftime('%Y-%m-%d %H:%M') if certificate.created_at else 'N/A' }}</dd>
                </dl>
                {% if certificate.fields %}
                <hr>
                <h5>证书详情</h5>
                <dl class="row">
                    {% for key, value in certificate.fields.items() %}
                    <dt class="col-sm-3">{{ key }}:</dt>
                    <dd class="col-sm-9">{{ value }}</dd>
                    {% endfor %}
                </dl>
                {% endif %}
            </div>
            <div class="card-footer">
                <a href="{{ url_for('certificates.edit', cert_id=certificate.id) }}" class="btn btn-warning">编辑 / Edit</a>
                <form method="POST" action="{{ url_for('certificates.delete', cert_id=certificate.id) }}" class="d-inline"
                      onsubmit="return confirm('确定要删除吗？/ Are you sure?');">
                    <button type="submit" class="btn btn-danger">删除 / Delete</button>
                </form>
                <a href="{{ url_for('certificates.list') }}" class="btn btn-secondary float-end">返回 / Back</a>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

Create app/blueprints/certificates/templates/upload.html (dynamic fields on same page):
```html
{% extends "base.html" %}

{% block title %}上传证书 - CertMgr{% endblock %}

{% block content %}
<h1>上传证书 / Upload Certificate</h1>

<form method="POST" enctype="multipart/form-data" id="certificate-form">
    {{ form.hidden_tag() }}

    <div class="mb-3">
        {{ form.certificate_type_id.label(class="form-label") }}
        {{ form.certificate_type_id(class="form-select", id="certificate_type_id") }}
        {% if form.certificate_type_id.errors %}<span class="text-danger">{{ form.certificate_type_id.errors[0] }}</span>{% endif %}
    </div>

    <div class="mb-3">
        {{ form.title.label(class="form-label") }}
        {{ form.title(class="form-control") }}
        {% if form.title.errors %}<span class="text-danger">{{ form.title.errors[0] }}</span>{% endif %}
    </div>

    <div class="mb-3">
        {{ form.file.label(class="form-label") }}
        {{ form.file(class="form-control", accept=".pdf,.png,.jpg,.jpeg,.gif") }}
        {% if form.file.errors %}<span class="text-danger">{{ form.file.errors[0] }}</span>{% endif %}
        <small class="text-muted">支持 PDF、图片格式</small>
    </div>

    <div id="dynamic-fields-container" class="border rounded p-3 mb-3" style="display: none;">
        <h5>证书详情 / Certificate Details</h5>
        <div id="dynamic-fields-content"></div>
    </div>

    <input type="hidden" name="dynamic_fields_json" id="dynamic_fields_json" value="{}">

    {{ form.submit(class="btn btn-primary") }}
    <a href="{{ url_for('certificates.list') }}" class="btn btn-secondary">取消 / Cancel</a>
</form>
{% endblock %}

{% block extra_js %}
<script>
const FIELD_SCHEMAS = {{ FIELD_SCHEMAS|tojson }};

document.addEventListener('DOMContentLoaded', function() {
    updateDynamicFields();
    document.getElementById('certificate_type_id').addEventListener('change', updateDynamicFields);
});

function updateDynamicFields() {
    const typeSelect = document.getElementById('certificate_type_id');
    const container = document.getElementById('dynamic-fields-container');
    const content = document.getElementById('dynamic-fields-content');
    const hiddenInput = document.getElementById('dynamic_fields_json');

    const selectedTypeName = typeSelect.options[typeSelect.selectedIndex]?.text;
    const schema = FIELD_SCHEMAS[selectedTypeName];

    if (!schema || schema.length === 0) {
        container.style.display = 'none';
        hiddenInput.value = '{}';
        return;
    }

    container.style.display = 'block';
    content.innerHTML = '';

    schema.forEach(field => {
        const div = document.createElement('div');
        div.className = 'mb-3';

        if (field.type === 'select') {
            div.innerHTML = `
                <label class="form-label">${field.label}${field.required ? ' *' : ''}</label>
                <select class="form-select" name="dynamic_${field.name}" id="dynamic_${field.name}" ${field.required ? 'required' : ''}>
                    <option value="">请选择</option>
                    ${(field.options || []).map(opt => `<option value="${opt}">${opt}</option>`).join('')}
                </select>`;
        } else if (field.type === 'text') {
            div.innerHTML = `
                <label class="form-label">${field.label}${field.required ? ' *' : ''}</label>
                <textarea class="form-control" name="dynamic_${field.name}" id="dynamic_${field.name}" rows="3" ${field.required ? 'required' : ''}></textarea>`;
        } else if (field.type === 'date') {
            div.innerHTML = `
                <label class="form-label">${field.label}${field.required ? ' *' : ''}</label>
                <input type="date" class="form-control" name="dynamic_${field.name}" id="dynamic_${field.name}" ${field.required ? 'required' : ''}>`;
        } else {
            div.innerHTML = `
                <label class="form-label">${field.label}${field.required ? ' *' : ''}</label>
                <input type="text" class="form-control" name="dynamic_${field.name}" id="dynamic_${field.name}" ${field.required ? 'required' : ''}>`;
        }
        content.appendChild(div);
    });

    document.getElementById('certificate-form').addEventListener('submit', function() {
        const fields = {};
        schema.forEach(field => {
            const el = document.getElementById('dynamic_' + field.name);
            if (el && el.value) fields[field.name] = el.value;
        });
        hiddenInput.value = JSON.stringify(fields);
    });
}
</script>
{% endblock %}
```

Create app/blueprints/certificates/templates/edit.html (pre-populated dynamic fields):
```html
{% extends "base.html" %}

{% block title %}编辑证书 - CertMgr{% endblock %}

{% block content %}
<h1>编辑证书 / Edit Certificate</h1>

<form method="POST" enctype="multipart/form-data" id="certificate-form">
    {{ form.hidden_tag() }}

    <div class="mb-3">
        {{ form.certificate_type_id.label(class="form-label") }}
        {{ form.certificate_type_id(class="form-select", id="certificate_type_id") }}
    </div>

    <div class="mb-3">
        {{ form.title.label(class="form-label") }}
        {{ form.title(class="form-control") }}
    </div>

    <div class="mb-3">
        <label class="form-label">更换证书文件 / Replace File (可选)</label>
        {{ form.file(class="form-control", accept=".pdf,.png,.jpg,.jpeg,.gif") }}
        <small class="text-muted">当前文件: {{ certificate.original_filename }}</small>
    </div>

    <div id="dynamic-fields-container" class="border rounded p-3 mb-3" style="display: none;">
        <h5>证书详情</h5>
        <div id="dynamic-fields-content"></div>
    </div>

    <input type="hidden" name="dynamic_fields_json" id="dynamic_fields_json" value="{{ certificate.fields|tojson }}">

    {{ form.submit(class="btn btn-primary") }}
    <a href="{{ url_for('certificates.detail', cert_id=certificate.id) }}" class="btn btn-secondary">取消</a>
</form>
{% endblock %}

{% block extra_js %}
<script>
const FIELD_SCHEMAS = {{ FIELD_SCHEMAS|tojson }};
const CURRENT_FIELDS = {{ certificate.fields|tojson }};

document.addEventListener('DOMContentLoaded', function() {
    updateDynamicFields();
    document.getElementById('certificate_type_id').addEventListener('change', updateDynamicFields);
    // Pre-fill current values
    if (CURRENT_FIELDS) {
        Object.keys(CURRENT_FIELDS).forEach(key => {
            const el = document.getElementById('dynamic_' + key);
            if (el) el.value = CURRENT_FIELDS[key];
        });
    }
});

function updateDynamicFields() {
    const typeSelect = document.getElementById('certificate_type_id');
    const container = document.getElementById('dynamic-fields-container');
    const content = document.getElementById('dynamic-fields-content');
    const hiddenInput = document.getElementById('dynamic_fields_json');

    const selectedTypeName = typeSelect.options[typeSelect.selectedIndex]?.text;
    const schema = FIELD_SCHEMAS[selectedTypeName];

    if (!schema || schema.length === 0) {
        container.style.display = 'none';
        return;
    }

    container.style.display = 'block';

    if (content.children.length === 0) {
        schema.forEach(field => {
            const div = document.createElement('div');
            div.className = 'mb-3';

            if (field.type === 'select') {
                div.innerHTML = `
                    <label class="form-label">${field.label}${field.required ? ' *' : ''}</label>
                    <select class="form-select" name="dynamic_${field.name}" id="dynamic_${field.name}">
                        <option value="">请选择</option>
                        ${(field.options || []).map(opt => `<option value="${opt}">${opt}</option>`).join('')}
                    </select>`;
            } else if (field.type === 'text') {
                div.innerHTML = `
                    <label class="form-label">${field.label}${field.required ? ' *' : ''}</label>
                    <textarea class="form-control" name="dynamic_${field.name}" id="dynamic_${field.name}" rows="3"></textarea>`;
            } else if (field.type === 'date') {
                div.innerHTML = `
                    <label class="form-label">${field.label}${field.required ? ' *' : ''}</label>
                    <input type="date" class="form-control" name="dynamic_${field.name}" id="dynamic_${field.name}">`;
            } else {
                div.innerHTML = `
                    <label class="form-label">${field.label}${field.required ? ' *' : ''}</label>
                    <input type="text" class="form-control" name="dynamic_${field.name}" id="dynamic_${field.name}">`;
            }
            content.appendChild(div);
        });
    }

    document.getElementById('certificate-form').addEventListener('submit', function() {
        const fields = {};
        schema.forEach(field => {
            const el = document.getElementById('dynamic_' + field.name);
            if (el && el.value) fields[field.name] = el.value;
        });
        hiddenInput.value = JSON.stringify(fields);
    });
}
</script>
{% endblock %}
```
  </action>
  <verify>
    <automated>cd /Users/ice/PycharmProjects/CertMgr && python -c "
import os
template_dir = 'app/blueprints/certificates/templates'
for f in ['list.html', 'detail.html', 'upload.html', 'edit.html']:
    path = os.path.join(template_dir, f)
    print(f'{f}: exists={os.path.exists(path)}')
"</automated>
  </verify>
  <done>
    Card layout list, detail page with edit/delete, upload with dynamic fields all implemented
  </done>
  <acceptance_criteria>
    - list.html exists with card grid layout (row-cols-*, card, card-img-top)
    - detail.html exists with edit/delete buttons
    - upload.html exists with dynamic fields container (shows/hides based on type)
    - edit.html exists with pre-populated dynamic fields
    - All templates extend base.html
  </acceptance_criteria>
</task>

</tasks>

<verification>
- Certificate model creates tables correctly
- CertificateType seeds 4 types on app startup
- All routes respond with appropriate templates
- Card layout displays in list view
- Dynamic fields show/hide when certificate type changes
</verification>

<success_criteria>
Wave 1 (Plan 02-01) complete when:
- Certificate model with JSONB fields exists
- 4 certificate types seeded
- User can upload certificate with dynamic fields
- User can view card-based certificate list
- User can view detail and edit/delete from there
- Admin can view/edit/delete any certificate
- Dynamic fields switch on same page based on certificate type
</success_criteria>

---

---
phase: 02-core
plan: 02
type: execute
wave: 2
depends_on: ["02-core-01"]
files_modified:
  - app/blueprints/certificates/api.py
  - app/blueprints/certificates/services.py
  - app/blueprints/certificates/templates/list.html
  - app/blueprints/certificates/templates/import.html
  - app/blueprints/admin/routes.py
autonomous: true
requirements:
  - CERT-06
  - CERT-07
  - CERT-08

must_haves:
  truths:
    - "User can search certificates by holder name, type, date range, issuer"
    - "User can filter certificates by multiple conditions on list page top"
    - "Admin can batch import certificates from Excel without template download"
    - "DataTables server-side pagination works correctly"
  artifacts:
    - path: "app/blueprints/certificates/api.py"
      provides: "DataTables server-side JSON API"
      contains: "@certificates_bp.route('/api/data')", "draw", "start", "length", "search"
    - path: "app/blueprints/certificates/services.py"
      provides: "ExcelImportService for auto-parse"
      contains: "class ExcelImportService", "COLUMN_MAPPINGS", "parse_excel"
    - path: "app/blueprints/certificates/templates/list.html"
      provides: "List page with search/filter at top"
      contains: "search input", "filter selects", "DataTables initialization"
  key_links:
    - from: "list.html"
      to: "/certificates/api/data"
      via: "DataTables ajax option"
    - from: "ExcelImportService"
      to: "Certificate"
      via: "db.session.add(certificate)"
---

<objective>
Wave 2: Implement DataTables server-side API with search/filter, and Excel batch import with auto-parse (no template download required). Search/filter UI at top of list page per user decision.
</objective>

<execution_context>
@/Users/ice/PycharmProjects/CertMgr/.planning/phases/02-core/02-RESEARCH.md
@/Users/ice/PycharmProjects/CertMgr/.planning/phases/02-core/02-CONTEXT.md
</execution_context>

<context>
# User Decisions (locked)

| Decision | Value |
|----------|-------|
| Search & Filter Location | On list page top |
| Excel Batch Import | Auto-parse without template - upload file, system automatically identifies columns |

# DataTables Server-Side Pattern (from 02-RESEARCH.md)

```python
@certificates_bp.route('/api/data')
@login_required
def certificates_data():
    draw = int(request.args.get('draw', 1))
    start = int(request.args.get('start', 0))
    length = int(request.args.get('length', 10))
    search_value = request.args.get('search[value]', '')
    order_column = int(request.args.get('order[0][column]', 0))
    order_dir = request.args.get('order[0][dir]', 'asc')

    query = Certificate.query
    if not current_user.is_admin:
        query = query.filter_by(user_id=current_user.id)

    if search_value:
        search_filter = or_(
            Certificate.title.ilike(f'%{search_value}%'),
            Certificate.certificate_type.has(CertificateType.name.ilike(f'%{search_value}%'))
        )
        query = query.filter(search_filter)

    total_count = query.count()
    order_col = ['id', 'title', 'type', 'created_at'][order_column]
    query = query.order_by(getattr(Certificate, order_col).asc() if order_dir == 'asc' else getattr(Certificate, order_col).desc()).offset(start).limit(length)

    return jsonify({
        'draw': draw,
        'recordsTotal': Certificate.query.count(),
        'recordsFiltered': total_count,
        'data': [cert.to_dict() for cert in query.all()]
    })
```

# Excel Auto-Parse Pattern (from 02-RESEARCH.md)

```python
class ExcelImportService:
    COLUMN_MAPPINGS = {
        'title': ['标题', '证书名称', '名称', 'name', 'title'],
        'type': ['类型', '证书类型', 'type'],
        # ... more mappings
    }

    @classmethod
    def parse_excel(cls, file_stream) -> tuple[list[dict], list[str]]:
        wb = load_workbook(file_stream, read_only=True, data_only=True)
        ws = wb.active
        headers = [cell.value for cell in ws[1]]
        column_map = cls._detect_columns(headers)
        # ... parse rows
```

# DataTables HTML Pattern

```html
<table id="certificates-table" class="table table-striped">
    <thead>
        <tr>
            <th>ID</th>
            <th>标题</th>
            <th>类型</th>
            <th>日期</th>
        </tr>
    </thead>
</table>

<script>
$('#certificates-table').DataTable({
    ajax: '/certificates/api/data',
    serverSide: true,
    columns: [
        { data: 'id', name: 'id' },
        { data: 'title', name: 'title' },
        { data: 'type', name: 'type' },
        { data: 'created_at', name: 'created_at' },
    ]
});
</script>
```
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create DataTables server-side API endpoint</name>
  <files>
    - app/blueprints/certificates/api.py
  </files>
  <read_first>
    - app/blueprints/certificates/routes.py (existing routes)
  </read_first>
  <action>
Create app/blueprints/certificates/api.py with DataTables server-side endpoint:

```python
"""DataTables server-side API for certificate list."""
from flask import request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import or_
from app.extensions import db
from app.models.certificate import Certificate, CertificateType
from app.blueprints.certificates import certificates_bp


@certificates_bp.route('/api/data')
@login_required
def certificates_data():
    """DataTables server-side endpoint for certificate list with search and filter.

    Query parameters (DataTables standard):
    - draw: int, incremented on each request
    - start: int, offset for pagination
    - length: int, page size
    - search[value]: str, global search term
    - order[0][column]: int, column index for sorting
    - order[0][dir]: str, 'asc' or 'desc'

    Custom filter parameters:
    - filter_type: int, certificate_type_id
    - filter_date_from: str, date string (YYYY-MM-DD)
    - filter_date_to: str, date string (YYYY-MM-DD)
    """
    draw = int(request.args.get('draw', 1))
    start = int(request.args.get('start', 0))
    length = int(request.args.get('length', 10))
    search_value = request.args.get('search[value]', '')
    order_column = int(request.args.get('order[0][column]', 0))
    order_dir = request.args.get('order[0][dir]', 'asc')

    # Custom filters
    filter_type = request.args.get('filter_type', type=int)
    filter_date_from = request.args.get('filter_date_from')
    filter_date_to = request.args.get('filter_date_to')

    # Column mapping (matches DataTables column index)
    columns = ['id', 'title', 'type', 'created_at']

    # Base query - non-admin sees only own certificates
    query = Certificate.query
    if not current_user.is_admin:
        query = query.filter_by(user_id=current_user.id)

    # Global search across title and type
    if search_value:
        search_filter = or_(
            Certificate.title.ilike(f'%{search_value}%'),
            Certificate.certificate_type.has(CertificateType.name.ilike(f'%{search_value}%'))
        )
        query = query.filter(search_filter)

    # Apply custom filters
    if filter_type:
        query = query.filter(Certificate.certificate_type_id == filter_type)

    if filter_date_from:
        query = query.filter(Certificate.created_at >= filter_date_from)

    if filter_date_to:
        query = query.filter(Certificate.created_at <= filter_date_to)

    # Total count before filtering
    total_count = query.count()

    # Apply sorting and pagination
    order_col = columns[order_column] if order_column < len(columns) else 'created_at'
    order_func = getattr(Certificate, order_col).asc() if order_dir == 'asc' else getattr(Certificate, order_col).desc()
    query = query.order_by(order_func).offset(start).limit(length)

    records = query.all()

    return jsonify({
        'draw': draw,
        'recordsTotal': Certificate.query.count(),
        'recordsFiltered': total_count,
        'data': [cert.to_dict() for cert in records]
    })


@certificates_bp.route('/api/types')
@login_required
def certificate_types():
    """Return all certificate types for filter dropdown."""
    types = CertificateType.query.order_by('name').all()
    return jsonify([
        {'id': t.id, 'name': t.name} for t in types
    ])
```
  </action>
  <verify>
    <automated>cd /Users/ice/PycharmProjects/CertMgr && python -c "
from app import create_app
app = create_app('testing')
with app.app_context():
    from app.blueprints.certificates.api import certificates_data
    print('API endpoint loads:', certificates_data is not None)
"</automated>
  </verify>
  <done>
    DataTables server-side API endpoint exists with search and filter support
  </done>
  <acceptance_criteria>
    - File app/blueprints/certificates/api.py exists
    - certificates_data endpoint accepts: draw, start, length, search[value], order[0][column], order[0][dir]
    - Returns JSON with: draw, recordsTotal, recordsFiltered, data
    - Supports filter_type, filter_date_from, filter_date_to parameters
    - certificate_types endpoint returns list of {id, name}
  </acceptance_criteria>
</task>

<task type="auto">
  <name>Task 2: Add ExcelImportService to services.py</name>
  <files>
    - app/blueprints/certificates/services.py
  </files>
  <read_first>
    - app/blueprints/certificates/services.py (existing)
  </read_first>
  <action>
Update app/blueprints/certificates/services.py to add ExcelImportService:

Add these imports at the top:
```python
from openpyxl import load_workbook
from app.models.certificate import CertificateType
```

Add ExcelImportService class to the file:

```python
class ExcelImportService:
    """Service for auto-parsing Excel files for batch certificate import.

    No template required - system automatically detects column headers.
    """

    # Column name mappings (Excel header -> Certificate field)
    COLUMN_MAPPINGS = {
        'title': ['标题', '证书名称', '名称', 'name', 'title'],
        'type': ['类型', '证书类型', 'type', 'certificate_type'],
        'competition_name': ['比赛名称', '比赛', 'competition'],
        'award_level': ['奖项', '获奖等级', 'level', 'award_level', '奖级'],
        'award_date': ['获奖日期', '获奖时间', 'award_date', '获奖日期'],
        'organizer': ['主办单位', '组织单位', 'organizer', '主办方'],
        'certificate_number': ['证书编号', '编号', 'number', 'certificate_number', '证书号'],
        'honor_title': ['荣誉名称', '荣誉', 'honor', '荣誉名称'],
        'grant_date': ['授予日期', '授予时间', 'grant_date'],
        'grantor': ['授予单位', 'grantor', '授予机构'],
        'reason': ['获得原因', '原因', 'reason'],
        'certificate_name': ['证书名称', '证书名', 'certificate_name'],
        'issue_date': ['发证日期', '颁发日期', 'issue_date'],
        'expiry_date': ['有效期', '有效期至', 'expiry_date', '过期日期'],
        'issuing_authority': ['发证机构', '颁发机构', 'issuer', 'issuing_authority', '发证单位'],
        'skill_name': ['职业技能', 'skill', 'skill_name', '职业名称'],
        'skill_level': ['等级', 'skill_level', '级别', '职业技能等级'],
    }

    @classmethod
    def parse_excel(cls, file_stream) -> tuple[list[dict], list[str]]:
        """Parse Excel file and return list of certificate records.

        Returns:
            Tuple of (records, errors)
        """
        wb = load_workbook(file_stream, read_only=True, data_only=True)
        ws = wb.active

        # Read headers from first row
        headers = [cell.value for cell in ws[1]]
        if not headers or not any(headers):
            wb.close()
            return [], ['Excel 文件为空或第一行没有列标题 / Excel file is empty or first row has no column headers']

        # Auto-detect column mapping
        column_map = cls._detect_columns(headers)

        if not column_map.get('title'):
            wb.close()
            return [], ['未找到标题列（标题、名称、证书名称 等）/ Title column not found (title, name, certificate name, etc.)']

        # Parse data rows
        records = []
        errors = []

        for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            if not any(row):
                continue  # Skip empty rows

            try:
                record = cls._parse_row(row, headers, column_map)
                if record:
                    records.append(record)
            except Exception as e:
                errors.append(f'第 {row_idx} 行解析错误 / Row {row_idx} parse error: {str(e)}')

        wb.close()
        return records, errors

    @classmethod
    def _detect_columns(cls, headers: list) -> dict:
        """Auto-detect which columns map to which certificate fields."""
        column_map = {}

        for field, aliases in cls.COLUMN_MAPPINGS.items():
            for idx, header in enumerate(headers):
                if header and str(header).strip().lower() in [a.lower() for a in aliases]:
                    column_map[field] = idx
                    break

        return column_map

    @classmethod
    def _parse_row(cls, row: tuple, headers: list, column_map: dict) -> dict | None:
        """Parse a single row into a certificate record."""
        # Get title
        title_idx = column_map.get('title')
        if title_idx is None or not row[title_idx]:
            return None

        title = str(row[title_idx]).strip()

        # Determine certificate type
        type_idx = column_map.get('type')
        cert_type = None
        if type_idx and row[type_idx]:
            type_name = str(row[type_idx]).strip()
            cert_type = CertificateType.query.filter(
                CertificateType.name.like(f'%{type_name}%')
            ).first()

        # If type not specified, default to first type
        if not cert_type:
            cert_type = CertificateType.query.first()

        # Build dynamic fields from mapped columns
        fields = {}
        for field_name, idx in column_map.items():
            if field_name not in ('title', 'type') and idx < len(row):
                value = row[idx]
                if value is not None:
                    # Handle date objects from Excel
                    if hasattr(value, 'strftime'):
                        value = value.strftime('%Y-%m-%d')
                    elif isinstance(value, (int, float)):
                        value = str(value)
                    else:
                        value = str(value).strip()
                    fields[field_name] = value

        return {
            'title': title,
            'certificate_type_id': cert_type.id if cert_type else None,
            'fields': fields,
        }

    @classmethod
    def import_batch(cls, records: list[dict], user_id: int, overwrite: bool = False) -> tuple[int, list[str]]:
        """Import batch of certificate records.

        Args:
            records: List of parsed certificate records
            user_id: User ID to associate certificates with
            overwrite: If True, update existing certificates by title+user

        Returns:
            Tuple of (success_count, errors)
        """
        success_count = 0
        errors = []

        for record in records:
            try:
                if overwrite:
                    existing = Certificate.query.filter_by(
                        user_id=user_id,
                        title=record['title']
                    ).first()
                    if existing:
                        existing.fields = record['fields']
                        existing.certificate_type_id = record['certificate_type_id']
                        db.session.commit()
                        success_count += 1
                        continue

                certificate = Certificate(
                    user_id=user_id,
                    title=record['title'],
                    certificate_type_id=record['certificate_type_id'],
                    file_path='',  # No file for imported certificates
                    fields=record['fields']
                )
                db.session.add(certificate)
                db.session.commit()
                success_count += 1
            except Exception as e:
                errors.append(f"导入 '{record.get('title', 'Unknown')}' 失败 / Failed to import '{record.get('title', 'Unknown')}': {str(e)}")

        return success_count, errors
```
  </action>
  <verify>
    <automated>cd /Users/ice/PycharmProjects/CertMgr && python -c "
from app import create_app
app = create_app()
with app.app_context():
    from app.blueprints.certificates.services import ExcelImportService
    print('ExcelImportService methods:', [m for m in dir(ExcelImportService) if not m.startswith('_')])
    print('COLUMN_MAPPINGS keys:', list(ExcelImportService.COLUMN_MAPPINGS.keys())[:5])
"</automated>
  </verify>
  <done>
    ExcelImportService with auto-parse exists
  </done>
  <acceptance_criteria>
    - File app/blueprints/certificates/services.py contains: ExcelImportService class
    - COLUMN_MAPPINGS contains: title, type, and dynamic field mappings
    - parse_excel method returns tuple of (records, errors)
    - import_batch method creates Certificate records
  </acceptance_criteria>
</task>

<task type="auto">
  <name>Task 3: Update list.html with DataTables and search/filter UI</name>
  <files>
    - app/blueprints/certificates/templates/list.html
  </files>
  <read_first>
    - app/blueprints/certificates/templates/list.html (existing)
  </read_first>
  <action>
Replace app/blueprints/certificates/templates/list.html with DataTables + search/filter at top:

```html
{% extends "base.html" %}

{% block title %}我的证书 - CertMgr{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="https://cdn.datatables.net/1.11.5/css/dataTables.bootstrap5.min.css">
{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <h1>我的证书 / My Certificates</h1>
    <div>
        <a href="{{ url_for('certificates.upload') }}" class="btn btn-primary">
            上传证书 / Upload
        </a>
        {% if current_user.is_admin %}
        <a href="{{ url_for('certificates.import_batch') }}" class="btn btn-success">
            批量导入 / Batch Import
        </a>
        {% endif %}
    </div>
</div>

{# Search and Filter Bar at top per user decision #}
<div class="card mb-4">
    <div class="card-body">
        <div class="row g-3">
            <div class="col-md-4">
                <label class="form-label">搜索 / Search</label>
                <input type="text" id="search-input" class="form-control" placeholder="搜索标题、类型... / Search title, type...">
            </div>
            <div class="col-md-3">
                <label class="form-label">证书类型 / Certificate Type</label>
                <select id="filter-type" class="form-select">
                    <option value="">全部 / All</option>
                </select>
            </div>
            <div class="col-md-2">
                <label class="form-label">从 / From</label>
                <input type="date" id="filter-date-from" class="form-control">
            </div>
            <div class="col-md-2">
                <label class="form-label">到 / To</label>
                <input type="date" id="filter-date-to" class="form-control">
            </div>
            <div class="col-md-1 d-flex align-items-end">
                <button type="button" id="filter-btn" class="btn btn-secondary w-100">筛选 / Filter</button>
            </div>
        </div>
    </div>
</div>

{# DataTables #}
<div class="table-responsive">
    <table id="certificates-table" class="table table-striped" style="width:100%">
        <thead>
            <tr>
                <th>ID</th>
                <th>标题 / Title</th>
                <th>类型 / Type</th>
                <th>上传时间 / Date</th>
                <th>操作 / Actions</th>
            </tr>
        </thead>
        <tbody>
        </tbody>
    </table>
</div>
{% endblock %}

{% block extra_js %}
<script src="https://cdn.datatables.net/1.11.5/js/jquery.dataTables.min.js"></script>
<script src="https://cdn.datatables.net/1.11.5/js/dataTables.bootstrap5.min.js"></script>
<script>
$(document).ready(function() {
    // Load certificate types for filter
    fetch('/certificates/api/types')
        .then(r => r.json())
        .then(data => {
            data.forEach(type => {
                $('#filter-type').append(`<option value="${type.id}">${type.name}</option>`);
            });
        });

    // Initialize DataTables
    var table = $('#certificates-table').DataTable({
        ajax: {
            url: '/certificates/api/data',
            type: 'GET',
            data: function(d) {
                d.search = $('#search-input').val();
                d.filter_type = $('#filter-type').val();
                d.filter_date_from = $('#filter-date-from').val();
                d.filter_date_to = $('#filter-date-to').val();
            }
        },
        serverSide: true,
        processing: true,
        columns: [
            { data: 'id', name: 'id' },
            { data: 'title', name: 'title' },
            { data: 'type', name: 'type' },
            { data: 'created_at', name: 'created_at' },
            {
                data: null,
                orderable: false,
                searchable: false,
                render: function(data, type, row) {
                    return `<a href="/certificates/${row.id}" class="btn btn-sm btn-outline-primary">详情</a>`;
                }
            }
        ],
        order: [[3, 'desc']],
        language: {
            url: '//cdn.datatables.net/plug-ins/1.11.5/i18n/zh.json'
        },
        drawCallback: function() {
            // Re-attach event handlers if needed
        }
    });

    // Filter button click
    $('#filter-btn').on('click', function() {
        table.draw();
    });

    // Search on Enter
    $('#search-input').on('keypress', function(e) {
        if (e.which === 13) {
            table.draw();
        }
    });
});
</script>
{% endblock %}
```
  </action>
  <verify>
    <automated>grep -l "DataTable\|serverSide" app/blueprints/certificates/templates/list.html && echo "DataTables found"</automated>
  </verify>
  <done>
    List page updated with DataTables server-side pagination and search/filter at top
  </done>
  <acceptance_criteria>
    - File list.html contains: DataTables initialization with serverSide: true
    - Contains search input, filter selects for type and date range
    - Filter button triggers table redraw
    - Data loaded from /certificates/api/data endpoint
  </acceptance_criteria>
</task>

<task type="auto">
  <name>Task 4: Create batch import page and route for admin</name>
  <files>
    - app/blueprints/certificates/routes.py
    - app/blueprints/certificates/templates/import.html
  </files>
  <read_first>
    - app/blueprints/certificates/routes.py (existing)
  </read_first>
  <action>
Add import route to app/blueprints/certificates/routes.py:

```python
@certificates_bp.route('/import', methods=['GET', 'POST'])
@login_required
@admin_required
def import_batch():
    """Batch import certificates from Excel file (admin only).

    Auto-parse without template per user decision.
    """
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('请选择文件 / Please select a file', 'danger')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('请选择文件 / Please select a file', 'danger')
            return redirect(request.url)

        if not file.filename.endswith(('.xlsx', '.xls')):
            flash('请上传 Excel 文件 / Please upload an Excel file', 'danger')
            return redirect(request.url)

        try:
            # Parse Excel
            records, parse_errors = ExcelImportService.parse_excel(file)

            if parse_errors:
                for error in parse_errors:
                    flash(error, 'warning')

            if not records:
                flash('未能从文件中解析出证书记录 / No certificate records parsed from file', 'warning')
                return redirect(request.url)

            # Import records
            success_count, import_errors = ExcelImportService.import_batch(records, user_id=1)  # Admin imports for user 1 as placeholder

            flash(f'成功导入 {success_count} 个证书 / Successfully imported {success_count} certificates', 'success')

            if import_errors:
                for error in import_errors:
                    flash(error, 'danger')

            return redirect(url_for('certificates.list'))

        except Exception as e:
            flash(f'导入失败 / Import failed: {str(e)}', 'danger')
            return redirect(request.url)

    return render_template('certificates/import.html')
```

Note: Update the imports at top of routes.py to include ExcelImportService.

Create app/blueprints/certificates/templates/import.html:

```html
{% extends "base.html" %}

{% block title %}批量导入 - CertMgr{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-8 offset-md-2">
        <h1>批量导入证书 / Batch Import Certificates</h1>

        <div class="card mb-4">
            <div class="card-header">
                说明 / Instructions
            </div>
            <div class="card-body">
                <p>上传 Excel 文件，系统将自动识别列标题并导入证书记录。</p>
                <p>Upload an Excel file and the system will automatically detect column headers to import certificate records.</p>

                <h5>支持的列 / Supported Columns:</h5>
                <ul>
                    <li><strong>标题 / Title</strong> (必需 / Required): 标题、名称、证书名称、name、title</li>
                    <li><strong>类型 / Type</strong> (可选 / Optional): 类型、证书类型、type</li>
                    <li><strong>比赛名称 / Competition Name</strong>: 比赛名称、比赛、competition</li>
                    <li><strong>获奖等级 / Award Level</strong>: 奖项、获奖等级、level</li>
                    <li><strong>获奖日期 / Award Date</strong>: 获奖日期、获奖时间</li>
                    <li><strong>主办单位 / Organizer</strong>: 主办单位、组织单位</li>
                    <li><strong>证书编号 / Certificate Number</strong>: 证书编号、编号</li>
                    <li>... 以及更多 / and more</li>
                </ul>

                <div class="alert alert-info">
                    <strong>提示:</strong> 第一行必须是列标题，数据从第二行开始。
                    <br><strong>Note:</strong> First row must be column headers, data starts from second row.
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                上传文件 / Upload File
            </div>
            <div class="card-body">
                <form method="POST" enctype="multipart/form-data">
                    <div class="mb-3">
                        <label class="form-label">选择 Excel 文件 / Select Excel File</label>
                        <input type="file" name="file" class="form-control" accept=".xlsx,.xls" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">导入到用户 / Import to User</label>
                        <select name="user_id" class="form-select">
                            {% for user in users %}
                            <option value="{{ user.id }}">{{ user.email }}</option>
                            {% endfor %}
                        </select>
                        <small class="text-muted">选择证书将属于的用户账户 / Select which user account the certificates will belong to</small>
                    </div>
                    <button type="submit" class="btn btn-primary">导入 / Import</button>
                    <a href="{{ url_for('certificates.list') }}" class="btn btn-secondary">取消 / Cancel</a>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

Update the import_batch route to also load users list for the dropdown:

```python
from app.models.user import User

@certificates_bp.route('/import', methods=['GET', 'POST'])
@login_required
@admin_required
def import_batch():
    if request.method == 'GET':
        users = User.query.order_by(User.email).all()
        return render_template('certificates/import.html', users=users)

    # ... rest of POST handling
```
  </action>
  <verify>
    <automated>grep -l "import_batch\|ExcelImportService" app/blueprints/certificates/routes.py && echo "Import route found"</automated>
  </verify>
  <done>
    Batch import page and route exist for admin
  </done>
  <acceptance_criteria>
    - File app/blueprints/certificates/routes.py contains: @certificates_bp.route('/import')
    - File app/blueprints/certificates/templates/import.html exists
    - Route uses @admin_required decorator
    - Parses Excel and uses ExcelImportService
  </acceptance_criteria>
</task>

</tasks>

<verification>
- DataTables server-side API responds to search/filter requests
- Excel import auto-detects columns
- List page search/filter works
- Batch import creates Certificate records
</verification>

<success_criteria>
Wave 2 (Plan 02-02) complete when:
- DataTables server-side pagination works
- Search by title/type works
- Filter by type, date range works
- Excel batch import with auto-parse works
- Admin can batch import certificates
</success_criteria>

---

---
phase: 02-core
plan: 03
type: execute
wave: 3
depends_on: ["02-core-01"]
files_modified:
  - app/blueprints/statistics/__init__.py
  - app/blueprints/statistics/routes.py
  - app/blueprints/statistics/templates/dashboard.html
  - app/__init__.py
autonomous: true
requirements:
  - CERT-09

must_haves:
  truths:
    - "Admin can view statistics dashboard with certificate counts by type"
    - "Admin can view time trend charts showing certificate creation over time"
    - "Statistics dashboard displays department/unit distribution"
  artifacts:
    - path: "app/blueprints/statistics/routes.py"
      provides: "Statistics API endpoints for Chart.js"
      contains: "@statistics_bp.route('/api/chart/by_type')", "@statistics_bp.route('/api/chart/monthly_trend')"
    - path: "app/blueprints/statistics/templates/dashboard.html"
      provides: "Statistics dashboard with charts"
      contains: "Chart.js canvas", "typeChart", "trendChart"
  key_links:
    - from: "dashboard.html"
      to: "/statistics/api/chart/by_type"
      via: "fetch() for chart data"
---

<objective>
Wave 3: Implement statistics dashboard with Chart.js. Show certificate counts by type, time trends, and distribution. Admin only access.
</objective>

<execution_context>
@/Users/ice/PycharmProjects/CertMgr/.planning/phases/02-core/02-RESEARCH.md
@/Users/ice/PycharmProjects/CertMgr/.planning/phases/02-core/02-CONTEXT.md
</execution_context>

<context>
# User Decisions (locked)

| Decision | Value |
|----------|-------|
| Statistics Dashboard | Detailed statistics - time trend charts, department/unit distribution, type breakdown |

# Chart.js Statistics Pattern (from 02-RESEARCH.md)

```python
@statistics_bp.route('/api/chart/<chart_type>')
@login_required
def chart_data(chart_type):
    if chart_type == 'by_type':
        data = db.session.query(
            CertificateType.name,
            func.count(Certificate.id)
        ).join(Certificate).group_by(CertificateType.name).all()
        return jsonify({
            'labels': [row[0] for row in data],
            'values': [row[1] for row in data]
        })
    elif chart_type == 'monthly_trend':
        # Last 12 months data
        ...
```

# Dashboard HTML Pattern

```html
<canvas id="typeChart"></canvas>
<script>
fetch('/statistics/api/chart/by_type')
    .then(r => r.json())
    .then(data => {
        new Chart(document.getElementById('typeChart'), {
            type: 'bar',
            data: { labels: data.labels, datasets: [{ label: '证书数量', data: data.values }] }
        });
    });
</script>
```
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create statistics blueprint</name>
  <files>
    - app/blueprints/statistics/__init__.py
    - app/blueprints/statistics/routes.py
  </files>
  <read_first>
    - app/blueprints/admin/__init__.py (blueprint pattern)
  </read_first>
  <action>
Create app/blueprints/statistics/__init__.py:
```python
"""Statistics blueprint for certificate analytics."""
from flask import Blueprint

statistics_bp = Blueprint('statistics', __name__, url_prefix='/statistics')

from app.blueprints.statistics import routes
```

Create app/blueprints/statistics/routes.py:
```python
"""Statistics routes for certificate analytics."""
from flask import render_template, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from app.extensions import db
from app.models.certificate import Certificate, CertificateType
from app.blueprints.statistics import statistics_bp
from app.decorators import admin_required


@statistics_bp.route('/')
@login_required
@admin_required
def dashboard():
    """Statistics dashboard page (admin only)."""
    return render_template('statistics/dashboard.html')


@statistics_bp.route('/api/chart/<chart_type>')
@login_required
@admin_required
def chart_data(chart_type):
    """Return JSON data for charts.

    Args:
        chart_type: 'by_type', 'monthly_trend', 'by_user', 'recent'
    """
    now = datetime.utcnow()

    if chart_type == 'by_type':
        # Bar chart: certificate count by type
        data = db.session.query(
            CertificateType.name,
            func.count(Certificate.id)
        ).join(Certificate).group_by(CertificateType.name).all()

        return jsonify({
            'labels': [row[0] for row in data],
            'values': [row[1] for row in data]
        })

    elif chart_type == 'monthly_trend':
        # Line chart: certificates per month (last 12 months)
        start_date = now - timedelta(days=365)

        # Build complete date range
        months = []
        current = start_date
        while current <= now:
            months.append((current.year, current.month))
            # Move to next month
            if current.month == 12:
                current = datetime(current.year + 1, 1, 1)
            else:
                current = datetime(current.year, current.month + 1, 1)

        # Query actual data
        data = db.session.query(
            extract('year', Certificate.created_at),
            extract('month', Certificate.created_at),
            func.count(Certificate.id)
        ).filter(
            Certificate.created_at >= start_date
        ).group_by(
            extract('year', Certificate.created_at),
            extract('month', Certificate.created_at)
        ).order_by(
            extract('year', Certificate.created_at),
            extract('month', Certificate.created_at)
        ).all()

        # Create lookup dict
        data_dict = {(int(row[0]), int(row[1])): row[2] for row in data}

        # Fill in missing months with 0
        labels = [f'{y}-{m:02d}' for y, m in months]
        values = [data_dict.get((y, m), 0) for y, m in months]

        return jsonify({'labels': labels, 'values': values})

    elif chart_type == 'by_user':
        # Pie chart: top 10 users by certificate count
        from app.models.user import User
        data = db.session.query(
            User.email,
            func.count(Certificate.id)
        ).join(Certificate).group_by(User.id, User.email).order_by(
            func.count(Certificate.id).desc()
        ).limit(10).all()

        return jsonify({
            'labels': [row[0] for row in data],
            'values': [row[1] for row in data]
        })

    elif chart_type == 'recent':
        # Recent certificates (last 10)
        certs = Certificate.query.order_by(Certificate.created_at.desc()).limit(10).all()

        return jsonify({
            'data': [
                {
                    'id': c.id,
                    'title': c.title,
                    'type': c.certificate_type.name if c.certificate_type else 'Unknown',
                    'user': c.owner.email if c.owner else 'Unknown',
                    'date': c.created_at.strftime('%Y-%m-%d') if c.created_at else ''
                }
                for c in certs
            ]
        })

    return jsonify({'error': 'Unknown chart type'}), 400


@statistics_bp.route('/api/summary')
@login_required
@admin_required
def summary():
    """Return summary statistics."""
    total = Certificate.query.count()
    by_type = db.session.query(
        CertificateType.name,
        func.count(Certificate.id)
    ).join(Certificate).group_by(CertificateType.name).all()

    return jsonify({
        'total': total,
        'by_type': [{'name': row[0], 'count': row[1]} for row in by_type],
        'recent_30_days': Certificate.query.filter(
            Certificate.created_at >= datetime.utcnow() - timedelta(days=30)
        ).count()
    })
```

Update app/__init__.py to register the statistics blueprint:
```python
from app.blueprints.statistics import statistics_bp
app.register_blueprint(statistics_bp)
```
  </action>
  <verify>
    <automated>cd /Users/ice/PycharmProjects/CertMgr && python -c "
from app import create_app
app = create_app('testing')
with app.app_context():
    from app.blueprints.statistics.routes import statistics_bp, chart_data
    print('Statistics blueprint loads:', statistics_bp is not None)
    print('Chart data function:', chart_data is not None)
"</automated>
  </verify>
  <done>
    Statistics blueprint with Chart.js API endpoints exists
  </done>
  <acceptance_criteria>
    - File app/blueprints/statistics/__init__.py exists
    - File app/blueprints/statistics/routes.py exists
    - Routes: dashboard, chart_data (by_type, monthly_trend, by_user, recent), summary
    - All routes use @login_required and @admin_required decorators
  </acceptance_criteria>
</task>

<task type="auto">
  <name>Task 2: Create statistics dashboard template with Chart.js</name>
  <files>
    - app/blueprints/statistics/templates/dashboard.html
  </files>
  <read_first>
    - app/templates/base.html
  </read_first>
  <action>
Create app/blueprints/statistics/templates/dashboard.html:

```html
{% extends "base.html" %}

{% block title %}统计面板 - CertMgr{% endblock %}

{% block extra_css %}
<style>
.stat-card {
    border-left: 4px solid;
}
.stat-card.primary { border-color: #0d6efd; }
.stat-card.success { border-color: #198754; }
.stat-card.warning { border-color: #ffc107; }
.stat-card.info { border-color: #0dcaf0; }
</style>
{% endblock %}

{% block content %}
<h1 class="mb-4">统计面板 / Statistics Dashboard</h1>

{# Summary Cards #}
<div class="row mb-4">
    <div class="col-md-4">
        <div class="card stat-card primary">
            <div class="card-body">
                <h5 class="card-title">证书总数 / Total Certificates</h5>
                <h2 id="total-count">-</h2>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card stat-card success">
            <div class="card-body">
                <h5 class="card-title">本月新增 / Added This Month</h5>
                <h2 id="recent-count">-</h2>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card stat-card info">
            <div class="card-body">
                <h5 class="card-title">证书类型 / Certificate Types</h5>
                <h2 id="type-count">-</h2>
            </div>
        </div>
    </div>
</div>

{# Charts Row 1 #}
<div class="row mb-4">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                证书类型分布 / Certificates by Type
            </div>
            <div class="card-body">
                <canvas id="typeChart"></canvas>
            </div>
        </div>
    </div>
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                月度趋势 / Monthly Trend (Last 12 Months)
            </div>
            <div class="card-body">
                <canvas id="trendChart"></canvas>
            </div>
        </div>
    </div>
</div>

{# Charts Row 2 #}
<div class="row mb-4">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                用户分布 / Certificates by User (Top 10)
            </div>
            <div class="card-body">
                <canvas id="userChart"></canvas>
            </div>
        </div>
    </div>
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                最新证书 / Recent Certificates
            </div>
            <div class="card-body">
                <table class="table table-sm">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>标题</th>
                            <th>类型</th>
                            <th>用户</th>
                            <th>日期</th>
                        </tr>
                    </thead>
                    <tbody id="recent-table">
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Load summary data
    fetch('/statistics/api/summary')
        .then(r => r.json())
        .then(data => {
            document.getElementById('total-count').textContent = data.total;
            document.getElementById('recent-count').textContent = data.recent_30_days;
            document.getElementById('type-count').textContent = data.by_type.length;
        });

    // Chart.js defaults
    Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
    Chart.defaults.color = '#666';

    // Type distribution chart (bar)
    fetch('/statistics/api/chart/by_type')
        .then(r => r.json())
        .then(data => {
            const ctx = document.getElementById('typeChart').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: '证书数量',
                        data: data.values,
                        backgroundColor: [
                            'rgba(54, 162, 235, 0.5)',
                            'rgba(255, 99, 132, 0.5)',
                            'rgba(255, 206, 86, 0.5)',
                            'rgba(75, 192, 192, 0.5)'
                        ],
                        borderColor: [
                            'rgba(54, 162, 235, 1)',
                            'rgba(255, 99, 132, 1)',
                            'rgba(255, 206, 86, 1)',
                            'rgba(75, 192, 192, 1)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { display: false } },
                    scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } }
                }
            });
        });

    // Monthly trend chart (line)
    fetch('/statistics/api/chart/monthly_trend')
        .then(r => r.json())
        .then(data => {
            const ctx = document.getElementById('trendChart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: '证书数量',
                        data: data.values,
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        tension: 0.1,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { display: false } },
                    scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } }
                }
            });
        });

    // User distribution chart (pie/doughnut)
    fetch('/statistics/api/chart/by_user')
        .then(r => r.json())
        .then(data => {
            const ctx = document.getElementById('userChart').getContext('2d');
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.values,
                        backgroundColor: [
                            'rgba(54, 162, 235, 0.5)',
                            'rgba(255, 99, 132, 0.5)',
                            'rgba(255, 206, 86, 0.5)',
                            'rgba(75, 192, 192, 0.5)',
                            'rgba(153, 102, 255, 0.5)',
                            'rgba(255, 159, 64, 0.5)',
                            'rgba(199, 199, 199, 0.5)',
                            'rgba(83, 102, 255, 0.5)',
                            'rgba(78, 205, 196, 0.5)',
                            'rgba(255, 99, 132, 0.5)'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: 'right' }
                    }
                }
            });
        });

    // Recent certificates table
    fetch('/statistics/api/chart/recent')
        .then(r => r.json())
        .then(data => {
            const tbody = document.getElementById('recent-table');
            tbody.innerHTML = '';
            data.data.forEach(cert => {
                tbody.innerHTML += `
                    <tr>
                        <td>${cert.id}</td>
                        <td>${cert.title}</td>
                        <td><span class="badge bg-primary">${cert.type}</span></td>
                        <td>${cert.user}</td>
                        <td>${cert.date}</td>
                    </tr>
                `;
            });
        });
});
</script>
{% endblock %}
```

Update navigation in base.html to add statistics link for admin. Add after the admin user management link:

```html
{% if current_user.is_admin %}
<li class="nav-item">
    <a class="nav-link" href="{{ url_for('statistics.dashboard') }}">统计 / Statistics</a>
</li>
{% endif %}
```
  </action>
  <verify>
    <automated>cd /Users/ice/PycharmProjects/CertMgr && python -c "
import os
path = 'app/blueprints/statistics/templates/dashboard.html'
print(f'dashboard.html exists: {os.path.exists(path)}')
"</automated>
  </verify>
  <done>
    Statistics dashboard with Chart.js charts exists
  </done>
  <acceptance_criteria>
    - File app/blueprints/statistics/templates/dashboard.html exists
    - Contains: typeChart (bar), trendChart (line), userChart (doughnut)
    - Contains summary cards (total, recent, type count)
    - Contains recent certificates table
    - Chart.js loaded from CDN
  </acceptance_criteria>
</task>

</tasks>

<verification>
- Statistics blueprint registered in app
- Dashboard accessible for admin users
- Charts render with data from API
- Navigation link visible for admin users
</verification>

<success_criteria>
Wave 3 (Plan 02-03) complete when:
- Statistics dashboard at /statistics/
- Certificate counts by type chart
- Monthly trend line chart
- User distribution doughnut chart
- Recent certificates table
- Admin only access
- Navigation link visible for admin
</success_criteria>

<output>
After completion, create `.planning/phases/02-core/02-01-SUMMARY.md`, `.planning/phases/02-core/02-02-SUMMARY.md`, and `.planning/phases/02-core/02-03-SUMMARY.md`
</output>
