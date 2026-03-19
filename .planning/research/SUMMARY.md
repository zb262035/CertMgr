# Project Research Summary

**Project:** CertMgr - School Certificate Management System
**Domain:** Education administrative software (Chinese school context)
**Researched:** 2026-03-19
**Confidence:** MEDIUM-HIGH

## Executive Summary

CertMgr is a document management system for school certificates (awards, transcripts, qualifications). Experts build such systems using Flask with the application factory pattern, PostgreSQL for data integrity at scale, and JSONB columns for flexible certificate metadata. The recommended stack prioritizes Windows Server compatibility given Chinese school IT environments: Waitress (not Gunicorn) as WSGI server, ReportLab (not WeasyPrint) for PDF generation, and Bootstrap 5.3 for responsive UI.

The core architectural decision is using JSONB for dynamic certificate fields rather than hardcoded columns, enabling schools to define custom certificate types without schema migrations. File storage must use UUID naming to prevent collisions and path traversal attacks. Unicode normalization (NFC) is mandatory for Chinese character handling across database, filesystem, and PDF generation.

Key risks include: Chinese school servers running Windows/IIS (not Linux), requiring cross-platform path handling via pathlib; file storage corruption from non-UUID naming; and duplicate detection failures from Unicode normalization inconsistency. Mitigate by implementing file storage service early, normalizing all text input, and testing deployment on target Windows environment.

## Key Findings

### Recommended Stack

Production-grade Flask application with dependencies selected for Windows Server compatibility and Chinese character support. PostgreSQL recommended over SQLite for concurrency and reliable backups. Waitress (pure Python, no C extensions) is the WSGI server choice for Windows Server environments where Gunicorn cannot run.

**Core technologies:**
- **Flask 3.1.x** — web framework, Python >=3.9 required
- **PostgreSQL 15+** — primary database with JSONB support; SQLite acceptable for single-server dev/testing only
- **Flask-SQLAlchemy 3.1.x** — ORM with SQLAlchemy 2.x
- **Flask-Login 0.6.x** — session management and authentication
- **Waitress 3.0.x** — WSGI server; DO NOT use Gunicorn (Unix-only)
- **ReportLab 4.4.x** — PDF generation; DO NOT use WeasyPrint (requires system dependencies, problematic on Windows)
- **Bootstrap 5.3.8** — UI framework; DO NOT use Bootstrap 3/4 (security updates ended)
- **DataTables 1.11+** — server-side pagination for certificate lists
- **Pillow 12.1.x** — image processing for thumbnails and validation

### Expected Features

**Must have (table stakes):**
- Single file upload and download — staff submit and retrieve certificates
- Basic search by holder name — find certificates quickly
- Certificate list view with pagination — DataTables for 1000+ records
- User authentication with roles (Regular User, Admin)
- Admin: manual certificate add/edit/delete
- Admin: batch Excel/CSV import

**Should have (competitive):**
- Multi-filter search (type, date range, issuer, category)
- Statistics dashboard (counts by type, trends over time)
- PDF export for printing
- Photo upload for paper certificates (mobile camera capture)
- Dynamic metadata fields per certificate type

**Defer (v2+):**
- OCR auto-extraction — requires OCR service evaluation (Tesseract vs cloud APIs)
- Expiration tracking and alerts — needs scheduled jobs
- Custom certificate templates — template engine complexity
- Audit trail — who viewed/downloaded certificates
- REST API for third-party integration

**Explicitly avoid:**
- Blockchain verification (overengineered for internal use)
- QR code public portal (out of scope per PROJECT.md)
- Approval workflow (PROJECT.md excludes 审批流程)
- Native mobile app (responsive web covers this)
- Multi-tenancy (single school deployment)

### Architecture Approach

Flask application factory pattern with modular blueprints (auth, certificates, admin). Services layer for business logic separation. JSONB for dynamic certificate fields enables flexible metadata without schema changes. File storage uses UUID-based paths with date sharding, abstracted behind a service for later S3 migration.

