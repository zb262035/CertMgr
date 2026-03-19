# Roadmap: CertMgr

## Overview

CertMgr is a school certificate management system that enables faculty/staff to digitize and manage their certificates (competition awards, honors, qualifications, vocational skills). The journey spans three phases: building the Flask application foundation with authentication and file storage, implementing certificate CRUD with search/statistics, and adding PDF export, SSO integration, and advanced features.

## Phases

- [ ] **Phase 1: Foundation** - Flask app factory, models, local auth, file storage, permission control
- [ ] **Phase 2: Core** - Certificate CRUD, dynamic fields, upload/download, batch import, search, filter, stats
- [ ] **Phase 3: Enhancement** - PDF export, SSO integration, OCR, audit trail

## Phase Details

### Phase 1: Foundation

**Goal**: Application infrastructure enabling all subsequent work

**Depends on**: Nothing (first phase)

**Requirements**: AUTH-01, AUTH-02, CERT-03, CERT-11

**Success Criteria** (what must be TRUE):
  1. User can register account with email and password
  2. User can log in and stay logged in across browser sessions
  3. User can log out from any page
  4. Admin can view all user accounts in the system
  5. Users can only view and edit their own certificates (permission enforced)
  6. Certificate files are stored with UUID-based paths (no original filenames in storage)
  7. File upload/download respects permission boundaries

**Plans**: TBD

### Phase 2: Core

**Goal**: Full certificate management with search and statistics

**Depends on**: Phase 1

**Requirements**: CERT-01, CERT-02, CERT-04, CERT-05, CERT-06, CERT-07, CERT-08, CERT-09

**Success Criteria** (what must be TRUE):
  1. User can upload certificate file (image/PDF) and associate with their account
  2. User can capture photo of paper certificate and upload it
  3. User can view list of their own certificates with pagination
  4. User can edit their own certificate metadata (title, issuer, date, dynamic fields)
  5. User can delete their own certificates
  6. Different certificate types display different dynamic fields in forms
  7. User can search certificates by holder name
  8. User can filter certificates by type, date range, and issuer
  9. Admin can view all certificates in the system
  10. Admin can manually add/edit/delete any certificate
  11. Admin can batch import certificates from Excel file
  12. Admin can view statistics: certificate counts by type, trends over time

**Plans**: TBD

### Phase 3: Enhancement

**Goal**: Advanced features and integrations

**Depends on**: Phase 2

**Requirements**: AUTH-02 (SSO component), CERT-10

**Success Criteria** (what must be TRUE):
  1. User can export certificate as printable PDF with Chinese text
  2. System supports SSO integration via pluggable auth adapter (OA/WeChat Work/CAS)
  3. System logs audit trail: who created/modified/deleted certificates
  4. User can upload photo of paper certificate and system auto-extracts text (OCR)

**Plans**: TBD

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 0/TBD | Not started | - |
| 2. Core | 0/TBD | Not started | - |
| 3. Enhancement | 0/TBD | Not started | - |

## Coverage

**Requirements mapped to phases:**

| Requirement | Phase | Description |
|-------------|-------|-------------|
| AUTH-01 | Phase 1 | Account management (local auth) |
| AUTH-02 | Phase 1 | Auth adapter interface (pluggable SSO) |
| CERT-03 | Phase 1 | File storage (local filesystem) |
| CERT-11 | Phase 1 | Permission control (user vs admin) |
| CERT-01 | Phase 2 | Upload electronic certificate |
| CERT-02 | Phase 2 | Upload photo of paper certificate |
| CERT-04 | Phase 2 | Dynamic fields per certificate type |
| CERT-05 | Phase 2 | Admin manual entry/edit |
| CERT-06 | Phase 2 | Batch import from Excel |
| CERT-07 | Phase 2 | Search by name/type/date/issuer |
| CERT-08 | Phase 2 | Multi-filter search |
| CERT-09 | Phase 2 | Statistics dashboard |
| CERT-10 | Phase 3 | Export to printable PDF |
| OCR | Phase 3 | Auto-extract text from certificate photo |
| Audit | Phase 3 | Audit trail for certificate changes |

**Coverage:** 13/13 v1 requirements mapped ✓
**Out of scope:** 5 items (see PROJECT.md)
