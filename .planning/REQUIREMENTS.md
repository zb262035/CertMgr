# Requirements: CertMgr

**Defined:** 2026-03-19
**Core Value:** Faculty/staff certificate assets are safe, accessible, and traceable.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Authentication

- [ ] **AUTH-01**: User can register account with email and password
- [ ] **AUTH-02**: Auth adapter interface - pluggable architecture for SSO integration (OA/企业微信/统一身份认证)

### Certificate Management

- [ ] **CERT-01**: User can upload electronic certificate file (image/PDF)
- [ ] **CERT-02**: User can capture and upload photo of paper certificate
- [ ] **CERT-03**: System stores certificate files in local filesystem with UUID-based paths
- [ ] **CERT-04**: Certificate records support dynamic fields per certificate type
- [ ] **CERT-05**: Admin can manually add/edit/delete any certificate
- [ ] **CERT-06**: Admin can batch import certificates from Excel file
- [ ] **CERT-07**: User can search certificates by name, type, date, issuer
- [ ] **CERT-08**: User can filter certificates by multiple conditions (time range, type, etc.)
- [ ] **CERT-09**: System displays statistics: certificate counts by type, trends over time
- [ ] **CERT-10**: User can export certificate as printable PDF format
- [ ] **CERT-11**: Permission control - users can only view/edit their own certificates, admins can view/edit all

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### OCR & Advanced

- **OCR-01**: System auto-extracts text from certificate photo using OCR
- **AUDIT-01**: System logs audit trail (who created/modified/deleted certificates)

### SSO Integration

- **SSO-01**: Integrate with school OA system
- **SSO-02**: Integrate with Enterprise WeChat (企业微信)
- **SSO-03**: Integrate with CAS (Central Authentication Service)

### Additional

- **STATS-02**: Export statistics as report
- **ALERT-01**: Alert when certificates expire

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Certificate authenticity verification | Requires third-party authority partnership |
| Approval workflow | Explicitly excluded per PROJECT.md |
| Native mobile app | Responsive web covers mobile use cases |
| Third-party API integration | v2+ only |
| Blockchain verification | Overengineered for internal use |
| Multi-tenancy | Single school deployment |

## Traceability

Which phases cover which requirements.

| Requirement | Phase | Status |
|-------------|-------|--------|
| AUTH-01 | Phase 1 | Pending |
| AUTH-02 | Phase 1 | Pending |
| CERT-03 | Phase 1 | Pending |
| CERT-11 | Phase 1 | Pending |
| CERT-01 | Phase 2 | Pending |
| CERT-02 | Phase 2 | Pending |
| CERT-04 | Phase 2 | Pending |
| CERT-05 | Phase 2 | Pending |
| CERT-06 | Phase 2 | Pending |
| CERT-07 | Phase 2 | Pending |
| CERT-08 | Phase 2 | Pending |
| CERT-09 | Phase 2 | Pending |
| CERT-10 | Phase 3 | Pending |
| OCR-01 | Phase 3 | Pending |
| AUDIT-01 | Phase 3 | Pending |

**Coverage:**
- v1 requirements: 13 total
- Mapped to phases: 13
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-19*
*Last updated: 2026-03-19 after roadmap creation*
