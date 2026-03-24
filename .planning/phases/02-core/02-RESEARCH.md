# Phase 2: Core — Research / 第二阶段：核心功能 - 研究

**研究日期 / Researched:** 2026-03-24
**Domain:** Certificate CRUD, dynamic fields, search/filter, batch import, statistics
**Confidence:** HIGH (based on verified PyPI versions, Flask/SQLAlchemy official docs, and established patterns)

---

## User Constraints (from CONTEXT.md) / 用户约束（来自 CONTEXT.md）

### Locked Decisions / 锁定决策

| Decision | Value |
|----------|-------|
| Certificate List Layout | Card layout with thumbnail preview, title, type, date |
| Dynamic Fields Switching | Single page dynamic switching — same form/page, fields change based on selected certificate type |
| Certificate Types | 比赛获奖证书, 荣誉证书, 资格证, 职业技能等级证书 |
| Search & Filter Location | On list page top |
| Statistics Dashboard | Detailed statistics — time trend charts, department/unit distribution, type breakdown |
| Excel Batch Import | Auto-parse without template — upload file, system automatically identifies columns |
| Certificate Edit/Delete | Detail page operation — open certificate detail page first, then edit/delete |

### Claude's Discretion / Claude的自主范围

- Certificate model field structure (within JSONB constraint)
- DataTables configuration details
- Chart.js chart types and configuration
- Excel column auto-detection algorithm
- Form validation strategy

### Deferred Ideas (OUT OF SCOPE) / 延期想法（超出范围）

None — all Phase 2 scope addressed.

---

## Phase Requirements / 阶段需求

| ID | Description | Research Support |
|----|-------------|------------------|
| CERT-01 | User can upload electronic certificate file (image/PDF) | Flask file upload pattern, FileStorageService already implemented in Phase 1 |
| CERT-02 | User can capture and upload photo of paper certificate | Mobile-friendly file upload (same endpoint as CERT-01) |
| CERT-04 | Certificate records support dynamic fields per certificate type | JSONB column with certificate_type_id, form fields switch based on type selection |
| CERT-05 | Admin can manually add/edit/delete any certificate | Certificate CRUD routes with admin ownership bypass |
| CERT-06 | Admin can batch import certificates from Excel file | openpyxl column auto-detection pattern |
| CERT-07 | User can search certificates by name, type, date, issuer | DataTables server-side search with SQL LIKE / JSONB contains |
| CERT-08 | User can filter certificates by multiple conditions | DataTables server-side filter with column-specific search |
| CERT-09 | System displays statistics: certificate counts by type, trends over time | Chart.js with Flask JSON endpoint |

---

## Summary / 摘要

Phase 2 implements full certificate management with dynamic fields, search/filter, batch import, and statistics. The core challenge is the **dynamic field system** — different certificate types (比赛获奖证书, 荣誉证书, 资格证, 职业技能等级证书) require different data structures. The solution uses **JSONB columns** to store flexible field data while maintaining a fixed schema for core fields (id, user_id, type, file_path, created_at).

Key technical decisions:
1. **JSONB for dynamic fields** — Certificate model has `fields` JSONB column, form switches field set based on `certificate_type_id`
2. **DataTables server-side** — Large datasets (~1000 users x multiple certificates) require server-side pagination
3. **openpyxl for Excel parsing** — No template download; system auto-detects column headers
4. **Chart.js for statistics** — Lightweight, Bootstrap 5 compatible, canvas-based rendering

---

## Standard Stack / 标准技术栈

### Existing Dependencies (Already Installed) / 已有依赖（已安装）

| Library | Version | Purpose |
|---------|---------|---------|
| Flask | 3.1.3 | Web framework |
| Flask-SQLAlchemy | 3.1.1 | ORM with JSONB support |
| WTForms | 3.2.1 | Dynamic form field rendering |
| Flask-WTF | 1.2.2 | CSRF protection |
| openpyxl | 3.1.5 | Excel file parsing |
| pandas | 2.3.3 | Data analysis (optional, for complex Excel) |
| Pillow | 11.3.0 | Image processing / thumbnail generation |

### New Dependencies for Phase 2 / Phase 2 新增依赖

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Chart.js | 4.4.x (CDN) | Statistics charts | Canvas-based, Bootstrap 5 compatible, easy JSON integration |
| DataTables | 1.11+ (CDN) | Server-side pagination | jQuery plugin, handles sort/filter/paginate server-side |

