# CertMgr — 学校证书管理系统

## What This Is / 项目简介

数字化管理全校教职工各类证书的系统，支持比赛获奖证书、荣誉证书、资格证、职业技能等级证书等。教职工可自行上传/拍照提交，管理员可批量录入。提供证书存储、搜索筛选、统计和导出打印功能。面向全校约1000名教职工，部署于学校服务器。

A digital certificate management system for school faculty/staff. Supports competition awards, honors, qualifications, and vocational skill certificates. Staff can upload/capture certificates, admins can batch import. Provides storage, search, statistics, and export/print. ~1000 users, deployed on school servers.

## Core Value / 核心价值

**教职工的证书资产安全、便捷、可追溯。**
Faculty/staff certificate assets are safe, accessible, and traceable.

## Requirements / 需求

### Active / 当前范围

- [ ] **CERT-01**: 教职工可上传电子证书文件（图片/PDF等）
- [ ] **CERT-02**: 教职工可拍照上传纸质证书
- [ ] **CERT-03**: 系统存储证书文件（本地文件系统）
- [ ] **CERT-04**: 证书记录动态字段（不同证书类型有不同信息）
- [ ] **CERT-05**: 管理员可手动录入/编辑证书
- [ ] **CERT-06**: 管理员可批量导入证书（Excel）
- [ ] **CERT-07**: 支持按姓名、证书类型、日期、颁发机构等搜索
- [ ] **CERT-08**: 支持多条件筛选（时间范围、证书类型等）
- [ ] **CERT-09**: 统计功能：各类型证书数量、趋势图
- [ ] **CERT-10**: 导出证书为可打印格式（PDF）
- [ ] **CERT-11**: 权限控制：教职工只能查看自己的证书，管理员可查看全部
- [ ] **AUTH-01**: 账号管理（注册/登录/找回密码）- 可插拔架构，v1用本地账号
- [ ] **AUTH-02**: 认证集成接口 - 预留与学校现有系统（OA/企业微信/统一身份认证）集成的架构

### Out of Scope / 超出范围

- 证书真伪验证 — 需要第三方权威机构合作
- 证书在线申请/审批流程 — 线下处理即可
- 移动端原生应用 — Web端响应式覆盖
- 与教育部学信网等官方系统对接 — 未来考虑

## Context / 背景

- 项目从零开始，无历史包袱
- 现有代码仅为PyCharm生成的示例文件，无实际功能
- 学校规模约1000名教职工
- 最终部署于学校内部服务器
- 证书颁发机构无法标准化，数量多且分散，直接识别原始信息

## Constraints / 约束

- **部署环境**: 学校内部服务器 — 需要考虑Windows Server兼容性或Linux服务器
- **用户规模**: 约1000人 — SQLite可支撑，PostgreSQL作为升级选项
- **浏览器**: 需要支持学校常用的Chrome/Edge等现代浏览器
- **文件存储**: 本地文件系统存储证书文件，需考虑备份策略

## Key Decisions / 关键决策

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| 认证架构可插拔 | 与学校系统集成不确定，先做简单本地认证 | — Pending |
| 颁发机构不标准化 | 机构太多且分散，直接存储原始信息 | — Pending |
| 动态证书字段 | 不同证书类型字段差异大，预留扩展性 | — Pending |
| OCR自动识别 | 考虑后续自动提取证书文字信息 | — Future |
| Flask + Bootstrap | 轻量、灵活，适合定制化业务 | — Pending |

---
*Last updated: 2026-03-19 after initial requirements gathering*
