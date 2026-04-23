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
| `RETROSPECTIVE-ENGINEERING.md` | 工程复盘报告 / Engineering retrospective | Phase 1-5 架构/测试/安全/DevOps/前端/依赖各维度评价、改进优先级 |
| `ENGINEERING_IMPROVEMENT_PLAN.md` | 工程修正计划 / Engineering improvement plan | P0-P3 共 11 项修正任务，根本原因+目标+做法+提升 |

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
| `PHASE-4/01-权限系统设计.md` | Phase 4 权限系统设计 / Phase 4 permission system design | 三级权限体系、部门管理、批量操作、导航栏设计 |
| `SESSION_LOG-2026-03-31.md` | 手动测试会话记录 / Testing session log | 按权限层级手动测试发现的问题和修复记录 |
| `PHASE-5/01-动态字段管理系统设计.md` | Phase 5 动态字段管理系统设计 / Phase 5 dynamic field management design | 证书类型动态管理、用户字段动态管理 |

### 待讨论文档 / Pending Documents

| 文档 | 功能 | 说明 |
|------|------|------|
| `PENDING/02-标志性成果管理需求.md` | 标志性成果管理需求 / Iconic achievements requirements | 成果类型扩展、分值体系、字段灵活性 |

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
| `app/models/user_field.py` | 用户字段模型 / User field model | UserField 动态字段定义模型 |
| `app/blueprints/auth/` | 认证模块 / Auth module | 注册、登录、登出路由和表单 |
| `app/blueprints/admin/` | 管理模块 / Admin module | 用户管理、权限控制路由 |
| `app/blueprints/certificates/` | 证书模块 / Certificates module | 证书 CRUD、OCR 识别、批量导入、DataTables API |
| `app/blueprints/statistics/` | 统计模块 / Statistics module | Chart.js 统计面板 API |
| `app/services/auth_service.py` | 认证服务 / Auth service | 可插拔认证适配器接口 |
| `app/services/file_storage_service.py` | 文件存储服务 / File storage | UUID 命名、日期分片的安全存储 |
| `app/services/ocr_service.py` | OCR 服务 / OCR service | PaddleOCR 证书识别服务 |
| `app/decorators.py` | 权限装饰器 / Permission decorators | `@admin_required` 管理员权限控制 |
| `app/templates/` | 模板文件 / Templates | Jinja2 HTML 模板 (base, auth, admin, home, certificates) |
| `app/templates/admin/certificate_types.html` | 证书类型管理列表 / Certificate types list | 证书类型 CRUD 列表页 |
| `app/templates/admin/certificate_type_edit.html` | 证书类型编辑 / Certificate type edit | 证书类型字段定义编辑页 |
| `app/templates/admin/user_fields.html` | 用户字段管理列表 / User fields list | 用户字段 CRUD 列表页 |
| `app/templates/admin/user_field_edit.html` | 用户字段编辑 / User field edit | 用户字段定义编辑页 |
| `instance/` | 实例目录 / Instance directory | 运行时生成（数据库、上传文件），不进入 git |
| `migrations/` | 数据迁移脚本 / Migration scripts | Flask-Migrate 迁移脚本目录 |
| `app/static/js/schema-loader.js` | Schema 加载器 / Schema loader | 动态表单字段渲染 JavaScript |

---

## 部署相关目录 / Deployment Directory

> P4 Docker 部署相关文件

| 文件 | 功能 | 说明 |
|------|------|------|
| `Dockerfile` | Docker 镜像定义 / Docker image definition | Python 3.9 + PaddleOCR + Waitress 生产镜像 |
| `docker-compose.yml` | Docker Compose 配置 / Docker Compose config | Flask + PostgreSQL + Nginx 完整服务栈 |
| `.env.example` | 环境变量模板 / Environment template | 生产环境变量模板（SECRET_KEY, DATABASE_URL 等） |
| `wsgi.py` | WSGI 入口点 / WSGI entry point | 生产环境 Waitress WSGI 启动 |
| `start.sh` | 容器启动脚本 / Container startup script | 数据库初始化 + 服务启动 |
| `init_db.py` | 数据库初始化脚本 / Database init script | `db.create_all()` 独立调用 |
| `deploy/nginx.conf` | Nginx 反向代理配置 / Nginx reverse proxy config | 80 端口、反向代理、安全头、压缩配置 |
| `.dockerignore` | Docker 构建排除 / Docker build exclusions | 排除测试/文档/IDE/缓存文件 |

