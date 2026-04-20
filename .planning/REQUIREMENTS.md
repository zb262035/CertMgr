# Requirements: CertMgr / 需求：CertMgr

**Defined / 定义:** 2026-03-19
**Core Value / 核心价值:** Faculty/staff certificate assets are safe, accessible, and traceable. / 教职工的证书资产安全、便捷、可追溯。

---

## v1 Requirements / v1 需求

Requirements for initial release. Each maps to roadmap phases. / 初始版本的需求。每个需求映射到路线图阶段。

### Authentication / 认证

- [x] **AUTH-01**: User can register account with email and password / 用户可以使用邮箱和密码注册账户
- [x] **AUTH-02**: Auth adapter interface - pluggable architecture for SSO integration / 认证适配器接口 - SSO集成可插拔架构

### Certificate Management / 证书管理

- [x] **CERT-01**: User can upload electronic certificate file / 用户可以上传电子证书文件
- [x] **CERT-02**: User can capture and upload photo of paper certificate / 用户可以拍摄并上传纸质证书照片
- [x] **CERT-03**: System stores certificate files with UUID-based paths / 系统使用UUID路径存储证书文件
- [x] **CERT-04**: Certificate records support dynamic fields per type / 证书记录支持每种类型的动态字段
- [x] **CERT-05**: Admin can manually add/edit/delete any certificate / 管理员可以手动添加/编辑/删除任何证书
- [x] **CERT-06**: Admin can batch import certificates from Excel / 管理员可以从Excel批量导入证书
- [x] **CERT-07**: User can search certificates by name, type, date, issuer / 用户可以按姓名/类型/日期/颁发机构搜索
- [x] **CERT-08**: User can filter certificates by multiple conditions / 用户可以按多个条件筛选证书
- [x] **CERT-09**: System displays statistics dashboard / 系统显示统计面板
- [ ] **CERT-10**: User can export certificate as printable PDF / 用户可以导出为可打印PDF
- [x] **CERT-11**: Permission control - users vs admins / 权限控制 - 用户vs管理员

---

## v1.1 Requirements / v1.1 需求

Certificate list Excel export feature / 证书列表Excel导出功能

### Report Export / 报表导出

- [ ] **RPT-01**: 用户可在证书列表页导出当前筛选结果的证书清单
- [ ] **RPT-02**: 导出包含：标题、持有人、部门、证书类型、获奖日期、颁发机构、创建时间等字段
- [ ] **RPT-03**: 导出文件名为 `证书清单_YYYYMMDD_HHmmss.xlsx`
- [ ] **RPT-04**: 支持导出全部证书或按筛选条件导出
- [ ] **RPT-05**: 管理员可导出所有证书，普通用户只能导出自己的

---

## v2 Requirements / v2 需求

Deferred to future release. / 延至未来版本。

### OCR & Advanced / OCR 与高级功能

- **OCR-01**: System auto-extracts text from certificate photo / 系统使用OCR从证书照片自动提取文字
- **AUDIT-01**: System logs audit trail / 系统记录审计日志

### SSO Integration / SSO 集成

- **SSO-01**: Integrate with school OA system / 与学校OA系统集成
- **SSO-02**: Integrate with Enterprise WeChat / 与企业微信集成
- **SSO-03**: Integrate with CAS / 与CAS集成

---

## Out of Scope / 超出范围

| Feature / 功能 | Reason / 原因 |
|---------------|--------------|
| Certificate authenticity verification / 证书真伪验证 | Requires third-party authority / 需要第三方权威机构 |
| Approval workflow / 审批流程 | Explicitly excluded / 明确排除 |
| Native mobile app / 原生移动应用 | Responsive web covers mobile / 响应式Web覆盖移动用例 |

---

## Traceability / 可追溯性

| Requirement / 需求 | Phase / 阶段 | Status / 状态 |
|---------------------|--------------|--------------|
| AUTH-01 | Phase 1 | ✅ Complete |
| AUTH-02 | Phase 1 | ✅ Complete |
| CERT-03 | Phase 1 | ✅ Complete |
| CERT-11 | Phase 1 | ✅ Complete |
| CERT-01 | Phase 2 | ✅ Complete |
| CERT-02 | Phase 2 | ✅ Complete |
| CERT-04 | Phase 2 | ✅ Complete |
| CERT-05 | Phase 2 | ✅ Complete |
| CERT-06 | Phase 2 | ✅ Complete |
| CERT-07 | Phase 2 | ✅ Complete |
| CERT-08 | Phase 2 | ✅ Complete |
| CERT-09 | Phase 2 | ✅ Complete |
| CERT-10 | Phase 3 | Pending |
| RPT-01 | Phase 6 | Pending |
| RPT-02 | Phase 6 | Pending |
| RPT-03 | Phase 6 | Pending |
| RPT-04 | Phase 6 | Pending |
| RPT-05 | Phase 6 | Pending |

---

*Requirements defined / 需求定义: 2026-03-19*
*Last updated / 最后更新: 2026-04-20 after v1.1 milestone started*
