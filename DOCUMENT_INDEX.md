# Document Index / 文档功能对照表

本文档列出 CertMgr 项目所有文档及其功能说明。所有新建或修改的文档必须同步更新此表。

This document lists all project documents and their purpose. All new or modified documents must be added to this index.

---

## 项目根目录 / Project Root

| 文档 | 功能 | 说明 |
|------|------|------|
| `CLAUDE.md` | 项目规则 / Project rules | 文档更新规则、文档语言规则、项目信息 |
| `requirements.txt` | Python 依赖 / Python dependencies | 项目所需 Python 包列表 |
| `run.py` | 应用入口 / Application entry point | Flask 应用启动入口 (Phase 1 重构后替代 main.py) |
| `DOCUMENT_INDEX.md` | 文档功能对照表 / Document index | 所有项目文档的功能说明和索引 |

---

## .planning/ 目录 / Planning Directory

### 核心规划文档 / Core Planning Documents

| 文档 | 功能 | 说明 |
|------|------|------|
| `PROJECT.md` | 项目定义 / Project definition | 核心价值、需求、背景、约束、关键决策 |
| `ROADMAP.md` | 路线图 / Roadmap | 3个阶段的计划、依赖关系、成功标准 |
| `REQUIREMENTS.md` | 需求清单 / Requirements list | v1/v2 需求、REQ-ID、覆盖追踪 |
| `STATE.md` | 项目状态 / Project state | 当前阶段、进度、性能指标、待办事项 |
| `SUMMARY.md` | 研究综合摘要 / Research summary | 4个维度研究的综合结论 |
| `config.json` | GSD 配置 / GSD configuration | 工作流偏好、粒度、模型选择 |

### 研究文档 / Research Documents

| 文档 | 功能 | 说明 |
|------|------|------|
| `research/SUMMARY.md` | 研究综合摘要 / Research summary | 4个维度研究的综合结论 |
| `FEATURES.md` | 功能清单 / Features | 系统所有功能及完成状态 |
| `research/FEATURES.md` | 功能全景分析 / Features landscape | 功能分类：基础/核心/差异化（研究文档） |
| `research/ARCHITECTURE.md` | 架构模式研究 / Architecture patterns | Flask工厂模式、JSONB、可插拔认证 |
| `research/PITFALLS.md` | 风险清单 / Pitfalls catalog | 16个常见错误及预防策略 |
| `research/STACK.md` | 技术栈推荐 / Tech stack recommendations | Python/Flask/PostgreSQL/Bootstrap/Waitress 版本 |

### Phase 文档 / Phase Documents

| 文档 | 功能 | 说明 |
|------|------|------|
| `phases/01-foundation/01-RESEARCH.md` | Phase 1 研究文档 / Phase 1 research | Flask 工厂模式、认证、文件存储、权限管理的技术研究 |
| `phases/02-core/02-RESEARCH.md` | Phase 2 研究文档 / Phase 2 research | 证书 CRUD、动态字段、搜索筛选、批量导入、统计图表的技术研究 |
| `phases/02-core/02-CONTEXT.md` | Phase 2 上下文文档 / Phase 2 context | 用户决策：卡片布局、动态字段、搜索、统计、Excel导入、编辑删除方式 |
| `phases/02-core/02-PLAN.md` | Phase 2 执行计划 / Phase 2 plan | 3-wave plan：CRUD+模板 → 搜索+导入 → 统计面板 |
| `phases/02-core/02-core-01-SUMMARY.md` | Phase 2 Wave 1 完成总结 / Wave 1 summary | Certificate 模型、CRUD、卡片模板 |
| `phases/02-core/02-core-02-SUMMARY.md` | Phase 2 Wave 2 完成总结 / Wave 2 summary | DataTables、搜索筛选、Excel 批量导入 |
| `phases/02-core/02-03-SUMMARY.md` | Phase 2 Wave 3 完成总结 / Wave 3 summary | Chart.js 统计面板 |
| `phases/02-core/02-VERIFICATION.md` | Phase 2 验证报告 / Phase 2 verification | 功能验证、安全审查 |
| `phases/01-foundation/01-PLAN.md` | Phase 1 Wave 1 执行计划 / Phase 1 Wave 1 plan | Flask 应用工厂、目录结构、User 模型、基础模板 |
| `phases/01-foundation/02-PLAN.md` | Phase 1 Wave 2 执行计划 / Phase 1 Wave 2 plan | 用户注册/登录/登出、Auth Adapter 接口 |
| `phases/01-foundation/03-PLAN.md` | Phase 1 Wave 3 执行计划 / Phase 1 Wave 3 plan | UUID 文件存储、权限装饰器、Admin 用户管理 |
| `phases/01-foundation/01-SUMMARY.md` | Phase 1 完成总结 / Phase 1 summary | Phase 1 完成内容、文件列表、验证状态 |
| `phases/{N}-{name}/PLAN.md` | 阶段执行计划 / Phase execution plan | Phase N 的具体任务列表 |
| `phases/{N}-{name}/SUMMARY.md` | 阶段完成总结 / Phase summary | Phase N 的完成内容、验证状态 |

