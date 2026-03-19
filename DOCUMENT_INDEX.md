# 文档功能对照表 / Document Index

本文档列出 CertMgr 项目所有文档及其功能说明。所有新建或修改的文档必须同步更新此表。

This document lists all project documents and their purpose. All new or modified documents must be added to this index.

---

## 项目根目录 / Project Root

| 文档 | 功能 | 说明 |
|------|------|------|
| `CLAUDE.md` | Claude Code 全局规则 / Global Claude Code rules | Claude Code 的最低层规则，规定所有项目文档必须中英双语 |
| `README.md` | 项目说明 / Project overview | 项目简介、安装方法、快速开始 |
| `requirements.txt` | Python 依赖 / Python dependencies | 项目所需 Python 包列表 |
| `main.py` | 应用入口 / Application entry point | 临时文件，待 Phase 1 重构 |

---

## .planning/ 目录 / Planning Directory

### 核心规划文档 / Core Planning Documents

| 文档 | 功能 | 说明 |
|------|------|------|
| `PROJECT.md` | 项目定义 / Project definition | 核心价值、需求、背景、约束、关键决策 |
| `ROADMAP.md` | 路线图 / Roadmap | 3个阶段的计划、依赖关系、成功标准 |
| `REQUIREMENTS.md` | 需求清单 / Requirements list | v1/v2 需求、REQ-ID、覆盖追踪 |
| `STATE.md` | 项目状态 / Project state | 当前阶段、进度、性能指标、待办事项 |
| `config.json` | GSD 配置 / GSD configuration | 工作流偏好、粒度、模型选择 |

### 研究文档 / Research Documents

| 文档 | 功能 | 说明 |
|------|------|------|
| `research/SUMMARY.md` | 研究综合摘要 / Research summary | 4个维度研究的综合结论 |
| `research/FEATURES.md` | 功能全景分析 / Features landscape | 功能分类：基础/核心/差异化 |
| `research/ARCHITECTURE.md` | 架构模式研究 / Architecture patterns | Flask工厂模式、JSONB、可插拔认证 |
| `research/PITFALLS.md` | 风险清单 / Pitfalls catalog | 16个常见错误及预防策略 |
| `research/STACK.md` | 技术栈推荐 / Tech stack recommendations | Python/Flask/PostgreSQL/Bootstrap/Waitress 版本 |

### Phase 文档 / Phase Documents

| 文档 | 功能 | 说明 |
|------|------|------|
| `phases/{N}-{name}/PLAN.md` | 阶段执行计划 / Phase execution plan | Phase N 的具体任务列表 |
| `phases/{N}-{name}/RESEARCH.md` | 阶段研究文档 / Phase research | Phase N 的实现细节研究 |
| `phases/{N}-{name}/STATE.md` | 阶段状态 / Phase state | Phase N 的执行状态 |

---

## 应用代码目录 / Application Code Directory

> Phase 1 创建

| 目录 | 功能 | 说明 |
|------|------|------|
| `app/__init__.py` | 应用工厂 / Application factory | Flask 应用创建和初始化 |
| `app/config.py` | 配置管理 / Configuration | 开发/生产环境配置 |
| `app/extensions.py` | 扩展实例 / Extensions | SQLAlchemy、LoginManager 等共享实例 |
| `app/models/` | 数据模型 / Data models | User、Certificate、CertificateType 等 ORM 模型 |
| `app/blueprints/` | 模块路由 / Blueprints | auth、certificates、admin 等模块 |
| `app/services/` | 业务逻辑 / Business logic | 文件存储、认证、导出等服务层 |
| `app/templates/` | 模板文件 / Templates | Jinja2 HTML 模板 |
| `app/static/` | 静态资源 / Static files | CSS、JS、uploads 目录 |
| `instance/` | 实例目录 / Instance directory | 运行时生成的文件（不进入 git） |

---

## 文档更新记录 / Document Update Log

| 日期 | 更新内容 | 负责人 |
|------|----------|--------|
| 2026-03-19 | 初始创建本文档，创建所有核心规划文档 | Claude |

---

*此文档由 CLAUDE.md 全局规则约束，必须保持中英双语。*
*This document is governed by CLAUDE.md global rules, must maintain bilingual Chinese + English.*
