# Architecture Patterns: Certificate Management System

**Domain:** School certificate management (Flask + Bootstrap + SQLite/PostgreSQL)
**Researched:** 2026-03-19
**Confidence:** MEDIUM-HIGH (based on Flask/Pallets official documentation)

## Recommended Architecture

### High-Level Structure

```
CertMgr/
├── app/
│   ├── __init__.py          # Application factory, extensions init
│   ├── config.py            # Configuration classes
│   ├── extensions.py        # Shared Flask extensions (db, login_manager, etc.)
│   │
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── certificate.py
│   │   ├── certificate_type.py
│   │   └── field_definition.py
│   │
│   ├── blueprints/          # Modular route containers
│   │   ├── __init__.py
│   │   ├── auth/            # Authentication module
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   ├── forms.py
│   │   │   └── templates/
│   │   ├── certificates/    # Certificate CRUD module
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   ├── forms.py
│   │   │   ├── templates/
│   │   │   └── services.py
│   │   ├── admin/            # Admin management module
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   ├── forms.py
│   │   │   └── templates/
│   │   └── api/              # REST API module (future)
│   │       ├── __init__.py
│   │       └── routes.py
│   │
│   ├── services/            # Business logic layer
│   │   ├── __init__.py
│   │   ├── certificate_service.py
│   │   ├── file_storage_service.py
│   │   ├── auth_service.py   # Pluggable auth adapter
│   │   └── export_service.py
│   │
│   ├── templates/           # Base templates
│   │   ├── base.html
│   │   └── macros.html
│   │
│   └── static/
│       ├── css/
│       ├── js/
│       └── uploads/         # Certificate file storage
│
├── instance/                # Instance-specific files (not in git)
│   ├── config.py
│   └── uploads/             # Uploaded certificate files
│
├── migrations/              # Alembic database migrations
├── tests/
├── requirements.txt
└── run.py                   # Application entry point
```

### Component Boundaries

