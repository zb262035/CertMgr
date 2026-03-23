# CertMgr 功能清单 / Features

**项目:** 学校证书管理系统 / School Certificate Management System
**版本:** v1.0
**更新:** 2026-03-23 (Phase 1 补充: 导航/反馈/用户管理增强)

---

## 概览 / Overview

CertMgr 提供教职工证书数字化管理，支持上传、存储、搜索、统计和导出。

CertMgr provides faculty/staff certificate digitization, supporting upload, storage, search, statistics, and export.

**当前进度 / Current Progress:**
- Phase 1: ✅ 完成 / Complete
- Phase 2: ⏳ 待开始 / Pending
- Phase 3: ⏳ 待开始 / Pending

---

## 功能模块 / Feature Modules

### 1. 用户认证 / User Authentication

| 功能 / Feature | ID | 状态 | 说明 |
|---------------|-----|------|------|
| 用户注册 / User registration | AUTH-01 | ✅ 已完成 | 邮箱 + 密码注册，PBKDF2 加密存储 |
| 用户登录 / User login | AUTH-01 | ✅ 已完成 | 会话管理，支持"记住我" |
| 用户登出 / User logout | AUTH-01 | ✅ 已完成 | 清除会话 |
| 认证适配器接口 / Auth adapter interface | AUTH-02 | ✅ 已完成 | 可插拔架构，预留 SSO 集成 |

### 2. 用户管理 / User Management

| 功能 / Feature | ID | 状态 | 说明 |
|---------------|-----|------|------|
| 管理员查看所有用户 / Admin views all users | CERT-11 | ✅ 已完成 | `/admin/users` 页面 |
| 管理员切换用户角色 / Admin toggles user role | CERT-11 | ✅ 已完成 | 提升/降级为管理员 |
| 管理员删除用户 / Admin deletes user | CERT-11 | ✅ 已完成 | 不可删除自己 |
| 防止权限升级 / Prevent privilege escalation | CERT-11 | ✅ 已完成 | 用户无法修改自己 |
| 管理员禁用/启用用户 / Admin enable/disable user | CERT-11 | ✅ 已完成 | 禁用后用户无法登录 |
| 管理员重置用户密码 / Admin reset user password | CERT-11 | ✅ 已完成 | 生成随机密码 |
| 用户修改自己密码 / User change own password | AUTH-01 | ✅ 已完成 | `/profile` 页面 |

### 2.1 导航与反馈 / Navigation & Feedback

| 功能 / Feature | ID | 状态 | 说明 |
|---------------|-----|------|------|
| 完整导航栏 / Complete navbar | UI-01 | ✅ 已完成 | 首页、证书、上传、管理、个人中心 |
| 操作成功反馈 / Success feedback | UI-02 | ✅ 已完成 | Flash messages |
| 操作失败反馈 / Error feedback | UI-02 | ✅ 已完成 | Flash messages |
| 登出功能 / Logout function | AUTH-01 | ✅ 已完成 | 清除会话 |

### 3. 证书管理 / Certificate Management

| 功能 / Feature | ID | 状态 | 说明 |
|---------------|-----|------|------|
| 上传电子证书 / Upload electronic certificate | CERT-01 | ⏳ 待做 | 支持图片/PDF |
| 拍照上传纸质证书 / Photo capture upload | CERT-02 | ⏳ 待做 | 移动端拍照上传 |
| 查看证书列表 / View certificate list | CERT-01 | ⏳ 待做 | 分页、排序 |
| 查看他人证书 / Admin views any certificate | CERT-05 | ⏳ 待做 | 管理员可查看所有 |
| 编辑证书 / Edit certificate | CERT-05 | ⏳ 待做 | 元数据编辑 |
| 删除证书 / Delete certificate | CERT-05 | ⏳ 待做 | 权限控制 |

### 4. 动态字段 / Dynamic Fields

| 功能 / Feature | ID | 状态 | 说明 |
|---------------|-----|------|------|
| 不同证书类型不同字段 / Different fields per type | CERT-04 | ⏳ 待做 | 比赛获奖/荣誉/资格证等 |
| 动态表单渲染 / Dynamic form rendering | CERT-04 | ⏳ 待做 | 根据类型显示不同表单 |

### 5. 文件存储 / File Storage

| 功能 / Feature | ID | 状态 | 说明 |
|---------------|-----|------|------|
| UUID 文件命名 / UUID file naming | CERT-03 | ✅ 已完成 | 防止文件名冲突和编码问题 |
| 日期分片 / Date sharding | CERT-03 | ✅ 已完成 | `uploads/YYYY/MM/` 目录结构 |
| 文件类型验证 / File type validation | CERT-03 | ✅ 已完成 | 仅允许 pdf/png/jpg/jpeg/gif |
| 文件大小限制 / File size limit | CERT-03 | ✅ 已完成 | 最大 10MB |
| 路径遍历防护 / Path traversal prevention | CERT-03 | ✅ 已完成 | 验证路径不超出上传目录 |