**Installation for new dependencies:**
```bash
# No pip install needed — DataTables and Chart.js are CDN-only
# Just add to templates via CDN
```

### Frontend (CDN)

| Library | Version | Purpose |
|---------|---------|---------|
| Bootstrap | 5.3.8 | UI framework (already in base.html) |
| DataTables | 1.11+ | Server-side pagination |
| Chart.js | 4.4.x | Statistics visualization |

---

## Architecture Patterns / 架构模式

### Recommended Project Structure / 推荐项目结构

```
app/
├── models/
│   ├── __init__.py
│   ├── user.py              # Phase 1 - existing
│   ├── certificate.py       # Phase 2 - Certificate model with JSONB
│   └── certificate_type.py  # Phase 2 - CertificateType enum/lookup
│
├── blueprints/
│   ├── certificates/
│   │   ├── __init__.py
│   │   ├── routes.py        # CRUD routes
│   │   ├── forms.py         # Dynamic forms
│   │   ├── services.py       # Business logic
│   │   ├── api.py            # DataTables JSON API endpoint
│   │   └── templates/
│   │       ├── list.html    # Card grid with DataTables
│   │       ├── detail.html  # Certificate detail + edit/delete
│   │       ├── upload.html  # Upload form with dynamic fields
│   │       └── import.html  # Excel batch import
│   └── statistics/          # Phase 2 - stats blueprint
│       ├── __init__.py
│       ├── routes.py
│       └── templates/
│           └── dashboard.html
│
├── templates/
│   ├── base.html             # Already exists
│   └── macros.html           # Already exists
│
└── static/
    └── js/
        └── certificates.js   # DataTables + Chart.js initialization
```

### Pattern 1: Certificate Model with JSONB Dynamic Fields

**What:** Certificate model stores fixed fields (type, owner, file) separately from dynamic fields in JSONB

**When to use:** Certificates have varying schemas based on type

