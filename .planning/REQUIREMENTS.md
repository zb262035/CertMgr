# Requirements: CertMgr / 需求：CertMgr

**Defined / 定义:** 2026-03-19
**Core Value / 核心价值:** Faculty/staff certificate assets are safe, accessible, and traceable. / 教职工的证书资产安全、便捷、可追溯。

---

## v1 Requirements / v1 需求

Requirements for initial release. Each maps to roadmap phases. / 初始版本的需求。每个需求映射到路线图阶段。

### Authentication / 认证

- [ ] **AUTH-01**: User can register account with email and password / 用户可以使用邮箱和密码注册账户
- [ ] **AUTH-02**: Auth adapter interface - pluggable architecture for SSO integration (OA/企业微信/统一身份认证) / 认证适配器接口 - 用于 SSO 集成的可插拔架构（OA/企业微信/统一身份认证）

### Certificate Management / 证书管理

- [ ] **CERT-01**: User can upload electronic certificate file (image/PDF) / 用户可以上传电子证书文件（图片/PDF）
- [ ] **CERT-02**: User can capture and upload photo of paper certificate / 用户可以拍摄并上传纸质证书照片
- [ ] **CERT-03**: System stores certificate files in local filesystem with UUID-based paths / 系统使用 UUID 路径在本地文件系统存储证书文件
- [ ] **CERT-04**: Certificate records support dynamic fields per certificate type / 证书记录支持每种证书类型的动态字段
- [ ] **CERT-05**: Admin can manually add/edit/delete any certificate / 管理员可以手动添加/编辑/删除任何证书
- [ ] **CERT-06**: Admin can batch import certificates from Excel file / 管理员可以从 Excel 文件批量导入证书
- [ ] **CERT-07**: User can search certificates by name, type, date, issuer / 用户可以按姓名、类型、日期、颁发机构搜索证书
- [ ] **CERT-08**: User can filter certificates by multiple conditions (time range, type, etc.) / 用户可以按多个条件（时间范围、类型等）筛选证书
- [ ] **CERT-09**: System displays statistics: certificate counts by type, trends over time / 系统显示统计：各类型证书数量、时间趋势
- [ ] **CERT-10**: User can export certificate as printable PDF format / 用户可以导出为可打印 PDF 格式的证书
- [ ] **CERT-11**: Permission control - users can only view/edit their own certificates, admins can view/edit all / 权限控制 - 用户只能查看/编辑自己的证书，管理员可以查看/编辑所有证书

---

## v2 Requirements / v2 需求

Deferred to future release. Tracked but not in current roadmap. / 延至未来版本。已跟踪但不在当前路线图中。

### OCR & Advanced / OCR 与高级功能

- **OCR-01**: System auto-extracts text from certificate photo using OCR / 系统使用 OCR 从证书照片自动提取文字
- **AUDIT-01**: System logs audit trail (who created/modified/deleted certificates) / 系统记录审计日志（谁创建/修改/删除了证书）

### SSO Integration / SSO 集成

- **SSO-01**: Integrate with school OA system / 与学校 OA 系统集成
- **SSO-02**: Integrate with Enterprise WeChat (企业微信) / 与企业微信集成
- **SSO-03**: Integrate with CAS (Central Authentication Service) / 与 CAS（集中认证服务）集成

### Additional / 额外功能

- **STATS-02**: Export statistics as report / 导出统计为报告
- **ALERT-01**: Alert when certificates expire / 证书过期时提醒

---

## Out of Scope / 超出范围

Explicitly excluded. Documented to prevent scope creep. / 明确排除。记录在案以防止范围蔓延。

| Feature / 功能 | Reason / 原因 |
|---------------|--------------|
| Certificate authenticity verification / 证书真伪验证 | Requires third-party authority partnership / 需要第三方权威机构合作 |
| Approval workflow / 审批流程 | Explicitly excluded per PROJECT.md / 根据 PROJECT.md 明确排除 |
| Native mobile app / 原生移动应用 | Responsive web covers mobile use cases / 响应式 Web 覆盖移动用例 |
| Third-party API integration / 第三方 API 集成 | v2+ only / 仅 v2+ |
| Blockchain verification / 区块链验证 | Overengineered for internal use / 对于内部使用过于复杂 |
| Multi-tenancy / 多租户 | Single school deployment / 单学校部署 |

---

## Traceability / 可追溯性

Which phases cover which requirements. Updated during roadmap creation. / 哪些阶段覆盖哪些需求。在路线图创建时更新。

| Requirement / 需求 | Phase / 阶段 | Status / 状态 |
|---------------------|--------------|--------------|
| AUTH-01 | Phase 1 | Pending / 待处理 |
| AUTH-02 | Phase 1 | Pending / 待处理 |
| CERT-03 | Phase 1 | Pending / 待处理 |
| CERT-11 | Phase 1 | Pending / 待处理 |
| CERT-01 | Phase 2 | Pending / 待处理 |
| CERT-02 | Phase 2 | Pending / 待处理 |
| CERT-04 | Phase 2 | Pending / 待处理 |
| CERT-05 | Phase 2 | Pending / 待处理 |
| CERT-06 | Phase 2 | Pending / 待处理 |
| CERT-07 | Phase 2 | Pending / 待处理 |
| CERT-08 | Phase 2 | Pending / 待处理 |
| CERT-09 | Phase 2 | Pending / 待处理 |
| CERT-10 | Phase 3 | Pending / 待处理 |
| OCR-01 | Phase 3 | Pending / 待处理 |
| AUDIT-01 | Phase 3 | Pending / 待处理 |

**Coverage / 覆盖率:**
- v1 requirements / v1 需求: 13 total / 共 13 条
- Mapped to phases / 已映射到阶段: 13
- Unmapped / 未映射: 0 ✓

---

*Requirements defined / 需求定义: 2026-03-19*
*Last updated / 最后更新: 2026-03-19 after roadmap creation / 路线图创建后*
