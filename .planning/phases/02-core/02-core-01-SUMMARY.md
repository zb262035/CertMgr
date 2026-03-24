---
phase: 02-core
plan: 01
subsystem: database
tags: [flask, sqlalchemy, certificate, jsonb]

# Dependency graph
requires:
  - phase: 01-foundation
    provides: User model, Flask app factory, file storage
provides:
  - Certificate and CertificateType models with JSONB dynamic fields
  - Full CRUD routes (upload, list, detail, edit, delete)
  - Dynamic fields switching on same page
  - Card-based certificate list template
affects: [02-core-02, 02-core-03]

# Tech tracking
tech-stack:
  added: [wtforms, flask-wtf]
  patterns: [jsonb-dynamic-fields, card-layout]

key-files:
  created:
    - app/models/certificate.py
    - app/blueprints/certificates/forms.py
    - app/blueprints/certificates/routes.py
    - app/blueprints/certificates/services.py
    - app/blueprints/certificates/templates/list.html
    - app/blueprints/certificates/templates/detail.html
    - app/blueprints/certificates/templates/upload.html
    - app/blueprints/certificates/templates/edit.html
  modified:
    - app/models/__init__.py
    - app/__init__.py

key-decisions:
  - "JSONB for dynamic certificate fields"
  - "Card layout for certificate list"
  - "Edit/delete from detail page"

patterns-established:
  - "CertificateType lookup table pattern"
  - "Dynamic fields via JSONB in Certificate model"
  - "CertificateService layer for business logic"

requirements-completed: [CERT-01, CERT-02, CERT-04, CERT-05]

# Metrics
duration: 12min
completed: 2026-03-24
---

# Phase 2 Wave 1: Certificate CRUD Summary

**Certificate model with JSONB dynamic fields, full CRUD operations, card-based templates with dynamic field switching**

## Performance

- **Duration:** 12 min
- **Started:** 2026-03-24T03:08:43Z
- **Completed:** 2026-03-24T03:18:03Z
- **Tasks:** 4
- **Files modified:** 11

## Accomplishments

- Certificate model with JSONB dynamic fields
- 4 certificate types seeded on startup (比赛获奖证书, 荣誉证书, 资格证, 职业技能等级证书)
- Full CRUD routes: upload, list, detail, edit, delete, file serving
- Dynamic fields switch on same page based on certificate type selection
- Card-based certificate list with thumbnail, title, type, date
- Permission control: users see own, admin sees all

## Task Commits

Each task was committed atomically:

1. **Task 1: Certificate models** - `8245ef6` (feat)
2. **Task 2: Certificate forms** - `51d454c` (feat)
3. **Task 3: CRUD routes and services** - `5ff74f3` (feat)
4. **Task 4: Templates** - `c92d494` (feat)

## Files Created/Modified

- `app/models/certificate.py` - Certificate and CertificateType models
- `app/models/__init__.py` - Updated to export Certificate, CertificateType
- `app/__init__.py` - Seed certificate types on startup
- `app/blueprints/certificates/forms.py` - CertificateBaseForm, CertificateEditForm, FIELD_SCHEMAS
- `app/blueprints/certificates/routes.py` - All CRUD routes
- `app/blueprints/certificates/services.py` - CertificateService
- `app/blueprints/certificates/__init__.py` - Blueprint with routes import
- `app/blueprints/certificates/templates/list.html` - Card grid layout
- `app/blueprints/certificates/templates/detail.html` - Detail with edit/delete
- `app/blueprints/certificates/templates/upload.html` - Dynamic fields form
- `app/blueprints/certificates/templates/edit.html` - Edit with pre-populated fields

## Decisions Made

- Used JSONB for dynamic fields (not EAV) for simplicity and performance
- Card layout for list view per user decision
- Dynamic fields switch on same page without page reload
- Edit/delete operations accessed from detail page per user decision

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - all tasks completed successfully.

## Next Phase Readiness

Wave 2 (Plan 02) can use:
- Certificate model already created
- CertificateService for integration with DataTables and Excel import
- CRUD routes as foundation for search/filter enhancements

---
*Phase: 02-core-01*
*Completed: 2026-03-24*
