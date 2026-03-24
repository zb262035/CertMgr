# State: CertMgr / 状态：CertMgr

## Project Reference / 项目引用

See / 参见: `.planning/PROJECT.md` (updated / 更新 2026-03-19)

**Core value / 核心价值:** Faculty/staff certificate assets are safe, accessible, and traceable. / 教职工的证书资产安全、便捷、可追溯。
**Current focus / 当前重点:** Phase 2 - Core / 第二阶段 - 核心功能

---

## Current Position / 当前状态

Phase / 阶段: 1 of 3 (Foundation / 基础架构)
Status / 状态: **COMPLETED / 已完成**
Last activity / 最后活动: 2026-03-24 — Phase 2 规划完成: 3-wave plan, 用户决策, 技术研究

**Phase 1 Progress / Phase 1 进度:** [████████████████████] 100% + 补充

**Phase 2 Progress / Phase 2 进度:** [████████████████████] 3/3 plans complete — Wave 1 + Wave 2 + Wave 3 complete

---

## Phase 1 Completion Summary / Phase 1 完成摘要

Phase 1 已在 2026-03-19 完成并提交到 main 分支。

**Commits / 提交:**
- `041b669` - feat(phase-1): Flask application factory and project structure
- `fe79204` - feat(phase-1): user authentication with register/login/logout
- `6816756` - feat(phase-1): file storage service and permission decorators
- `12d4352` - fix(phase-1): navigation, user management, and certificates stub
- `0cb062b` - docs(phase-2): planning complete with 3 waves, decisions, research

**What was built / 完成内容:**
- ✅ Flask 应用工厂 (`create_app()`)
- ✅ User 模型 (PBKDF2 密码哈希)
- ✅ 认证模块 (注册/登录/登出)
- ✅ 文件存储服务 (UUID 命名、日期分片)
- ✅ 权限装饰器 (`@admin_required`)
- ✅ Admin 用户管理 (`/admin/users`)

**Phase 1 补充 / Phase 1 Supplement (2026-03-23):**
- ✅ 完整导航栏 (首页/证书/上传/管理/个人中心)
- ✅ 操作反馈 (Flash messages)
- ✅ 用户管理增强 (禁用/启用、重置密码)
- ✅ 用户个人中心 (修改密码)

---

## Phase 2 Planning Summary / Phase 2 规划摘要

**Phase 2 已在 2026-03-24 完成规划。**

**Wave 结构 / Wave Structure:**

| Wave | 任务 | 文件数 |
|------|------|--------|
| Wave 1 | Certificate 模型 + CRUD + 卡片模板 | 10 |
| Wave 2 | DataTables API + 搜索/筛选 + Excel 导入 | 5 |
| Wave 3 | Chart.js 统计面板 | 4 |

**用户决策 / User Decisions:**
- 证书列表布局: 卡片布局
- 动态字段: 同一页面动态切换
- 搜索/筛选位置: 列表页顶部
- 统计面板: 详细统计
- Excel批量导入: 自动解析
- 编辑/删除入口: 详情页操作

**Phase 2 执行状态 / Phase 2 Execution Status:**

- **Wave 1 (Plan 01):** ✅ 完成 - Certificate 模型、CRUD 路由、服务、模板
  - Commits: `8245ef6`, `51d454c`, `5ff74f3`, `c92d494`
- **Wave 2 (Plan 02):** ✅ 完成 - DataTables API、搜索/筛选、Excel 批量导入
  - Commits: `3ffd35e`, `99ee52c`, `31b7111`, `aa024b2`
- **Wave 3 (Plan 03):** ✅ 完成 - Chart.js 统计面板
  - Commits: `0175a92`, `18021f8`

---

## Performance Metrics / 性能指标

**Velocity / 速度:**
- Total plans completed / 已完成计划总数: 3
- Average duration / 平均时长: N/A
- Total execution time / 总执行时间: ~2 hours / 小时

**By Phase / 按阶段:**

| Phase / 阶段 | Plans / 计划 | Total / 总计 | Avg/Plan / 平均/计划 |
|--------------|--------------|--------------|---------------------|
| 1. Foundation | 3/3 | Complete | ~40 min |

**Recent Trend / 最近趋势:**
- Phase 1 completed successfully

---

## Accumulated Context / 累积上下文

### Decisions / 决策

From research (2026-03-19) / 来自研究 (2026-03-19):
- Phase 1 / 第一阶段: Use Flask app factory pattern with extensions.py / 使用 Flask 应用工厂模式和 extensions.py
- Phase 1 / 第一阶段: JSONB for dynamic certificate fields (not EAV) / 使用 JSONB 存储动态证书字段（不用 EAV）
- Phase 1 / 第一阶段: UUID-based file naming with date sharding / 使用 UUID 文件命名和日期分片
- Phase 2 / 第二阶段: Use DataTables for server-side pagination / 使用 DataTables 实现服务器端分页
- Phase 3 / 第三阶段: Use ReportLab (not WeasyPrint) for PDF on Windows Server / 使用 ReportLab（不用 WeasyPrint）用于 Windows Server 上的 PDF
- Phase 3 / 第三阶段: Waitress (not Gunicorn) for Windows-compatible WSGI / 使用 Waitress（不用 Gunicorn）实现 Windows 兼容的 WSGI

### Pending Todos / 待办事项

- [x] Phase 2: Create Certificate model and blueprint
- [x] Phase 2: Implement certificate CRUD (upload, list, edit, delete)
- [x] Phase 2: Implement search and filtering
- [x] Phase 2: Implement batch import from Excel
- [x] Phase 2: Implement statistics dashboard (Wave 3 - Plan 03)

### Blockers/Concerns / 阻碍/关注

None yet. / 暂无。

---

## Session Continuity / 会话连续性

Last session / 最后会话: 2026-03-24
Stopped at / 停止于: Phase 2 全部完成 — Wave 1 + Wave 2 + Wave 3 executed, summaries created
Resume file / 恢复文件: None / 无