**Major components:**
1. **app/__init__.py** — Application factory, blueprint registration, extension setup
2. **app/extensions.py** — Shared Flask extension instances (db, login_manager)
3. **app/models/** — SQLAlchemy models with JSONB dynamic_fields column
4. **app/blueprints/** — auth (login/logout), certificates (CRUD), admin (batch import, stats)
5. **app/services/** — Business logic layer (certificate_service, file_storage_service, auth_service with pluggable adapter)
6. **instance/uploads/** — Local file storage with {year}/{month}/{uuid}.ext structure

### Critical Pitfalls

1. **File Storage Without UUID Naming** — Original filenames cause collisions and Unicode corruption. Always rename on ingest: `{uuid4()}.{extension}`. Store original filename in database metadata.

2. **Unicode Normalization Inconsistency** — Chinese characters like "李" vs "李" (NFC vs NFD) compare as different. Normalize all text input to NFC using `unicodedata.normalize('NFC', text)` at ingestion points.

3. **Dynamic Fields as Hardcoded Columns** — New certificate types require schema migrations. Use JSONB column for certificate-specific data alongside fixed fields. Define certificate type templates in database, not code.

4. **No Incremental Backup Strategy** — Certificate files are large (100KB-2MB). Full backups exhaust disk space. Implement weekly full + daily incremental backups with checksum verification.

5. **Windows/IIS Deployment Assumptions** — Code works on Mac, fails on Windows. Use `pathlib` for all file operations, test on target OS early, keep paths short and ASCII where possible.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Foundation
**Rationale:** Architecture decisions that enable everything else. Build once, refactor later is painful.
**Delivers:** Project structure with app factory, core models (user, certificate, certificate_type with field_definitions), local authentication with Flask-Login, auth adapter interface (pluggable for future SSO).
**Avoids:** Pitfall #3 (dynamic fields as columns), Pitfall #6 (RBAC without hierarchy), Pitfall #10 (no audit trail), Pitfall #14 (timezone mismatch)
**Research Flags:** Schema review needed for JSONB field definitions; permission matrix design before coding

### Phase 2: Core Infrastructure
**Rationale:** File handling and database infrastructure must be solid before business features.
**Delivers:** File storage service with UUID naming and date sharding, incremental backup strategy, file size validation (16MB limit), indexes for search performance (GIN on JSONB, B-tree on common fields), multi-filter search capability.
**Avoids:** Pitfall #1 (file naming), Pitfall #5 (file size validation), Pitfall #7 (full-table scan), Pitfall #9 (Windows path issues)
**Stack:** PostgreSQL (or SQLite for dev), Flask-Migrate, Waitress
**Research Flags:** Needs integration testing on target Windows Server deployment environment

### Phase 3: Core Features
**Rationale:** Depends on Phase 1 (auth, models) and Phase 2 (file storage).
**Delivers:** Certificate CRUD with dynamic form generation, batch Excel/CSV import, statistics dashboard, multi-filter search UI, certificate preview.
**Features:** Multi-file upload, photo capture upload, dynamic metadata fields per type, multi-filter search, statistics
**Research Flags:** Excel parsing library selection; DataTables server-side pagination configuration

### Phase 4: Export & Polish
**Rationale:** Depends on Phase 3 having certificate data.
**Delivers:** PDF generation for certificates using ReportLab (bundled Chinese fonts), certificate templates as Jinja2 files, session timeout (30 min inactivity), export streaming for large datasets.
**Avoids:** Pitfall #8 (PDF tightly coupled), Pitfall #2 (backup), Pitfall #12 (export memory issues)
**Research Flags:** Chinese font bundling and licensing; PDF template testing in CI pipeline

### Phase Ordering Rationale

- Foundation must come first: app factory, models, and auth establish patterns that everything else depends on
- Core Infrastructure before Core Features: file storage and database indexing are foundational, not features
- Export deferred to Phase 4: PDF generation depends on having certificate data to export; template architecture should be designed early but implemented after core CRUD
- Differentiators (OCR, audit trail, expiration tracking) deferred to v2+: require solid foundation first

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 1:** JSONB field definition schema — complex, needs architecture review with domain experts
- **Phase 2:** Windows Server deployment specifics — Chinese school IT environment varies; integration testing essential
- **Phase 3:** Excel/CSV parsing library evaluation — openpyxl vs pandas vs alternatives for Chinese school data
- **Phase 4:** Chinese PDF font licensing and bundling requirements

Phases with standard patterns (skip research-phase):
- **Phase 1:** Flask application factory — well-documented in official Flask tutorial
- **Phase 2:** File upload handling — standard Flask patterns, Template provided in ARCHITECTURE.md

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM-HIGH | Versions verified via PyPI; Windows Server compatibility validated; PostgreSQL over SQLite recommendation strong |
| Features | MEDIUM | Based on domain knowledge and PROJECT.md; no competitor analysis (WebSearch unavailable) |
| Architecture | MEDIUM-HIGH | Flask patterns from official docs; JSONB approach well-established; file storage service pattern solid |
| Pitfalls | MEDIUM | Knowledge-based; WebSearch unavailable for verification; Chinese encoding specifics need production testing |

**Overall confidence:** MEDIUM-HIGH

### Gaps to Address

- **Chinese school IT environment specifics:** Actual Windows Server vs Linux distribution unknown; recommend Phase 2 integration testing
- **Competitor analysis:** No access to competitor product pages; recommend Phase 1 architecture review with actual school administrators
- **OCR evaluation:** Tesseract vs cloud APIs (Azure, Tencent) not compared; defer to Phase 3 planning
- **Print template requirements:** "Printable format" meaning unclear; need user research for Phase 4
- **Font licensing:** Chinese font (Noto Sans CJK, Source Han Sans) licensing for PDF bundling unclear

## Sources

### Primary (HIGH confidence)
- [Flask 3.1.x PyPI](https://pypi.org/project/Flask/) — stack versions and requirements
- [Flask Application Factory](https://flask.palletsprojects.com/en/stable/tutorial/factory/) — architecture pattern
- [PostgreSQL JSONB Documentation](https://www.postgresql.org/docs/current/datatype-json.html) — dynamic fields approach
- [Flask-Login Documentation](https://flask-login.readthedocs.io/en/stable/) — authentication pattern
- [Bootstrap 5.3 docs](https://getbootstrap.com/docs/5.3/getting-started/introduction/) — frontend framework

### Secondary (MEDIUM confidence)
- [ReportLab 4.4.x PyPI](https://pypi.org/project/reportlab/) — PDF generation, Chinese font integration notes
- [Waitress 3.0.x PyPI](https://pypi.org/project/waitress/) — Windows-compatible WSGI server
- [Flask deployment docs - ProxyFix](https://flask.palletsprojects.com/en/stable/deploying/) — IIS reverse proxy guidance
- Flask documentation on file handling — file upload security patterns
- OWASP security guidelines for RBAC — permission system design

### Tertiary (LOW confidence)
- Domain knowledge: Document management systems, school administrative software — needs validation against actual users
- Unicode normalization standards (UTR #15) — applied based on Python docs, production verification needed
- Chinese school server environment — general patterns, specific institutions vary

---
*Research completed: 2026-03-19*
*Ready for roadmap: yes*
