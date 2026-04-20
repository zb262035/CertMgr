# Roadmap: CertMgr / 路线图：CertMgr

## Overview / 总览

CertMgr is a school certificate management system. The journey spans multiple phases: foundation, core features, enhancements, and v1.1 Excel export.

## Phase Summary / 阶段概览

| # | Phase | Goal | Status |
|---|-------|------|--------|
| 1 | Foundation / 基础架构 | Flask app factory, models, auth, file storage | ✅ Complete |
| 2 | Core / 核心功能 | Certificate CRUD, search, filter, stats | ✅ Complete |
| 3 | Enhancement / 增强功能 | PDF export, SSO, audit, OCR | Pending |
| 6 | Excel 导出功能 | Certificate list Excel export | Pending |

## Phase Details / 阶段详情

### Phase 1: Foundation / 基础架构

**Goal / 目标**: Application infrastructure / 应用基础设施

**Requirements / 需求**: AUTH-01, AUTH-02, CERT-03, CERT-11

**Success Criteria / 成功标准**: 11 criteria met

**Status**: ✅ Completed 2026-03-19

---

### Phase 2: Core / 核心功能

**Goal / 目标**: Full certificate management / 完整证书管理

**Requirements / 需求**: CERT-01 ~ CERT-09

**Status**: ✅ Completed 2026-03-24

---

### Phase 3: Enhancement / 增强功能

**Goal / 目标**: Advanced features / 高级功能

**Requirements / 需求**: CERT-10, OCR-01, AUDIT-01

**Status**: Not started / 未开始

---

### Phase 6: Excel 导出功能

**Goal / 目标**: Certificate list Excel export / 证书列表Excel导出

**Requirements / 需求**: RPT-01, RPT-02, RPT-03, RPT-04, RPT-05

**Success Criteria / 成功标准** (what must be TRUE / 必须满足):

1. 用户可在证书列表页点击导出按钮
2. 导出 Excel 包含正确字段（标题、持有人、部门、类型、日期、颁发机构、创建时间）
3. 文件名格式为 `证书清单_YYYYMMDD_HHmmss.xlsx`
4. 支持当前筛选条件导出
5. 权限正确：管理员导出全部，用户只导出自己的

**Implementation Notes / 实现备注**:
- 使用 openpyxl 库生成 .xlsx 文件
- 后端 API: GET /certificates/api/export
- 前端: 在证书列表页添加导出按钮
- 使用现有 DataTables 筛选条件

**Status**: Not started / 未开始

---

## Progress / 进度

| Phase / 阶段 | Status / 状态 | Completed / 完成 |
|--------------|---------------|------------------|
| 1. Foundation | ✅ Complete | 2026-03-19 |
| 2. Core | ✅ Complete | 2026-03-24 |
| 3. Enhancement | Not started | - |
| 6. Excel Export | Not started | - |

---

## Coverage / 覆盖率

**Requirements mapped to phases / 需求映射到阶段:**

| Requirement | Phase | Description |
|-------------|-------|-------------|
| AUTH-01, AUTH-02 | Phase 1 | Authentication |
| CERT-03, CERT-11 | Phase 1 | Storage & Permission |
| CERT-01~CERT-09 | Phase 2 | Certificate CRUD & Stats |
| CERT-10, OCR-01, AUDIT-01 | Phase 3 | Enhancement |
| RPT-01~RPT-05 | Phase 6 | Excel Export |

**Coverage / 覆盖率:** 13 + 5 v1.1 requirements mapped / 需求已映射 ✓

---

*Roadmap created / 路线图创建: 2026-03-19*
*Last updated / 最后更新: 2026-04-20 after v1.1 milestone started*
