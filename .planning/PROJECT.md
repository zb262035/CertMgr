# CertMgr — 学校证书管理系统

## What This Is / 项目简介

数字化管理全校教职工各类证书的系统，支持比赛获奖证书、荣誉证书、资格证、职业技能等级证书等。教职工可自行上传/拍照提交，管理员可批量录入。提供证书存储、搜索筛选、统计和导出打印功能。面向全校约1000名教职工，部署于学校服务器。

A digital certificate management system for school faculty/staff. Supports competition awards, honors, qualifications, and vocational skill certificates. Staff can upload/capture certificates, admins can batch import. Provides storage, search, statistics, and export/print. ~1000 users, deployed on school servers.

## Core Value / 核心价值

**教职工的证书资产安全、便捷、可追溯。**
Faculty/staff certificate assets are safe, accessible, and traceable.

## Current Milestone: v1.1 统计报表导出

**Goal:** 在证书列表页添加 Excel 导出功能，支持导出证书清单

**Target features:**
- 证书清单 Excel 导出（按筛选条件）
- 导出字段：标题、持有人、部门、类型、日期、颁发机构等
- 管理员可导出全部，用户只能导出自己的

## Requirements / 需求

### Active / 当前范围

- [ ] **RPT-01**: 用户可在证书列表页导出当前筛选结果的证书清单
- [ ] **RPT-02**: 导出包含：标题、持有人、部门、证书类型、获奖日期、颁发机构、创建时间等字段
- [ ] **RPT-03**: 导出文件名为 `证书清单_YYYYMMDD_HHmmss.xlsx`
- [ ] **RPT-04**: 支持导出全部证书或按筛选条件导出
- [ ] **RPT-05**: 管理员可导出所有证书，普通用户只能导出自己的

### Validated / 已验证

- CERT-01 ~ CERT-11 (Phase 1-2 完成)
- AUTH-01 ~ AUTH-02 (Phase 1 完成)

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
| Excel 导出 | 使用 openpyxl 库生成 .xlsx 文件 | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-20 after v1.1 milestone started*
