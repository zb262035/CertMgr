# Technology Stack

**Project:** School Certificate Management System
**Researched:** 2026-03-19
**Confidence:** MEDIUM-HIGH (versions verified via PyPI, architecture patterns from official docs)

---

## Recommended Stack

### Core Runtime

| Technology | Version | Purpose | Rationale |
|------------|---------|---------|-----------|
| **Python** | 3.11 LTS | Runtime | Best Windows Server compatibility, LTS stability, wide hosting support. 3.12 also acceptable. Avoid 3.13 for production (too new). |

### Web Framework

| Technology | Version | Purpose | Rationale |
|------------|---------|---------|-----------|
| **Flask** | 3.1.x | Web framework | Pallets Projects flagship. Stable, well-documented, extensive ecosystem. Python >=3.9 required. |

### Database

| Technology | Version | Purpose | Rationale |
|------------|---------|---------|-----------|
| **PostgreSQL** | 15+ | Primary database | **RECOMMENDED over SQLite** for production. Better concurrency, ACID compliance, reliable backups. SQLite acceptable for single-server dev/testing with <1000 users, but PostgreSQL is more appropriate for a school environment where data integrity matters. |
| **Flask-SQLAlchemy** | 3.1.x | ORM | Official Flask ORM extension. SQLAlchemy 2.x required. Provides db.Model, scoped sessions, automatic table names. |
| **Flask-Migrate** | 4.1.x | Database migrations | Alembic wrapper for Flask. Handles schema changes without data loss. Version 4.1.0 released Jan 2025. |

### Authentication

| Technology | Version | Purpose | Rationale |
|------------|---------|---------|-----------|
| **Flask-Login** | 0.6.x | Session management | Standard for Flask auth. User sessions, remember_me, login_required. Version 0.6.3 (Oct 2023). **Note:** 0.7.x documentation exists but PyPI shows 0.6.3 as latest stable. |
| **Flask-WTF** | 1.2.x | Form validation + CSRF | Integrates WTForms with Flask. CSRF protection required for file uploads. Version 1.2.2 (Oct 2024). |
| **WTForms** | 3.2.x | Form handling | Required by Flask-WTF. Version 3.2.1 (Oct 2024). Python >=3.9. |

### File Handling

| Technology | Version | Purpose | Rationale |
|------------|---------|---------|-----------|
| **Pillow** | 12.1.x | Image processing | Thumbnail generation, format validation, EXIF stripping for uploads. Version 12.1.1 (Feb 2026). |
| **python-dotenv** | 1.2.x | Environment config | Load .env files in development. Keeps secrets out of code. Version 1.2.2 (Mar 2026). Python >=3.10. |

### PDF Generation

| Technology | Version | Purpose | Rationale |
|------------|---------|---------|-----------|
| **ReportLab** | 4.4.x | PDF creation | Certificate export/print. Mature, well-supported. Version 4.4.10 (Feb 2026). Python >=3.9. **DO NOT use WeasyPrint** (requires system dependencies, problematic on Windows). |

### Frontend

| Technology | Version | Purpose | Rationale |
|------------|---------|---------|-----------|
| **Bootstrap** | 5.3.8 | UI framework | Current stable (as of Mar 2026). Responsive grid, components, JS bundle with Popper. **DO NOT use Bootstrap 3/4** (security updates stopped). |
| **DataTables** | 1.11+ | Table display | Server-side pagination, search, sorting. Bootstrap 5 integration via `datatables.net-dt`. Essential for certificate lists with 1000+ records. |

### WSGI Server

| Technology | Version | Purpose | Rationale |
|------------|---------|---------|-----------|
| **Waitress** | 3.0.x | WSGI server | **RECOMMENDED for Windows Server**. Cross-platform, pure Python, no C extensions. Version 3.0.2 (Nov 2024). **DO NOT use Gunicorn** (Unix-only, does not run on Windows). |

---

## Chinese School IT Environment Considerations

### Windows Server Deployment

For schools that already run Windows Server:

```
Internet → IIS (reverse proxy) → Waitress (Flask on port 8000)
```

