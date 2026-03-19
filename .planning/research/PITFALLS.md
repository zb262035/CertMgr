# Domain Pitfalls: School Certificate Management System

**Domain:** Education certificate management (Chinese school context)
**Researched:** 2026-03-19
**Confidence:** MEDIUM (knowledge-based; WebSearch unavailable for verification)

## Critical Pitfalls

Mistakes that cause data loss, rewrites, or system failures.

---

### Pitfall 1: File Storage Without UUID Naming

**What goes wrong:** Original filenames preserved (e.g., `成绩单_张三_2024.pdf`, `Certificate_John.pdf`). When duplicates exist or characters get corrupted, files overwrite or become inaccessible.

**Why it happens:** Developers preserve original names for user friendliness. Chinese filenames contain characters that may be illegal on some filesystems or get mangled during transfer.

**Consequences:**
- File collisions overwrite existing certificates
- Characters garbled in storage paths (especially across OS boundaries)
- Backup/restore produces inconsistent results
- Antivirus false positives on files with certain Chinese characters in names

**Prevention:**
- Always rename on ingest: `{uuid4()}.{extension}`
- Store original filename in database metadata column
- Use filesystem-unsafe characters stripping on all uploads

**Warning signs:**
- Files disappearing after upload
- "File not found" errors for existing records
- Backup size inconsistent with record count

**Phase:** Phase 2 (Core Infrastructure) - must implement before any upload functionality

---

### Pitfall 2: No Incremental Backup Strategy

**What goes wrong:** Daily full backups exhaust server disk space within months. Backups fail silently due to size. Recovery takes hours.

**Why it happens:** Certificate files are large (~100KB-2MB each). At 1000 users with multiple certificates, 10GB+ storage fills quickly.

**Consequences:**
- Disk full errors halt operations
- Failed backups unnoticed until disaster recovery needed
- Long recovery time from full backups
- Potential data loss between backup intervals

**Prevention:**
- Implement incremental backup: full weekly, incremental daily (new files only)
- Store file checksums in database to verify backup integrity
- Use dedicated backup volume separate from application storage
- Test restore quarterly

**Warning signs:**
- Backup jobs failing with "no space left"
- Backup times increasing linearly with record count
- No monitoring/alerting on backup success

**Phase:** Phase 2 (Core Infrastructure) - backup strategy before production deployment

---

### Pitfall 3: Dynamic Certificate Fields as Hardcoded Columns

**What goes wrong:** New certificate types require schema migration. Each school has different fields (awards, transcripts, attendance). Code becomes field-specific conditionals.

**Why it happens:** Initial schema design uses fixed columns: `student_name`, `course_name`, `score`, `date`. When school needs custom fields, migrations proliferate.

**Consequences:**
- Schema migrations lock tables (SQLite especially problematic)
- Each new certificate type requires code change
- Conditional display logic pollutes templates
- EAV (Entity-Attribute-Value) anti-pattern emerges

**Prevention:**
- Use JSON/JSONB column for certificate-specific data alongside fixed fields
- Define certificate type templates in database (not code)
- Store field definitions: `{name, type, required, validation}`
- Use document storage pattern for the dynamic payload

**Recommended schema:**
```sql
certificates (
    id UUID PRIMARY KEY,
    student_id FK,
    certificate_type_id FK,
    issued_at TIMESTAMP,
    -- Fixed fields
    serial_number VARCHAR(50),
    status VARCHAR(20),
    -- Dynamic payload as JSONB
    payload JSONB,
    created_at, updated_at
)

certificate_types (
    id,
    name,
    template JSONB  -- field definitions
)
```

**Warning signs:**
- Frequent ALTER TABLE statements
- `if cert_type == 'transcript': show_field('gpa')` in templates
- Different certificate types require different create forms

**Phase:** Phase 1 (Schema Design) - fundamental architecture decision

---

### Pitfall 4: Unicode Normalization Inconsistency

**What goes wrong:** Chinese characters like "李" vs "李" (different Unicode representations) compare as different. Search for "李明" returns nothing because stored as composed vs decomposed form.