| Component | Responsibility | Communicates With |
|-----------|---------------|-------------------|
| **app/__init__.py** | Application factory, blueprint registration, extension setup | All modules via imports |
| **app/extensions.py** | Shared extension instances (db, login_manager, etc.) | All modules import from here |
| **models/** | SQLAlchemy ORM models, data validation | Services call models, routes pass models to templates |
| **blueprints/auth/** | Login, logout, registration, password reset | Uses auth_service, user model |
| **blueprints/certificates/** | Certificate CRUD, search, viewing | Uses certificate_service, file_storage_service |
| **blueprints/admin/** | Batch import, statistics, user management | Uses certificate_service, user model |
| **blueprints/api/** | REST API endpoints (future) | Services layer |
| **services/** | Business logic, file handling, export | Models for data, blueprints for routing |

### Data Flow

```
[Browser]
    |
    v
[Flask Routes (blueprints)]
    |
    +-- GET /certificates --> [CertificateService.get_list()] --> [Certificate Model]
    |                                                                   |
    |<-- Jinja2 Template <------------------------------------------------+
    |
    +-- POST /certificates/upload --> [FileStorageService.save()] --> [File System]
    |                               --> [CertificateService.create()] --> [Certificate Model]
    |
    +-- GET /admin/stats --> [CertificateService.get_statistics()] --> [Aggregated Data]

[Database (SQLite/PostgreSQL)]
    |
    v
[Certificate Model] <-- JSONB dynamic_fields column
```

### Database Schema Design (Dynamic Certificate Fields)

**Recommendation: Hybrid JSONB + Normalized Core Fields**

Use PostgreSQL JSONB for dynamic certificate attributes while keeping core fields normalized.

```sql
-- Certificate types (e.g., "比赛获奖", "荣誉证书", "资格证")
CREATE TABLE certificate_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Field definitions for each certificate type (for UI generation)
CREATE TABLE field_definitions (
    id SERIAL PRIMARY KEY,
    certificate_type_id INTEGER REFERENCES certificate_types(id),
    field_name VARCHAR(50) NOT NULL,      -- e.g., "award_level"
    field_label VARCHAR(100) NOT NULL,    -- e.g., "获奖等级"
    field_type VARCHAR(20) NOT NULL,      -- text, date, select, number
    field_options JSONB,                  -- For select type: {"options": ["一等奖", "二等奖"]}
    display_order INTEGER DEFAULT 0,
    required BOOLEAN DEFAULT FALSE,
    searchable BOOLEAN DEFAULT TRUE       -- Index this field for search
);

-- Core certificates table with JSONB for dynamic fields
CREATE TABLE certificates (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    certificate_type_id INTEGER REFERENCES certificate_types(id) NOT NULL,

    -- Normalized common fields
    title VARCHAR(200) NOT NULL,          -- Certificate title
    issuer VARCHAR(200) NOT NULL,         -- Issuing organization
    issue_date DATE NOT NULL,

    -- File information
    file_path VARCHAR(500),               -- Path to stored file
    file_hash VARCHAR(64),                -- SHA-256 for integrity
    original_filename VARCHAR(255),

    -- Dynamic fields stored as JSONB
    -- e.g., {"award_level": "一等奖", "competition_name": "数学竞赛"}
    dynamic_fields JSONB DEFAULT '{}',

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id),
    verified BOOLEAN DEFAULT FALSE,
    verified_by INTEGER REFERENCES users(id),
    verified_at TIMESTAMP
);

-- Index for common queries
CREATE INDEX idx_certificates_user ON certificates(user_id);
CREATE INDEX idx_certificates_type ON certificates(certificate_type_id);
CREATE INDEX idx_certificates_date ON certificates(issue_date);

-- GIN index for dynamic fields (flexible querying)
CREATE INDEX idx_certificates_dynamic ON certificates USING GIN (dynamic_fields);
```

**Why JSONB over EAV:**

| Factor | JSONB | EAV |
|--------|-------|-----|
| Querying dynamic fields | `dynamic_fields @> '{"award_level": "一等奖"}'` | Multiple JOINs |
| Schema evolution | No migration needed | ALTER TABLE |
| Storage efficiency | Compact for sparse data | Row per attribute |
| Nesting support | Yes (awards[0].level) | No |
| Complexity | Simple insert/update | Complex pivoting |

**When EAV might be better:**
- Need foreign key constraints on attribute values (e.g., validated dropdown lists)
- Need individual B-tree indexes per attribute for complex reporting
- Third-party tools require normalized structure

### File Storage Strategy

**Local filesystem with UUID-based paths:**

```
instance/uploads/
├── {year}/
│   ├── {month}/
│   │   ├── {uuid}.pdf
│   │   └── {uuid}.jpg
```

**Key Design Decisions:**

1. **Path = UUID, not user-provided filename**
   - Prevents path traversal attacks
   - Avoids filename collisions
   - `secure_filename()` + UUID generation

2. **Directory sharding by date**
   - Limits files per directory (subtle filesystem optimization)
   - Enables easy archival/deletion by date range

3. **Store metadata in database, not filesystem**
   - Original filename, SHA-256 hash, MIME type in `certificates` table
   - Filesystem only stores binary content

4. **File serving via `send_from_directory`**
   - Prevents directory traversal
   - Set `build_only=True` in production for performance

```python
# file_storage_service.py
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename

class FileStorageService:
    UPLOAD_FOLDER = 'instance/uploads'
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in FileStorageService.ALLOWED_EXTENSIONS

    @staticmethod
    def save_file(file, base_path=None):
        if not file or file.filename == '':
            raise ValueError("No file provided")

        if not FileStorageService.allowed_file(file.filename):
            raise ValueError(f"File type not allowed")

        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{ext}"

        # Directory sharding: /year/month/
        now = datetime.now()
        date_path = os.path.join(str(now.year), f"{now.month:02d}")

        full_dir = os.path.join(base_path or FileStorageService.UPLOAD_FOLDER, date_path)
        os.makedirs(full_dir, exist_ok=True)

        full_path = os.path.join(full_dir, unique_filename)
        file.save(full_path)

        return {
            'path': os.path.join(date_path, unique_filename),
            'original_filename': secure_filename(file.filename),
            'size': os.path.getsize(full_path)
        }
```

### Authentication System (Pluggable Architecture)

**Pattern: Adapter/Strategy Pattern for Auth Backends**

```python
# app/services/auth_service.py
from abc import ABC, abstractmethod

class AuthAdapter(ABC):
    """Abstract base for authentication backends"""

    @abstractmethod
    def authenticate(self, username, password):
        pass

    @abstractmethod
    def get_user_by_id(self, user_id):
        pass

    @abstractmethod
    def get_user_by_username(self, username):
        pass

# app/services/auth_backends.py
class LocalAuthAdapter(AuthAdapter):
    """Local database authentication"""

    def authenticate(self, username, password):
        # Check against hashed password in database
        pass

class SSOAuthAdapter(AuthAdapter):
    """Enterprise SSO (OA/WeChat Work/ CAS)"""

    def authenticate(self, username, password):
        # Delegate to external SSO
        pass

# app/extensions.py
from flask_login import LoginManager
login_manager = LoginManager()

# app/__init__.py
def create_app():
    app = Flask(__name__)

    # Select auth backend via config
    auth_backend = app.config.get('AUTH_BACKEND', 'local')
    if auth_backend == 'sso':
        from app.services.auth_backends import SSOAuthAdapter
        auth_adapter = SSOAuthAdapter()
    else:
        from app.services.auth_backends import LocalAuthAdapter
        auth_adapter = LocalAuthAdapter()

    app.extensions['auth_adapter'] = auth_adapter

    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        auth_adapter = current_app.extensions['auth_adapter']
        return auth_adapter.get_user_by_id(user_id)
```

**Pluggable points:**
1. `AUTH_BACKEND` config variable selects adapter
2. Auth adapter interface is consistent regardless of backend
3. Future: Add `WeChatWorkAuthAdapter`, `CASAuthAdapter` without changing app code

### API Design vs Server-Side Rendering

**Recommendation: Server-Side Rendering with Flask + Bootstrap (Phase 1)**

For a school certificate management system with ~1000 users:

| Factor | Server-Side (Jinja2) | REST API + SPA |
|--------|---------------------|----------------|
| **Complexity** | Low (Flask default) | High (separate frontend) |
| **SEO** | Not critical | Not critical |
| **Interactivity** | Bootstrap + minimal JS | Full JS framework needed |
| **Dev speed** | Fast for CRUD | Slower (two codebases) |
| **Mobile** | Responsive enough | Better with dedicated frontend |
| **Auth integration** | Flask-Login native | Need token management |

**When to add REST API:**
- Phase 2 or later if mobile app needed
- Third-party integrations required
- Complex real-time features
- Separate frontend team

**API Design if needed later:**

```python
# app/blueprints/api/__init__.py
from flask import Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# app/blueprints/api/routes.py
@api_bp.route('/certificates', methods=['GET'])
def list_certificates():
    """List certificates with filtering"""
    user_id = request.args.get('user_id')
    cert_type = request.args.get('type')
    # ... filtering logic
    return jsonify(certificates)

@api_bp.route('/certificates/<int:id>', methods=['GET'])
def get_certificate(id):
    """Get single certificate with file URL"""
    cert = Certificate.query.get_or_404(id)
    return jsonify({
        'id': cert.id,
        'title': cert.title,
        'dynamic_fields': cert.dynamic_fields,
        'file_url': url_for('download_file', name=cert.file_path)
    })

@api_bp.route('/certificates', methods=['POST'])
@login_required
def create_certificate():
    """Create certificate (handles file upload)"""
    # Handle multipart form data
    pass
```

### Suggested Build Order (Architecture Implications)

**Phase 1: Foundation (Build first, enables all others)**
1. **Project structure with app factory**
   - `extensions.py`, `__init__.py` with factory pattern
   - This is infrastructure - build once, refactor later is painful

2. **Models (user, certificate, certificate_type)**
   - Define database schema early
   - JSONB dynamic fields schema decision here

3. **Auth blueprint (local auth)**
   - Flask-Login integration
   - Auth adapter interface (even if only local impl)

4. **File storage service**
   - File upload/download infrastructure
   - Security patterns (secure_filename, path validation)

**Phase 2: Core Features (Depends on Phase 1)**
5. **Certificate CRUD blueprint**
   - Dynamic form generation from field_definitions
   - Search with JSONB querying

6. **Admin blueprint**
   - Batch import (Excel)
   - Statistics queries

**Phase 3: Polish & Integration (Depends on Phase 2)**
7. **Export service (PDF generation)**
8. **SSO integration** (swap auth adapter)

**Phase 4: API (Optional, depends on Phase 2)**
9. **REST API blueprint**
   - Only if mobile app or third-party integration needed

### Build Order Rationale

```
Foundation (Phase 1)
    |
    +-- extensions.py, factory --> [auth] needs this
    |                             --> [certificates] needs this
    |                             --> [admin] needs this
    |
    +-- Models --> [auth] validates users
               --> [certificates] CRUD operations
               --> [file_storage] metadata in DB
    |
    +-- Auth service --> [certificates] needs @login_required
                     --> [admin] needs role checking
    |
    v
Core Features (Phase 2)
    |
    +-- Certificate CRUD --> [admin] admin can edit any
    |
    +-- Admin features --> Depends on certificate CRUD
    |
    v
Polish (Phase 3)
    |
    +-- Export PDF --> Uses certificate data
    +-- SSO --> Uses auth adapter interface
```

### Anti-Patterns to Avoid

**1. Global Flask app instance**
```python
# BAD - prevents testing, multiple app instances
app = Flask(__name__)

# GOOD - factory pattern
def create_app(config=None):
    app = Flask(__name__)
    if config:
        app.config.from_mapping(config)
    return app
```

**2. Circular imports via routes**
```python
# BAD - routes imports models, models imports db, circular
from app import db
from app.routes import certificates

# GOOD - use extensions.py for shared db instance
from app.extensions import db
```

**3. Storing files without UUID**
```python
# BAD - path traversal, collisions
filename = request.form['filename']
file.save(f"/uploads/{filename}")

# GOOD - UUID-based path
import uuid
filename = f"{uuid.uuid4()}.pdf"
file.save(os.path.join(UPLOAD_DIR, filename))
```

**4. Auth checks in every route**
```python
# BAD - repeated code
@app.route('/admin')
def admin_panel():
    if not current_user.is_admin:
        abort(403)
    return render_template(...)

# GOOD - decorator
@app.route('/admin')
@admin_required
def admin_panel():
    return render_template(...)
```

### Scalability Considerations

| Scale | Challenge | Approach |
|-------|-----------|----------|
| 100 users | SQLite fine | Default, minimal ops |
| 1,000 users | SQLite acceptable | Add indexes on user_id, type_id |
| 10,000 users | PostgreSQL recommended | Connection pooling, read replicas |
| 100K+ certificates | File storage | Consider object storage (S3-compatible) |

**For this project (~1000 users, unknown certificate volume):**
- Start with SQLite, migrate to PostgreSQL if needed
- JSONB GIN indexes for dynamic field search
- File storage: local initially, abstract behind service for later S3 migration

### Sources

- [Flask Blueprints Documentation](https://flask.palletsprojects.com/en/stable/blueprints/)
- [Flask Application Factory](https://flask.palletsprojects.com/en/stable/tutorial/factory/)
- [Flask Extension Development](https://flask.palletsprojects.com/en/stable/extensiondev/)
- [Flask File Uploads](https://flask.palletsprojects.com/en/stable/patterns/fileuploads/)
- [Flask Configuration](https://flask.palletsprojects.com/en/stable/config/)
- [PostgreSQL JSONB Documentation](https://www.postgresql.org/docs/current/datatype-json.html)
- [Flask-Login Documentation](https://flask-login.readthedocs.io/en/stable/)