### 6. 搜索与筛选 / Search & Filter

| 功能 / Feature | ID | 状态 | 说明 |
|---------------|-----|------|------|
| 按姓名搜索 / Search by name | CERT-07 | ⏳ 待做 | 证书持有人搜索 |
| 按类型筛选 / Filter by type | CERT-08 | ⏳ 待做 | 证书类型筛选 |
| 按日期范围筛选 / Filter by date range | CERT-08 | ⏳ 待做 | 时间范围筛选 |
| 按颁发机构筛选 / Filter by issuer | CERT-08 | ⏳ 待做 | 颁发机构筛选 |
| 多条件组合 / Multi-filter combination | CERT-08 | ⏳ 待做 | 同时使用多个筛选条件 |

### 7. 批量操作 / Batch Operations

| 功能 / Feature | ID | 状态 | 说明 |
|---------------|-----|------|------|
| Excel 批量导入 / Batch import from Excel | CERT-06 | ⏳ 待做 | 管理员功能 |
| 批量导出 / Batch export | - | ⏳ 待做 | 未来版本 |

### 8. 统计面板 / Statistics Dashboard

| 功能 / Feature | ID | 状态 | 说明 |
|---------------|-----|------|------|
| 按类型统计 / Count by type | CERT-09 | ⏳ 待做 | 各类型证书数量 |
| 时间趋势 / Trends over time | CERT-09 | ⏳ 待做 | 月度/年度趋势图 |
| 导出统计报告 / Export statistics report | STATS-02 | ⏳ 待做 | v2 版本 |

### 9. 权限控制 / Permission Control

| 功能 / Feature | ID | 状态 | 说明 |
|---------------|-----|------|------|
| 用户只能看自己的证书 / Users view own only | CERT-11 | ✅ 已完成 | `@owner_required` 装饰器 |
| 管理员可看所有 / Admin views all | CERT-11 | ✅ 已完成 | `@admin_required` 装饰器 |
| 文件访问权限 / File access permission | CERT-11 | ✅ 已完成 | 验证用户身份 |

### 10. PDF 导出 / PDF Export

| 功能 / Feature | ID | 状态 | 说明 |
|---------------|-----|------|------|
| 导出为可打印 PDF / Export as printable PDF | CERT-10 | ⏳ 待做 | Phase 3 |
| 中文支持 / Chinese language support | CERT-10 | ⏳ 待做 | 中文字体支持 |

### 11. 高级功能 / Advanced Features

| 功能 / Feature | ID | 状态 | 说明 |
|---------------|-----|------|------|
| OCR 自动提取 / OCR auto-extraction | OCR-01 | ⏳ 待做 | Phase 3，从照片提取文字 |
| 审计日志 / Audit trail | AUDIT-01 | ⏳ 待做 | Phase 3，谁操作了什么 |
| SSO 集成 / SSO integration | SSO-01/02/03 | ⏳ 待做 | OA/企业微信/CAS |
| 证书过期提醒 / Expiration alerts | ALERT-01 | ⏳ 待做 | v2 版本 |

---

## 证书类型 / Certificate Types

系统支持以下证书类型，每种类型有不同的动态字段：

| 类型 / Type | 动态字段 / Dynamic Fields |
|-------------|--------------------------|
| 比赛获奖证书 / Competition Award | 奖项名称、比赛名称、主办单位、获奖等级 |
| 荣誉证书 / Honor | 荣誉名称、颁发单位、授予日期 |
| 资格证 / Qualification | 证书名称、证书编号、颁发机构、有效期限 |
| 职业技能等级证书 / Vocational Skill | 职业名称、等级、证书编号、颁发机构 |

---

## 状态说明 / Status Legend

| 状态 | 说明 |
|------|------|
| ✅ 已完成 | Phase 1 已实现 |
| ⏳ 待做 | 尚未实现，将在后续 Phase 完成 |
| - | 未规划或超出范围 |

---

## 更新记录 / Change Log

| 日期 | 更新内容 |
|------|----------|
| 2026-03-23 | Phase 1 补充: 添加禁用/启用用户、重置密码、修改密码功能；完善导航栏；添加操作反馈 |
| 2026-03-23 | 创建功能清单文档，同步 Phase 1 完成状态 |

---

*此文档受项目 CLAUDE.md 规则约束，必须保持中英双语。*
*This document is governed by project CLAUDE.md rules, must maintain bilingual Chinese + English.*