**Why it happens:** Python/Flask handles Unicode, but database collation, file system, and PDF libraries may normalize differently. iOS/Android clients may submit NFC vs NFD forms.

**Consequences:**
- Duplicate student records for same person
- Search returns incomplete results
- PDF generation produces garbled characters
- Data migration corrupts character data

**Prevention:**
- Normalize all text input to NFC on ingestion (Python: `unicodedata.normalize('NFC', text)`)
- Set database collation to UTF-8 binary or NFC-aware
- Verify PDF font supports all CJK Unified Ideographs
- Document normalization standard in onboarding

**Warning signs:**
- `len(set([name, name])) > 1` for identical-seeming names
- Search results vary by how query was typed
- Font missing glyph warnings in PDF generation

**Phase:** Phase 1 (Schema Design) - normalization at data entry points

---

### Pitfall 5: No File Size Validation at Application Layer

**What goes wrong:** Large uploads (videos, high-res scans) exhaust server resources. nginx/Flask connection drops, leaving partial files.

**Why it happens:** Default Flask limit is 16MB, but config often set to 0 (unlimited) or 500MB. File upload to temp directory first.

**Consequences:**
- Server disk full from temp files
- Denial of service from large uploads
- Partial files accepted as complete
- Memory exhaustion on 32-bit systems

**Prevention:**
- Set explicit limits: `MAX_CONTENT_LENGTH = 16 * 1024 * 1024` (16MB) or reasonable for PDFs
- Validate file size in route before saving: check `Content-Length` header
- Stream large files to disk, never memory
- Clean temp directory on schedule

**For PDFs specifically:**
- 300KB-2MB is typical for certificate PDFs
- Larger suggests scanning instead of generated PDF
- Reject >10MB individual files

**Warning signs:**
- Server response time increases with uploads
- `/tmp` directory growing large
- Memory usage spiking during uploads

**Phase:** Phase 2 (Core Infrastructure) - before any upload endpoint

---

### Pitfall 6: RBAC Without Role Hierarchy

**What goes wrong:** Teachers can delete certificates. Admins accidentally modify student records. No distinction between certificate issuance vs verification permissions.

**Why it happens:** Simple boolean permissions: `can_edit = True`. No distinction between certificate creation, approval, and viewing.

**Consequences:**
- Privilege escalation: teacher grants themselves admin
- Audit log meaningless without granular actions
- Cannot delegate temporary access for substitutes
- Compliance issues for academic records

**Prevention:**
- Design permission matrix before coding:
  - **Admin:** all operations, user management, system config
  - **Registrar:** create, issue, revoke certificates
  - **Teacher:** view, verify (no create/modify)
  - **Student:** view own certificates only
- Use Flask-Principal or similar for permission system
- All sensitive operations require audit log entry
- Separate authentication (who) from authorization (what)

**Warning signs:**
- "admin" role has 50+ permissions
- Same account used by multiple people
- No way to revoke access without deleting account

**Phase:** Phase 1 (Schema Design) - permission model before business logic

---

### Pitfall 7: Full-Table Scan for Certificate Search

**What goes wrong:** Search by student name takes 10+ seconds on 10,000 certificates. Pagination breaks. UI unresponsive.

**Why it happens:** `LIKE '%name%'` on payload JSONB column. No index on searchable fields.

**Consequences:**
- Timeouts on search requests
- Database CPU maxed during peak hours
- Cannot support autocomplete/suggest
- Pagination returns inconsistent results

**Prevention:**
- Create indexes on: `serial_number`, `student_id`, `certificate_type_id`, `issued_at`, `status`
- For JSONB payload search: use GIN index + `->>` operator
- Consider PostgreSQL full-text search for Chinese text
- Implement result caching for common searches

**For SQLite:** Limited index options. Use FTS5 extension for full-text search:
```sql
CREATE VIRTUAL TABLE certificates_fts USING fts5(
    student_name,
    certificate_type,
    content='certificates',
    content_rowid='id'
);
```

**Warning signs:**
- Search page takes >3 seconds to load
- `EXPLAIN QUERY PLAN` shows SCAN TABLE
- Database CPU >80% during business hours

**Phase:** Phase 2 (Core Infrastructure) - indexing strategy before query optimization