---

## 应用代码目录 / Application Code Directory

> Phase 1 创建

| 目录 | 功能 | 说明 |
|------|------|------|
| `app/__init__.py` | 应用工厂 / Application factory | Flask 应用创建和初始化 (`create_app()`) |
| `app/config.py` | 配置管理 / Configuration | Dev/Prod/Testing 环境配置 |
| `app/extensions.py` | 扩展实例 / Extensions | SQLAlchemy、LoginManager、CSRF 共享实例 |
| `app/models/user.py` | 用户模型 / User model | User ORM 模型，PBKDF2 密码哈希 |
| `app/models/certificate.py` | 证书模型 / Certificate model | Certificate/CertificateType 模型，JSONB 动态字段 |
| `app/blueprints/auth/` | 认证模块 / Auth module | 注册、登录、登出路由和表单 |
| `app/blueprints/admin/` | 管理模块 / Admin module | 用户管理、权限控制路由 |
| `app/blueprints/certificates/` | 证书模块 / Certificates module | 证书 CRUD、OCR 识别、批量导入、DataTables API |
| `app/blueprints/statistics/` | 统计模块 / Statistics module | Chart.js 统计面板 API |
| `app/services/auth_service.py` | 认证服务 / Auth service | 可插拔认证适配器接口 |
| `app/services/file_storage_service.py` | 文件存储服务 / File storage | UUID 命名、日期分片的安全存储 |
| `app/services/ocr_service.py` | OCR 服务 / OCR service | PaddleOCR 证书识别服务 |
| `app/decorators.py` | 权限装饰器 / Permission decorators | `@admin_required` 管理员权限控制 |
| `app/templates/` | 模板文件 / Templates | Jinja2 HTML 模板 (base, auth, admin, home) |
| `instance/` | 实例目录 / Instance directory | 运行时生成（数据库、上传文件），不进入 git |

---

## 文档更新记录 / Document Update Log

| 日期 | 更新内容 | 负责人 |
|------|----------|--------|
| 2026-03-19 | 初始创建本文档，创建所有核心规划文档 | Claude |
| 2026-03-19 | 移除不存在的 CLAUDE.md 引用，添加 01-RESEARCH.md 到 Phase 文档表 | Claude |
| 2026-03-19 | 添加 01-PLAN.md、02-PLAN.md、03-PLAN.md 到 Phase 文档表 | Claude |
| 2026-03-23 | 更新项目状态：移除 main.py（已删除），添加 run.py；添加 Phase 1 SUMMARY.md | Claude |
| 2026-03-23 | 更新 STATE.md：Phase 1 已完成，Phase 2 准备开始 | Claude |
| 2026-03-23 | 创建 .planning/FEATURES.md 功能清单文档 | Claude |
| 2026-03-23 | 更新 CLAUDE.md：状态从"Phase 1 规划中"改为"Phase 1 已完成" | Claude |
| 2026-03-24 | 添加 phases/02-core/02-RESEARCH.md 到 Phase 文档表 | Claude |
| 2026-03-24 | 添加 phases/02-core/02-CONTEXT.md 和 02-PLAN.md；Phase 2 规划完成 | Claude |
| 2026-03-24 | 添加 Phase 2 完成文档（Wave 1-3 summaries, verification）；添加 certificates/statistics blueprints、ocr_service、certificate 模型到文档索引 | Claude |

---

*此文档受项目 CLAUDE.md 规则约束，必须保持中英双语。*
*This document is governed by project CLAUDE.md rules, must maintain bilingual Chinese + English.*