**Source:** [SQLAlchemy JSON/JSONB Type](https://docs.sqlalchemy.org/20/core/type_basics.html)

```python
# app/models/certificate.py
from datetime import datetime
from app.extensions import db

class CertificateType(db.Model):
    """Certificate type lookup table."""
    __tablename__ = 'certificate_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # e.g., "比赛获奖证书"
    fields_schema = db.Column(db.JSON)  # Defines expected fields for this type
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<CertificateType {self.name}>'


class Certificate(db.Model):
    """Certificate record with dynamic fields."""
    __tablename__ = 'certificates'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    certificate_type_id = db.Column(db.Integer, db.ForeignKey('certificate_types.id'), nullable=False)

    # Fixed fields
    title = db.Column(db.String(200), nullable=False)  # e.g., "2024年数学竞赛一等奖"
    file_path = db.Column(db.String(500), nullable=False)  # UUID-based path
    original_filename = db.Column(db.String(255))  # Original upload name
    file_size = db.Column(db.Integer)  # Bytes
    file_mime_type = db.Column(db.String(100))  # e.g., "image/png", "application/pdf"

    # Dynamic fields stored as JSONB
    fields = db.Column(db.JSON)  # e.g., {"issuer": "学校", "award_date": "2024-01-01", "level": "省级"}

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = db.relationship('User', backref=db.backref('certificates', lazy='dynamic'))
    certificate_type = db.relationship('CertificateType', backref=db.backref('certificates', lazy='dynamic'))

    def __repr__(self):
        return f'<Certificate {self.id}: {self.title}>'

    def to_dict(self):
        """Serialize for DataTables JSON response."""
        return {
            'id': self.id,
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

### Pattern 2: Dynamic WTForms Based on Certificate Type

**What:** Form fields change based on selected certificate type using JavaScript + hidden form fields

**When to use:** Same form/page needs different fields for different certificate types

**Source:** [WTForms Dynamic Field Pattern](https://wtforms.readthedocs.io/en/stable/)

```python
# app/blueprints/certificates/forms.py
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional

class CertificateBaseForm(FlaskForm):
    """Base form with fixed fields."""
    certificate_type_id = SelectField('证书类型 / Certificate Type', coerce=int, validators=[DataRequired()])
    title = StringField('证书标题 / Title', validators=[DataRequired()])
    file = FileField('证书文件 / Certificate File', validators=[
        FileRequired(),
        FileAllowed(['pdf', 'png', 'jpg', 'jpeg', 'gif'], '只能是 PDF 或图片文件')
    ])
    submit = SubmitField('提交 / Submit')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate certificate type choices
        from app.models.certificate import CertificateType
        self.certificate_type_id.choices = [
            (ct.id, ct.name) for ct in CertificateType.query.order_by('name').all()
        ]


class DynamicCertificateForm(CertificateBaseForm):
    """Extended form with dynamic fields populated via JavaScript."""
    # Dynamic fields added at runtime based on certificate_type_id
    pass


# Field schemas for each certificate type (stored in CertificateType.fields_schema)
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

### Pattern 3: DataTables Server-Side with Flask JSON API

**What:** DataTables sends pagination/sort/search params to Flask, Flask returns JSON

**When to use:** Large datasets require server-side pagination

**Source:** [DataTables Server-Side Processing](https://datatables.net/examples/data_sources/server_side)

```python
# app/blueprints/certificates/api.py
from flask import request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.certificate import Certificate, CertificateType
from app.blueprints.certificates import certificates_bp
from sqlalchemy import or_

@certificates_bp.route('/api/data')
@login_required
def certificates_data():
    """DataTables server-side endpoint for certificate list."""
    # DataTables sends these parameters:
    draw = int(request.args.get('draw', 1))
    start = int(request.args.get('start', 0))
    length = int(request.args.get('length', 10))
    search_value = request.args.get('search[value]', '')
    order_column = int(request.args.get('order[0][column]', 0))
    order_dir = request.args.get('order[0][dir]', 'asc')

    # Column mapping (matches DataTables column index)
    columns = ['id', 'title', 'type', 'created_at']
    order_col = columns[order_column] if order_column < len(columns) else 'created_at'

    # Base query — non-admin sees only own certificates
    query = Certificate.query
    if not current_user.is_admin:
        query = query.filter_by(user_id=current_user.id)

    # Search across title and type
    if search_value:
        search_filter = or_(
            Certificate.title.ilike(f'%{search_value}%'),
            Certificate.certificate_type.has(CertificateType.name.ilike(f'%{search_value}%'))
        )
        query = query.filter(search_filter)

    # Total count before filtering
    total_count = query.count()

    # Apply sorting and pagination
    order_func = getattr(Certificate, order_col).asc() if order_dir == 'asc' else getattr(Certificate, order_col).desc()
    query = query.order_by(order_func).offset(start).limit(length)

    records = query.all()

    return jsonify({
        'draw': draw,
        'recordsTotal': Certificate.query.count(),  # Total without filter
        'recordsFiltered': total_count,
        'data': [cert.to_dict() for cert in records]
    })
```

```javascript
// app/static/js/certificates.js
$(document).ready(function() {
    $('#certificates-table').DataTable({
        ajax: '/certificates/api/data',
        processing: true,
        serverSide: true,
        columns: [
            { data: 'id', name: 'id' },
            { data: 'title', name: 'title' },
            { data: 'type', name: 'type' },
            { data: 'created_at', name: 'created_at' },
            { data: null, orderable: false, searchable: false } // Actions column
        ],
        order: [[3, 'desc']],  // Default sort by created_at desc
        language: {
            url: '//cdn.datatables.net/plug-ins/1.11.5/i18n/zh.json'  // Chinese translation
        }
    });
});
```

### Pattern 4: Excel Auto-Parse with openpyxl

**What:** Upload Excel file, system automatically detects column headers and maps to certificate fields

**When to use:** Batch import without requiring pre-defined template

```python
# app/blueprints/certificates/services.py
from openpyxl import load_workbook
from app.models.certificate import Certificate, CertificateType
from app.extensions import db

class ExcelImportService:
    """Service for auto-parsing Excel files for batch certificate import."""

    # Column name mappings (Excel header -> Certificate field)
    COLUMN_MAPPINGS = {
        'title': ['标题', '证书名称', '名称', 'name', 'title'],
        'type': ['类型', '证书类型', 'type'],
        'competition_name': ['比赛名称', '比赛', 'competition'],
        'award_level': ['奖项', '获奖等级', 'level', 'award_level'],
        'award_date': ['获奖日期', '获奖时间', 'award_date'],
        'organizer': ['主办单位', '组织单位', 'organizer'],
        'certificate_number': ['证书编号', '编号', 'number', 'certificate_number'],
        'honor_title': ['荣誉名称', '荣誉', 'honor'],
        'grant_date': ['授予日期', '授予时间', 'grant_date'],
        'grantor': ['授予单位', 'grantor'],
        'skill_name': ['职业技能', 'skill'],
        'skill_level': ['等级', 'skill_level'],
        'issuing_authority': ['发证机构', '颁发机构', 'issuer', 'issuing_authority'],
        'expiry_date': ['有效期', 'expiry'],
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
            return [], ['Excel 文件为空或第一行没有列标题']

        # Auto-detect column mapping
        column_map = cls._detect_columns(headers)

        if not column_map.get('title'):
            return [], ['未找到标题列（标题、名称、证书名称 等）']

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
                errors.append(f'第 {row_idx} 行解析错误: {str(e)}')

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

        # Build dynamic fields
        fields = {}
        for field_name, idx in column_map.items():
            if field_name not in ('title', 'type') and idx < len(row):
                value = row[idx]
                if value is not None:
                    fields[field_name] = str(value).strip() if isinstance(value, str) else value

        return {
            'title': title,
            'certificate_type_id': cert_type.id if cert_type else None,
            'fields': fields,
        }
```

### Pattern 5: Chart.js Statistics Dashboard

**What:** Flask serves JSON data, Chart.js renders charts

**When to use:** Statistics dashboard with time trends and breakdowns

```python
# app/blueprints/statistics/routes.py
from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from app.extensions import db
from app.models.certificate import Certificate, CertificateType
from sqlalchemy import func, extract
from datetime import datetime, timedelta

statistics_bp = Blueprint('statistics', __name__, url_prefix='/statistics')

@statistics_bp.route('/')
@login_required
def dashboard():
    """Statistics dashboard page."""
    return render_template('statistics/dashboard.html')

@statistics_bp.route('/api/chart/<chart_type>')
@login_required
def chart_data(chart_type):
    """Return JSON data for charts."""
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

        labels = [f'{int(row[0])}-{int(row[1]):02d}' for row in data]
        values = [row[2] for row in data]

        return jsonify({'labels': labels, 'values': values})

    return jsonify({'error': 'Unknown chart type'}), 400
```

```html
<!-- app/blueprints/statistics/templates/dashboard.html -->
{% extends "base.html" %}

{% block content %}
<div class="row">
    <div class="col-md-6 mb-4">
        <div class="card">
            <div class="card-header">证书类型分布 / Certificates by Type</div>
            <div class="card-body">
                <canvas id="typeChart"></canvas>
            </div>
        </div>
    </div>
    <div class="col-md-6 mb-4">
        <div class="card">
            <div class="card-header">月度趋势 / Monthly Trend</div>
            <div class="card-body">
                <canvas id="trendChart"></canvas>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Type distribution bar chart
    fetch('/statistics/api/chart/by_type')
        .then(r => r.json())
        .then(data => {
            new Chart(document.getElementById('typeChart'), {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: '证书数量',
                        data: data.values,
                        backgroundColor: 'rgba(54, 162, 235, 0.5)'
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { display: false } }
                }
            });
        });

    // Monthly trend line chart
    fetch('/statistics/api/chart/monthly_trend')
        .then(r => r.json())
        .then(data => {
            new Chart(document.getElementById('trendChart'), {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: '证书数量',
                        data: data.values,
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { display: false } }
                }
            });
        });
});
</script>
{% endblock %}
```

---

## Don't Hand-Roll / 禁止自研

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Server-side pagination | Custom pagination logic | DataTables serverSide option | Handles sort/filter/paginate consistently, proven in production |
| Dynamic form fields | Hardcoded field sets | JSONB + JavaScript form builder | Schema changes don't require code changes |
| Excel parsing | Template-based import | Auto-detect column mapping | Simpler UX, more robust for varying Excel formats |
| Charts | Matplotlib/ReportLab images | Chart.js + Canvas | Interactive, responsive, no server-side image generation |
| JSON field querying | String matching | SQLAlchemy JSON operators | SQL injection safe, database-indexed |

---

## Common Pitfalls / 常见陷阱

### Pitfall 1: JSONB Query with SQLite

**What goes wrong:** `contains()` and `has_key()` JSON operators work differently in SQLite vs PostgreSQL.

**Why it happens:** SQLite stores JSON as TEXT, not as native JSONB. JSON operators may not function as expected.

**How to avoid:** Use PostgreSQL for production. For SQLite dev, test JSONB queries thoroughly. Consider using JSON stored as TEXT with string matching for dev compatibility.

**Warning signs:** JSON query returns no results but data exists.

### Pitfall 2: DataTables Server-Side + Client-Side Mixed Mode

**What goes wrong:** Table renders but pagination/sort doesn't work correctly.

**Why it happens:** `serverSide: true` requires ALL data operations to go to server. Mixing client-side data with server-side processing causes conflicts.

**How to avoid:** Ensure `serverSide: true` is set AND your Flask endpoint handles all pagination/sort/filter. Never load data client-side when using serverSide mode.

**Warning signs:** Table shows all pages or sort doesn't reflect server-side results.

### Pitfall 3: WTForms Dynamic Fields Not in `hidden_tag()`

**What goes wrong:** Dynamic fields added via JavaScript don't appear in form submission.

**Why it happens:** WTForms only processes fields in `form.hidden_tag()`. JavaScript-added DOM elements aren't registered with WTForms.

**How to avoid:** Use hidden input fields that are already in the form, or submit dynamic fields as JSON in a single hidden field that WTForms processes.

```html
<!-- WRONG: Dynamic field won't be submitted -->
<input type="text" id="dynamic_field" name="dynamic_field">

<!-- CORRECT: Wrap in form hidden inputs -->
<form method="POST">
    {{ form.hidden_tag() }}
    <input type="hidden" name="dynamic_fields_json" id="dynamic_fields_json">
    <!-- JavaScript populates #dynamic_fields_json -->
</form>
```

**Warning signs:** Form submits but dynamic field values are empty in Flask.

### Pitfall 4: Excel Cell Data Type Mismatch

**What goes wrong:** Date columns parsed as datetime objects, numbers parsed as strings, causing validation errors.

**Why it happens:** openpyxl reads raw cell values with data_type. Dates are `datetime` objects, numbers are `float`, strings are `str`.

**How to avoid:** Normalize all values in `_parse_row()` — convert dates to ISO format strings, ensure numbers are cast properly.

**Warning signs:** Validation errors on batch import for seemingly valid data.

### Pitfall 5: Chart.js Canvas Re-render Memory Leak

**What goes wrong:** Charts don't update properly when data changes; memory usage grows.

**Why it happens:** Chart.js canvases need to be destroyed before re-rendering with new data.

**How to avoid:** Check if chart instance exists, destroy before creating new:

```javascript
if (window.myChart) {
    window.myChart.destroy();
}
window.myChart = new Chart(ctx, config);
```

**Warning signs:** Charts overlap or don't refresh when navigating between views.

---

## Environment Availability / 环境可用性

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | Runtime | ✓ | 3.9.6 | — |
| Flask | Web framework | ✓ | 3.1.3 | — |
| Flask-SQLAlchemy | ORM | ✓ | 3.1.1 | — |
| openpyxl | Excel parsing | ✓ | 3.1.5 | — |
| pandas | Data analysis | ✓ | 2.3.3 | Use openpyxl only |
| Chart.js | Charts | CDN | 4.4.0 | — |
| DataTables | Pagination | CDN | 1.11 | — |
| PostgreSQL | Production DB | ✗ (using SQLite) | — | SQLite for dev, PostgreSQL for prod |

**Missing dependencies with fallback:**
- **PostgreSQL**: Development uses SQLite. Production deployment should use PostgreSQL 15+ with JSONB for optimal performance.

---

## Validation Architecture / 验证架构

### Test Framework / 测试框架

| Property | Value |
|----------|-------|
| Framework | pytest 8.x + pytest-flask |
| Config file | `pytest.ini` or `pyproject.toml` |
| Quick run command | `pytest tests/ -x -q` |
| Full suite command | `pytest tests/ -v` |

### Phase Requirements to Test Map / 阶段需求测试映射

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CERT-01 | User can upload certificate file (image/PDF) | integration | `pytest tests/test_certificates.py::test_upload_certificate -x` | no |
| CERT-01 | Upload rejects files over 10MB | unit | `pytest tests/test_certificates.py::test_upload_size_limit -x` | no |
| CERT-04 | Dynamic fields change based on certificate type | integration | `pytest tests/test_certificates.py::test_dynamic_fields_by_type -x` | no |
| CERT-04 | JSONB stores and retrieves dynamic fields correctly | unit | `pytest tests/test_certificates.py::test_jsonb_dynamic_fields -x` | no |
| CERT-05 | Admin can view any user's certificate | integration | `pytest tests/test_certificates.py::test_admin_view_all_certificates -x` | no |
| CERT-05 | Admin can edit any certificate | integration | `pytest tests/test_certificates.py::test_admin_edit_certificate -x` | no |
| CERT-05 | Admin can delete any certificate | integration | `pytest tests/test_certificates.py::test_admin_delete_certificate -x` | no |
| CERT-05 | Non-admin cannot edit other's certificate | integration | `pytest tests/test_certificates.py::test_non_admin_cannot_edit_others -x` | no |
| CERT-06 | Excel import auto-detects column headers | unit | `pytest tests/test_excel_import.py::test_auto_detect_columns -x` | no |
| CERT-06 | Excel import creates certificate records | integration | `pytest tests/test_excel_import.py::test_batch_import_creates_records -x` | no |
| CERT-06 | Excel import handles errors gracefully | unit | `pytest tests/test_excel_import.py::test_batch_import_error_handling -x` | no |
| CERT-07 | Search finds certificates by title | integration | `pytest tests/test_certificates.py::test_search_by_title -x` | no |
| CERT-07 | Search finds certificates by type | integration | `pytest tests/test_certificates.py::test_search_by_type -x` | no |
| CERT-08 | Filter by date range works | integration | `pytest tests/test_certificates.py::test_filter_by_date_range -x` | no |
| CERT-08 | Filter by certificate type works | integration | `pytest tests/test_certificates.py::test_filter_by_type -x` | no |
| CERT-09 | Statistics API returns chart data | integration | `pytest tests/test_statistics.py::test_statistics_api -x` | no |
| CERT-09 | Dashboard renders charts | integration | `pytest tests/test_statistics.py::test_dashboard_renders -x` | no |

### Sampling Rate / 采样率

- **Per task commit:** `pytest tests/ -x -q` (fail fast)
- **Per wave merge:** `pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps / Wave 0 缺口

- [ ] `tests/conftest.py` - pytest fixtures (app, db, client, authenticated_client, admin_client)
- [ ] `tests/test_certificates.py` - CERT-01, CERT-04, CERT-05, CERT-07, CERT-08 tests
- [ ] `tests/test_excel_import.py` - CERT-06 tests
- [ ] `tests/test_statistics.py` - CERT-09 tests
- [ ] `app/models/certificate.py` - Certificate and CertificateType models
- [ ] `app/blueprints/certificates/forms.py` - Dynamic form classes
- [ ] `app/blueprints/certificates/services.py` - ExcelImportService

---

## Sources / 参考资料

### Primary (HIGH confidence) / 主要来源（高置信度）

- [Flask 3.1.x PyPI](https://pypi.org/project/Flask/) - verified version 3.1.3
- [Flask-SQLAlchemy 3.1.x PyPI](https://pypi.org/project/Flask-SQLAlchemy/) - verified version 3.1.1
- [SQLAlchemy JSON/JSONB Type](https://docs.sqlalchemy.org/20/core/type_basics.html) - JSON column with variant support
- [DataTables Server-Side Processing](https://datatables.net/examples/data_sources/server_side) - official server-side pattern
- [openpyxl Documentation](https://openpyxl.readthedocs.io/) - Excel read/write API
- [Chart.js Documentation](https://www.chartjs.org/docs/latest/) - chart configuration
- [Bootstrap 5 Cards](https://getbootstrap.com/docs/5.3/components/card/) - card layout patterns
- [WTForms Documentation](https://wtforms.readthedocs.io/en/stable/) - dynamic field patterns

### Secondary (MEDIUM-HIGH confidence) / 次要来源（中高置信度）

- [Flask Application Factory Pattern](https://flask.palletsprojects.com/en/stable/tutorial/factory/) - project structure
- [Flask File Uploads](https://flask.palletsprojects.com/en/stable/patterns/fileuploads/) - file handling security

---

## Metadata / 元数据

**Confidence breakdown:**
- Standard Stack: HIGH - all versions verified from PyPI/CDN, established libraries
- Architecture: HIGH - patterns from official docs and established Flask community practices
- Pitfalls: MEDIUM-HIGH - documented from common issues, some SQLite JSONB limitations are environment-specific

**Research date:** 2026-03-24
**Valid until:** 2026-04-24 (30 days for stable libraries)