---

### Pitfall 8: PDF Generation Tightly Coupled to Business Logic

**What goes wrong:** Changing certificate template requires code deployment. PDF library version breaks existing templates. Chinese fonts render as boxes on different systems.

**Why it happens:** PDF generation inline in routes. Template HTML embedded in Python strings. Font files not bundled properly.

**Consequences:**
- Cannot customize templates per school without deploy
- PDF output varies by server font availability
- Testing PDF requires running full application
- Breaking changes in library version affect all templates

**Prevention:**
- Separate PDF generation into standalone service/module
- Store templates as files (Jinja2 HTML templates)
- Bundle required fonts in application, reference by absolute path
- Use WeasyPrint (HTML/CSS to PDF) or ReportLab
- For Chinese fonts: include `Noto Sans CJK` or similar bundled font
- Test PDF output in CI pipeline

**Chinese font recommendation:**
- Bundle: Noto Sans SC (Google Fonts), Source Han Sans (Adobe)
- Embed fonts in PDF: `font-face: 'Noto Sans SC'` in CSS
- Verify: open PDF in OS-native viewer, not just browser

**Warning signs:**
- PDF templates have if/else logic for different schools
- "Font not found" errors in production logs
- Different PDF output on different servers

**Phase:** Phase 3 (Certificate Generation) - template architecture before implementation

---

### Pitfall 9: School Server Windows/IIS Assumptions

**What goes wrong:** Code works on developer Mac, fails on Windows server. File path separators wrong. Permission denied on uploads. Path length >260 characters.

**Why it happens:** Hardcoded Unix paths. Assumptions about filesystem case sensitivity. IIS handles authentication differently.

**Consequences:**
- Deployment failures
- File upload works, storage fails silently
- Path traversal vulnerabilities if user input in paths
- Chinese characters in paths break on Windows

**Prevention:**
- Use `pathlib` for all file operations (works cross-platform)
- Never construct paths from user input
- Test deployment on target OS (Windows Server is common in Chinese schools)
- Use environment variables for base paths, not hardcoded strings
- Keep paths short and ASCII where possible

**Windows-specific:**
```python
from pathlib import Path
UPLOAD_FOLDER = Path(os.environ.get('UPLOAD_FOLDER', 'C:/certificates'))
# Use forward slash or Path.absolute() for Windows compatibility
```

**Warning signs:**
- Works on development, fails on production
- "Permission denied" errors only in production
- File not found errors with Chinese filenames

**Phase:** Phase 2 (Core Infrastructure) - deployment target identified before coding

---

### Pitfall 10: No Audit Trail for Certificate Changes

**What goes wrong:** Student claims certificate was modified. No way to prove otherwise. Diploma forgery goes undetected. Compliance audit fails.

**Why it happens:** Certificate updates modify records in place. No history retained. No signing/verification of document integrity.

**Consequences:**
- Cannot detect tampering after issuance
- No evidence for disputes
- Regulatory compliance failure
- Cannot identify who made changes

**Prevention:**
- Append-only log for certificate lifecycle:
  ```sql
  certificate_audit (
      id, certificate_id, action, actor_id,
      old_values JSONB, new_values JSONB,
      timestamp, ip_address
  )
  ```
- Actions: `created`, `issued`, `revoked`, `viewed`, `verified`
- Sign certificates with hash (SHA-256) stored separately
- Consider blockchain-style chaining: each certificate stores hash of previous

**Digital signature approach:**
```python
import hashlib
certificate_data = f"{serial_number}:{student_id}:{issued_at}:{payload_hash}"
signature = hmac(key, certificate_data.encode()).hexdigest()
```

**Warning signs:**
- "Last modified" column shows current timestamp for old records
- No way to query who viewed a specific certificate
- Audit reports require manual investigation

**Phase:** Phase 1 (Schema Design) - audit requirements before data model

---

## Moderate Pitfalls

Issues that cause operational problems but can be recovered.

---

### Pitfall 11: Session Management Without Timeout

**What goes wrong:** Shared computers in computer labs. Previous student's certificates visible to next user. Session hijacking possible.

