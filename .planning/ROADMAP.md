# Roadmap: CertMgr / 路线图：CertMgr

## Overview / 总览

CertMgr is a school certificate management system that enables faculty/staff to digitize and manage their certificates (competition awards, honors, qualifications, vocational skills). The journey spans three phases: building the Flask application foundation with authentication and file storage, implementing certificate CRUD with search/statistics, and adding PDF export, SSO integration, and advanced features.

CertMgr 是一个学校证书管理系统，使教职工能够数字化和管理他们的证书（竞赛获奖、荣誉、资格、职业证书等）。整个过程分为三个阶段：构建 Flask 应用基础设施（认证和文件存储）、实现证书 CRUD 与搜索统计、以及 PDF 导出、SSO 集成和高级功能。

## Phases / 阶段

- [ ] **Phase 1: Foundation / 基础架构** - Flask app factory, models, local auth, file storage, permission control / Flask 应用工厂、数据模型、本地认证、文件存储、权限控制
- [x] **Phase 2: Core / 核心功能** - Certificate CRUD, dynamic fields, upload/download, batch import, search, filter, stats, OCR / 证书 CRUD、动态字段、上传下载、批量导入、搜索、筛选、统计、OCR (completed 2026-03-24, OCR added 2026-03-24)
- [ ] **Phase 3: Enhancement / 增强功能** - PDF export, SSO integration, audit trail / PDF 导出、SSO 集成、审计日志

## Phase Details / 阶段详情

### Phase 1: Foundation / 基础架构

**Goal / 目标**: Application infrastructure enabling all subsequent work / 为后续所有工作奠定应用基础设施

**Depends on / 依赖**: Nothing (first phase) / 无（第一阶段）

**Requirements / 需求**: AUTH-01, AUTH-02, CERT-03, CERT-11

**Waves / 波次**:

| Wave | 内容 / Content | 状态 / Status |
|------|---------------|---------------|
| Wave 1 | Flask 项目结构、User 模型、extensions | ✅ 已完成 |
| Wave 2 | 认证模块（注册/登录/登出） | ✅ 已完成 |
| Wave 3 | 文件存储服务、权限装饰器 | ✅ 已完成 |

**Success Criteria / 成功标准** (what must be TRUE / 必须满足):

1. User can register account with email and password / 用户可以使用邮箱和密码注册账户
2. User can log in and stay logged in across browser sessions / 用户可以登录并在浏览器会话间保持登录状态
3. User can log out from any page / 用户可以从任何页面登出
4. Admin can view all user accounts in the system / 管理员可以查看系统中所有用户账户
5. Users can only view and edit their own certificates (permission enforced) / 用户只能查看和编辑自己的证书（权限强制执行）
6. Certificate files are stored with UUID-based paths (no original filenames in storage) / 证书文件使用 UUID 路径存储（存储中不保留原始文件名）
7. File upload/download respects permission boundaries / 文件上传/下载遵守权限边界
8. All operations provide user feedback via flash messages / 所有操作通过 flash 消息向用户提供反馈
9. Navigation allows users to access all pages from any location / 导航允许用户从任何位置访问所有页面
10. Admin can enable/disable users, reset passwords / 管理员可以启用/禁用用户、重置密码
11. Users can change their own password / 用户可以修改自己的密码

**Plans / 计划**: 3 plans (completed)

---

### Phase 2: Core / 核心功能

**Goal / 目标**: Full certificate management with search and statistics / 完整的证书管理与搜索统计

**Depends on / 依赖**: Phase 1 / 第一阶段

**Requirements / 需求**: CERT-01, CERT-02, CERT-04, CERT-05, CERT-06, CERT-07, CERT-08, CERT-09

**Success Criteria / 成功标准** (what must be TRUE / 必须满足):

1. User can upload certificate file (image/PDF) and associate with their account / 用户可以上传证书文件（图片/PDF）并关联到自己的账户
2. User can capture photo of paper certificate and upload it / 用户可以拍摄纸质证书照片并上传
3. User can view list of their own certificates with pagination / 用户可以查看自己的证书列表并分页
4. User can edit their own certificate metadata (title, issuer, date, dynamic fields) / 用户可以编辑自己的证书元数据（标题、颁发机构、日期、动态字段）
5. User can delete their own certificates / 用户可以删除自己的证书
6. Different certificate types display different dynamic fields in forms / 不同证书类型在表单中显示不同的动态字段
7. User can search certificates by holder name / 用户可以按持有人姓名搜索证书
8. User can filter certificates by type, date range, and issuer / 用户可以按类型、日期范围和颁发机构筛选证书
9. Admin can view all certificates in the system / 管理员可以查看系统中所有证书
10. Admin can manually add/edit/delete any certificate / 管理员可以手动添加/编辑/删除任何证书
11. Admin can batch import certificates from Excel file / 管理员可以批量从 Excel 文件导入证书
12. Admin can view statistics: certificate counts by type, trends over time / 管理员可以查看统计：各类型证书数量、时间趋势

