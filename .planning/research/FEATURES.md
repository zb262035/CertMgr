# Feature Landscape

**Domain:** School Certificate Management System
**Researched:** 2026-03-19
**Research Confidence:** MEDIUM (WebSearch unavailable; based on domain knowledge and PROJECT.md context)

## Table Stakes

Features users expect. Missing = product feels incomplete or unusable.

| Feature | Why Expected | Complexity | Dependencies |
|---------|--------------|------------|--------------|
| **File Upload (single)** | Staff must be able to submit their certificates | Low | Storage backend |
| **File View/Download** | Staff need to retrieve their certificates | Low | Storage backend |
| **Basic Search (text)** | Find certificates by holder name | Low | Database indexing |
| **Certificate List View** | See all certificates in system | Low | Pagination |
| **User Authentication** | Login/logout to protect certificate data | Low | Session management |
| **Role: Regular User** | View own certificates only | Low | Permission layer |
| **Role: Admin** | View all certificates, edit any | Low | Permission layer |

## Core Features

Features that make the system functional for the stated use case.

| Feature | Why Expected | Complexity | Dependencies |
|---------|--------------|------------|--------------|
| **Multi-file Upload** | Bulk submission of multiple certificates | Medium | File handling, queue |
| **Photo Capture Upload** | Mobile camera to submit paper certificates | Medium | Mobile-responsive UI, client-side compression |
| **Batch Import (Excel/CSV)** | Admins migrate existing records or import bulk data | Medium | Excel parsing library, validation |
| **Dynamic Metadata Fields** | Different certificate types have different fields | Medium | Schema design, form builder |
| **PDF Generation for Export** | Printable certificate output | Medium | PDF library |
| **Multi-filter Search** | Filter by type, date range, issuer, category | Medium | Database query builder |
| **Certificate Preview** | View uploaded image/PDF in-browser | Medium | File viewer component |
| **Certificate Edit (Admin)** | Manually correct/add certificate data | Low | CRUD operations |
| **Certificate Delete** | Remove erroneous entries | Low | Soft-delete (audit trail) |
| **User Profile/Account** | Staff manage their own account | Low | User table |

## Statistics Features

| Feature | Why Valuable | Complexity | Dependencies |
|---------|--------------|------------|--------------|
| **Count by Type** | See distribution of certificate types | Low | Aggregation queries |
| **Trend Over Time** | Certificate acquisition over months/years | Medium | Time-series grouping |
| **Per-user Count** | How many certs each person has | Low | Aggregation queries |
| **Export Statistics** | Download stats as report | Medium | Report generation |

## Differentiators

Features that set this product apart. Not expected, but valued.

| Feature | Value Proposition | Complexity | Dependencies |
|---------|-------------------|------------|--------------|
| **OCR Auto-extraction** | Automatically fill metadata from certificate photo | High | OCR service/library, field mapping |
| **Expiration Tracking** | Alert when certificates expire | Medium | Scheduled jobs, notification system |
| **Mobile-optimized Upload** | Excellent mobile UX for photo capture | Medium | Responsive design, image processing |
| **Bulk Export** | Download all certificates as ZIP or combined PDF | Medium | File streaming, zip library |
| **Custom Certificate Templates** | Beautiful printable layouts | High | Template engine, designer |
| **API for Third-party Integration** | Data exchange with HR or other school systems | Medium | REST API, documentation |
| **Audit Trail** | Who viewed/downloaded which certificate | Medium | Logging system |
| **Duplicate Detection** | Warn when similar certificate already exists | Medium | Fuzzy matching, record similarity |

## Anti-Features

Features to explicitly NOT build (at least in v1).

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|---------------------|
| **Blockchain certificate verification** | Overengineered for internal use case; requires external authority | Trust school administrators |
| **QR code verification public portal** | Requires external-facing infrastructure, maintenance | Out of scope per PROJECT.md |
| **Certificate request/approval workflow** | PROJECT.md explicitly excludes审批流程 | Manual submission, admin batch import |
| **Native mobile app** | Web responsive design covers mobile use cases | Progressive Web App if truly needed |
| **Multi-tenancy (multiple schools)** | Single school deployment; adds complexity | Single-tenant architecture |
| **Certificate blockchain immutability** | Storage is local; database backup is sufficient | Regular database backups |
| **Real-time collaboration** | Certificates are individual records, not collaborative documents | N/A |
| **Gamification/badges** | Not aligned with school administrative use case | N/A |

## Feature Dependencies

```
User Authentication
    └── Role-based Access Control
            ├── Regular User (view own)
            └── Admin (view all, edit, delete, import)

File Storage
    └── File Upload/Download/Preview

Dynamic Metadata Schema
    └── Form Builder for Certificate Types
            └── Search & Filter by Fields

Search & Filter
    └── Statistics & Reporting

Batch Import
    └── Validation & Error Reporting

Export/Print
    └── PDF Generation
            └── Optional: Custom Templates

OCR (Future)
    └── Field Mapping
            └── Auto-fill on Upload
```

## MVP Recommendation

**Phase 1 Priority (Must Have):**
1. User authentication with role-based access
2. Single file upload and download
3. Basic search by name
4. Certificate list view with pagination
5. Admin: manual certificate add/edit/delete
6. Admin: batch Excel import

**Phase 2 (Core Functionality):**
1. Multi-filter search (type, date, issuer)
2. Statistics dashboard (counts, trends)
3. PDF export for printing
4. Photo upload for paper certificates
5. Dynamic metadata fields per certificate type

**Phase 3 (Enhancement):**
1. OCR auto-extraction
2. Expiration tracking and alerts
3. Custom certificate templates
4. Audit trail

**Explicitly Deferred:**
- Mobile native app (responsive web covers this)
- Blockchain verification (out of scope)
- Workflow/approval system (PROJECT.md excludes)
- Third-party API integration (v1+ only)

## Confidence Assessment

| Category | Confidence | Notes |
|----------|------------|-------|
| Table stakes | MEDIUM | Based on general document management system patterns |
| Core features | MEDIUM | Derived from PROJECT.md requirements |
| Differentiators | LOW | Would benefit from competitor analysis |
| Anti-features | MEDIUM | Based on explicit PROJECT.md out-of-scope |

## Sources

- PROJECT.md (CertMgr project context)
- Domain knowledge: Document management systems, school administrative software

## Gaps to Address

- **Competitor analysis:** No access to current competitor product pages due to WebSearch unavailability
- **User research:** Would benefit from interviews with actual school administrators
- **OCR selection:** Need to evaluate Tesseract vs cloud APIs when ready for Phase 3
- **Print template requirements:** Need to understand what "printable format" means to end users