**Prevention:**
- Implement session timeout (30 min inactivity)
- Clear session on browser close (session cookie, not persistent)
- CSRF protection on all state-changing requests
- Consider fingerprinting for suspicious session reuse

**Phase:** Phase 2 (Core Infrastructure)

---

### Pitfall 12: Export Functionality Loads Entire Dataset to Memory

**What goes wrong:** Bulk export of 10,000 certificates causes memory error. ZIP generation fails. Export times out.

**Prevention:**
- Stream exports using generators
- Use disk-based temporary files for large exports
- Chunk exports: 1000 records per file
- Background job for large exports with email notification

**Phase:** Phase 3 (Features)

---

### Pitfall 13: Database Connection Pool Exhaustion

**What goes wrong:** Many concurrent users exhaust SQLite connections. PostgreSQL pool exhausted under load.

**Why it happens:** SQLite has single-writer limitation. Flask debug mode holds connections. Long-running queries block new requests.

**Prevention:**
- SQLite: use WAL mode, connection per request closed properly
- PostgreSQL: set pool size to 2x CPU cores, timeout on acquire
- Use `with g.db.cursor()` pattern, always close
- Monitor connection count in production

**Phase:** Phase 2 (Core Infrastructure)

---

### Pitfall 14: Timezone Mismatch on Certificate Dates

**What goes wrong:** Certificate shows issued date from previous day when viewed in different timezone. Timestamp math errors.

**Prevention:**
- Store all timestamps as UTC
- Store issuer's timezone separately if needed
- Display in user's local timezone
- Use `pytz` or Python 3.9+ `zoneinfo` for conversions
- Test across China timezone (UTC+8)

**Phase:** Phase 1 (Schema Design)

---

## Minor Pitfalls

Operational inconveniences that don't cause failures.

---

### Pitfall 15: No Serial Number Format Standardization

**Problem:** Serial numbers like "CERT-2024-001", "2024001", "第2024001号" all in same system.

**Prevention:** Define format standard: `{PREFIX}-{YEAR}{SEQ:06d}` e.g., `CERT-2024000001`

**Phase:** Phase 1 (Schema Design)

---

### Pitfall 16: Missing Graceful Degradation for PDF Viewing

**Problem:** Browser blocks PDF embeds. Mobile devices can't view inline PDFs.

**Prevention:**
- Always provide download link, not just embed
- Test on common browsers used in schools (360, QQ, WeChat built-in)
- Offer alternative format (PNG image) if PDF fails

**Phase:** Phase 3 (Features)

---

## Phase-Specific Warnings

| Phase | High-Risk Pitfalls | Mitigation |
|-------|-------------------|------------|
| **Phase 1: Schema Design** | Dynamic fields (EAV), RBAC, audit trail, normalization, timezone | Architecture review before implementation |
| **Phase 2: Core Infrastructure** | File storage UUID, backup, file size limits, connection pooling, server OS | Integration testing on target deployment environment |
| **Phase 3: Features** | PDF generation, search performance, export streaming | Load testing with production-like data volume |
| **Phase 4: Polish** | Session security, export timeouts | Security audit, performance testing |

---

## Research Notes

**Confidence assessment:**
- File storage/RBAC/backup pitfalls: HIGH confidence (well-documented patterns)
- Chinese encoding specifics: MEDIUM confidence (requires production verification)
- PDF generation Chinese fonts: MEDIUM confidence (font availability changes)
- School server environment: MEDIUM confidence (varies by institution)

**Unable to verify with current sources** due to WebSearch API unavailability. Recommend Phase 1 architecture review to validate against actual school IT environment.

**Topics requiring deeper research:**
- Actual school server OS distribution (Windows vs Linux)
- Network file system (NFS) usage for shared storage
- Specific Chinese PDF font licensing requirements
- Provincial education bureau certificate format requirements

---

## Sources

_Primary sources unavailable (WebSearch API error). Findings based on:_
- Flask documentation on file handling
- PostgreSQL JSONB best practices
- Unicode normalization standards (UTR #15)
- OWASP security guidelines for RBAC
- WeasyPrint/ReportLab Chinese font integration
- Windows Server file path limitations (MAX_PATH 260)
