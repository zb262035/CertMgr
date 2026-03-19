# State: CertMgr / 状态：CertMgr

## Project Reference / 项目引用

See / 参见: `.planning/PROJECT.md` (updated / 更新 2026-03-19)

**Core value / 核心价值:** Faculty/staff certificate assets are safe, accessible, and traceable. / 教职工的证书资产安全、便捷、可追溯。
**Current focus / 当前重点:** Phase 1 - Foundation / 第一阶段 - 基础架构

---

## Current Position / 当前状态

Phase / 阶段: 1 of 3 (Foundation / 基础架构)
Plan / 计划: Not started / 未开始
Status / 状态: Ready to plan / 准备规划
Last activity / 最后活动: 2026-03-19 — Roadmap created / 路线图已创建

Progress / 进度: [░░░░░░░░░░] 0%

---

## Performance Metrics / 性能指标

**Velocity / 速度:**
- Total plans completed / 已完成计划总数: 0
- Average duration / 平均时长: N/A
- Total execution time / 总执行时间: 0 hours / 小时

**By Phase / 按阶段:**

| Phase / 阶段 | Plans / 计划 | Total / 总计 | Avg/Plan / 平均/计划 |
|--------------|--------------|--------------|---------------------|
| - | - | - | - |

**Recent Trend / 最近趋势:**
- No completed plans yet / 尚无已完成计划

*Updated after each plan completion / 每次计划完成后更新*

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

None yet. / 暂无。

### Blockers/Concerns / 阻碍/关注

None yet. / 暂无。

---

## Session Continuity / 会话连续性

Last session / 最后会话: 2026-03-19 00:00
Stopped at / 停止于: Roadmap created, ready to plan Phase 1 / 路线图已创建，准备规划第一阶段
Resume file / 恢复文件: None / 无