**Why this approach:**
- IIS handles SSL termination, static file caching, security hardening (familiar to Chinese school IT staff)
- Waitress runs Flask app internally (no Gunicorn on Windows)
- Flask `ProxyFix` middleware handles X-Forwarded headers

**Configuration:**
```python
# app.py
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
```

### Anti-Recommendations for Chinese School Environment

| Technology | Why Avoid | Alternative |
|------------|-----------|-------------|
| **MySQL** | Oracle-owned, dropped Python 3.x support in original connector, licensing concerns | PostgreSQL |
| **MongoDB** | Overkill for relational certificate data, operational complexity | PostgreSQL JSONB if semi-structured needed |
| **WeasyPrint** | Requires GTK/CAIRO system libraries, painful on Windows | ReportLab |
| **Gunicorn** | Unix-only (no Windows support), problematic in Windows Server envs | Waitress |
| **Bootstrap 3/4** | Security updates ended | Bootstrap 5.3 |
| **SQLite (production)** | Single-writer limitation, no remote access, poor backup story | PostgreSQL |
| **Celery + Redis** | Operational complexity overkill for ~1000 users, Redis Windows issues | Skip for MVP; use Flask-APScheduler if background tasks needed |

### Network Considerations

- Many Chinese schools have **restricted outbound internet** - prefer CDN fallbacks for Bootstrap/DataTables
- Consider hosting Bootstrap JS locally if CDN access is unreliable
- Print functionality may need to support **Chinese fonts** (include noto-fonts or similar)

---

## File Storage

### Local Storage (Recommended for MVP)

```
certificates/
  ├── originals/      # uploaded PDFs/photos
  ├── thumbnails/     # generated previews
  └── exports/        # temporary PDF exports
```

**Requirements:**
- Backups to another drive/location (critical)
- Virus scanning on upload (integrate with Windows Defender or ClamAV)
- Path validation to prevent path traversal attacks

**NOT recommended:** Database BLOBs (makes backups difficult, strains DB server)

---

## Installation

```bash
# Core dependencies
pip install Flask==3.1.3
pip install Flask-SQLAlchemy==3.1.1
pip install Flask-Migrate==4.1.0
pip install Flask-Login==0.6.3
pip install Flask-WTF==1.2.2
pip install WTForms==3.2.1
pip install psycopg2-binary==2.0.48
pip install Pillow==12.1.1
pip install ReportLab==4.4.10
pip install python-dotenv==1.2.2
pip install waitress==3.0.2

# Frontend (via CDN or npm)
# Bootstrap 5.3.8
# DataTables 1.11+
```

---

## Sources

- [Flask 3.1.x PyPI](https://pypi.org/project/Flask/) - Python >=3.9, released Feb 2026
- [Flask-SQLAlchemy 3.1.x PyPI](https://pypi.org/project/Flask-SQLAlchemy/) - SQLAlchemy 2.x required
- [Flask-Migrate 4.1.x PyPI](https://pypi.org/project/Flask-Migrate/) - released Jan 2025
- [Flask-Login 0.6.x PyPI](https://pypi.org/project/Flask-Login/) - released Oct 2023
- [Flask-WTF 1.2.x PyPI](https://pypi.org/project/Flask-WTF/) - released Oct 2024
- [WTForms 3.2.x PyPI](https://pypi.org/project/WTForms/) - Python >=3.9
- [psycopg2-binary 2.0.x PyPI](https://pypi.org/project/psycopg2-binary/) - PostgreSQL adapter
- [Pillow 12.1.x PyPI](https://pypi.org/project/Pillow/) - Python >=3.10
- [ReportLab 4.4.x PyPI](https://pypi.org/project/reportlab/) - Python >=3.9, released Feb 2026
- [python-dotenv 1.2.x PyPI](https://pypi.org/project/python-dotenv/) - Python >=3.10
- [waitress 3.0.x PyPI](https://pypi.org/project/waitress/) - cross-platform, Windows-compatible
- [Bootstrap 5.3 docs](https://getbootstrap.com/docs/5.3/getting-started/introduction/) - v5.3.8 current
- [Flask deployment docs - ProxyFix](https://flask.palletsprojects.com/en/stable/deploying/) - IIS reverse proxy guidance