---

## 测试目录 / Testing Directory

> Phase 2 补充

| 目录/文件 | 功能 | 说明 |
|------------|------|------|
| `tests/` | 测试目录 / Test directory | Playwright UI 测试、单元测试、API 测试 |
| `tests/test_ui.py` | UI 测试脚本 / UI test script | 端到端浏览器测试（登录、证书列表、搜索、上传、统计） |
| `tests/conftest.py` | pytest 配置 / pytest configuration | 临时数据库 fixture、测试客户端 |
| `tests/unit/test_models.py` | 单元测试 / Unit tests | User、Certificate、CertificateType 模型测试 |
| `tests/unit/test_permission_service.py` | 权限服务单元测试 / Permission service unit tests | 校级/部门管理员权限边界测试 |
| `tests/unit/test_file_storage.py` | 文件存储服务单元测试 / File storage unit tests | 文件验证、路径安全、存储/删除测试 |
| `tests/unit/test_ocr_service.py` | OCR 服务单元测试 / OCR service unit tests | 文本质量评估、类型检测、字段提取测试 |
| `tests/unit/test_certificate_service.py` | 证书服务单元测试 / Certificate service unit tests | Excel 导入、CRUD 操作、文件验证测试 |
| `tests/api/test_routes.py` | API 测试 / API tests | 认证、证书 CRUD、管理员 API 端点测试、权限边界测试 |

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
| 2026-03-24 | 改进 tests/test_ui.py：添加测试结果汇总、自动创建测试数据、更好的错误检测；更新测试目录文档 | Claude |
| 2026-03-26 | 创建 Phase 4 权限系统设计文档和标志性成果需求待讨论文档 | Claude |
| 2026-03-26 | 更新状态：Phase 3 已完成（8/8 UI测试通过），Phase 4 进行中 | Claude |
| 2026-03-30 | 更新状态：Phase 4 权限分级系统已完成（部门管理、三级权限、批量操作） | Claude |
| 2026-03-30 | v1.1 UI优化：批量管理、视图切换、卡片/列表视图、上传入口区分 | Claude |
| 2026-03-31 | v1.1 UI优化续：部门管理员证书详情403修复、列表视图显示修复、统计面板按部门过滤、姓名字段（extra JSONB）、全系统姓名显示 | Claude |
| 2026-03-31 | Phase 5 动态字段管理系统：证书类型管理、用户字段管理、schema-loader.js、OCR LLM 动态字段提取、llm_service 数据库读取支持 | Claude |
| 2026-04-14 | 添加 RETROSPECTIVE-ENGINEERING.md 工程复盘报告；更新 CLAUDE.md 添加规则 7-10；创建 ENGINEERING_IMPROVEMENT_PLAN.md；完善文档索引 | Claude |
| 2026-04-17 | 完成 P0-P4 工程改进计划：权限服务、Service 层拆分、Flask-Migrate、单元测试（99个）、权限边界 API 测试（27个）、Docker 部署配置、生产配置加固 | Claude |
| 2026-04-21 | OCR 优化：deepseek-r1:8b → qwen2.5vl:7b（速度 15-20s → 7-8s）；添加 OCR 字段名映射（LLM → schema）；sips → Pillow（跨平台）；修复非管理员导出功能；IMPROVEMENT_PLAN.md 添加 P3.3 OCR 速度优化待办 | Claude |
| 2026-04-23 | 批量上传 OCR 功能修复：修复 `int is not defined`（改用 `Math.floor`）；修复 CSRF token 传递问题（移除 formData 中的重复 csrf_token）；修复预览只显示第一个文件（改为多文件缩略图网格）；添加动态字段渲染；简化流程移除多余的"加入队列"按钮 | Claude |

---

*此文档受项目 CLAUDE.md 规则约束，必须保持中英双语。*
*This document is governed by project CLAUDE.md rules, must maintain bilingual Chinese + English.*