**Plans / 计划**: 3 plans in 3 waves

Plans:
- [x] 02-01-PLAN.md — Wave 1: Certificate model + CRUD routes + card templates ✅
- [x] 02-02-PLAN.md — Wave 2: DataTables API + search/filter + Excel batch import ✅
- [x] 02-03-PLAN.md — Wave 3: Statistics dashboard with Chart.js ✅
- [x] 02-04-PLAN.md.deferred — OCR certificate entry (PaddleOCR效果不佳，移至Phase 3)

---

### Phase 3: Enhancement / 增强功能

**Goal / 目标**: Advanced features and integrations / 高级功能和集成

**Depends on / 依赖**: Phase 2 / 第二阶段

**Requirements / 需求**: AUTH-02 (SSO component / SSO 组件), CERT-10, OCR-01, AUDIT-01

**Success Criteria / 成功标准** (what must be TRUE / 必须满足):

1. User can export certificate as printable PDF with Chinese text / 用户可以导出带有中文的可打印 PDF 证书
2. System supports SSO integration via pluggable auth adapter (OA/WeChat Work/CAS) / 系统通过可插拔认证适配器支持 SSO 集成（OA/企业微信/CAS）
3. System logs audit trail: who created/modified/deleted certificates / 系统记录审计日志：谁创建/修改/删除了证书
4. User can upload certificate and system auto-extracts text using OCR (improved) / 用户可以上传证书，系统使用OCR自动提取文字（改进版）

**Plans / 计划**: TBD / 待定

---

## Progress / 进度

| Phase / 阶段 | Plans Complete / 计划完成 | Status / 状态 | Completed / 完成 |
|--------------|---------------------------|---------------|-----------------|
| 1. Foundation / 基础架构 | 3/3 | ✅ Complete / 已完成 | 2026-03-19 |
| 2. Core / 核心功能 | 4/4 | ✅ Complete / 已完成 | 2026-03-24 |
| 3. Enhancement / 增强功能 | 0/TBD | Not started / 未开始 | - |

---

## Coverage / 覆盖率

**Requirements mapped to phases / 需求映射到阶段:**

| Requirement / 需求 | Phase / 阶段 | Description / 描述 |
|---------------------|--------------|-------------------|
| AUTH-01 | Phase 1 | Account management (local auth) / 账户管理（本地认证） |
| AUTH-02 | Phase 1 | Auth adapter interface (pluggable SSO) / 认证适配器接口（可插拔SSO） |
| CERT-03 | Phase 1 | File storage (local filesystem) / 文件存储（本地文件系统） |
| CERT-11 | Phase 1 | Permission control (user vs admin) / 权限控制（用户vs管理员） |
| CERT-01 | Phase 2 | Upload electronic certificate / 上传电子证书 |
| CERT-02 | Phase 2 | Upload photo of paper certificate / 上传纸质证书照片 |
| CERT-04 | Phase 2 | Dynamic fields per certificate type / 每种证书类型的动态字段 |
| CERT-05 | Phase 2 | Admin manual entry/edit / 管理员手动录入/编辑 |
| CERT-06 | Phase 2 | Batch import from Excel / 从Excel批量导入 |
| CERT-07 | Phase 2 | Search by name/type/date/issuer / 按姓名/类型/日期/颁发机构搜索 |
| CERT-08 | Phase 2 | Multi-filter search / 多条件筛选搜索 |
| CERT-09 | Phase 2 | Statistics dashboard / 统计面板 |
| OCR-01 | Phase 3 | Auto-extract text from certificate photo / 从证书照片自动提取文字 |
| CERT-10 | Phase 3 | Export to printable PDF / 导出为可打印PDF |
| AUDIT-01 | Phase 3 | Audit trail for certificate changes / 证书变更审计日志 |

**Coverage / 覆盖率:** 15/15 v1 requirements mapped / 15/15 v1 需求已映射 ✓
**Out of scope / 超出范围:** 5 items (see PROJECT.md / 见 PROJECT.md)
