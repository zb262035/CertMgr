# CertMgr 项目规则 / Project Rules

## 文档更新规则 / Document Update Rule

**每创建一个新文档，必须同步更新 `DOCUMENT_INDEX.md`。**

Every new document created must be added to `DOCUMENT_INDEX.md`.

### 更新步骤 / Update Steps

1. 创建新文档后，立即更新 `DOCUMENT_INDEX.md`
2. 在对应的分类表格中添加新文档条目
3. 在"文档更新记录"中添加更新日志

### 示例 / Example

创建 `phases/02-core/01-RESEARCH.md` 后：

```markdown
| `phases/02-core/01-RESEARCH.md` | Phase 2 研究文档 / Phase 2 research | 证书 CRUD、搜索、导入导出的技术研究 |
```

更新日志：

```markdown
| 2026-03-20 | 添加 phases/02-core/01-RESEARCH.md | Claude |
```

---

## 文档语言规则 / Documentation Language Rule

所有项目文档必须中英双语。/ All project documents must be bilingual Chinese + English.

- 中文：让用户看懂 / Chinese: so the user can understand
- 英文：让 AI 更好理解工作内容 / English: so AI can better understand the work

---

## 高层开发指导 / High-Level Development Guidelines

> 这些规则来自项目复盘经验教训（RETROSPECTIVE.md），每个新功能开发时必须遵守。
> These rules come from project retrospective lessons (RETROSPECTIVE.md), must be followed for every new feature.

### 规则 1: 测试跟着功能走 / Tests Ship With Features

**禁止提交没有对应测试的功能代码。**
Each new feature MUST include its tests in the same commit/PR. "I'll add tests later" means "no tests."

- 新 Service 函数 → 必须有单元测试
- 新 API 端点 → 必须有 API 测试（含权限边界）
- 新页面/交互 → 必须有 UI 测试或手动验证记录

### 规则 2: 复制粘贴即重构信号 / Copy-Paste Is a Refactor Signal

**同一段逻辑出现第二次时，立即抽取公共方法，不要等到第三次。**
When the same logic appears twice, extract it immediately. Don't wait for the third time.

- 权限检查逻辑 → 抽成 `permission_service.py` 中的函数
- 表单验证逻辑 → 抽成 form 级别的 validator
- 前端 JS 逻辑 → 抽成独立 `.js` 文件

### 规则 3: 硬编码是临时状态 / Hardcoded Values Are Temporary

**任何硬编码值必须在首次使用后计划移除时间。**
All hardcoded values (schemas, URLs, magic numbers) must have a plan for removal.

- 新增硬编码时注释 `# TODO: 移除时机`
- 优先使用数据库配置或环境变量
- 定期清理已无用的硬编码

### 规则 4: 每个 Blueprint 都要有 Service 层 / Every Blueprint Gets a Service Layer

**路由函数只负责：提取参数 → 调用 Service → 返回响应。**
Route functions only: extract params → call service → return response.

- 路由函数不超过 30 行
- 业务逻辑全部在 `services/` 目录下
- 数据库操作通过 Service 层，不直接在路由中 `db.session`

### 规则 5: 安全不能绕过 / Security Is Never Optional

**禁止为方便而 `@csrf.exempt`，禁止为调试而硬编码密钥。**
Never bypass security for convenience. Fix the root cause, not bypass it.

- CSRF token 必须正确传递，不豁免
- 文件上传必须校验内容，不仅校验扩展名
- 批量操作必须包裹事务

### 规则 6: 部署同步建设 / Deploy As You Build

**每个 Phase 完成时，部署能力要同步就绪。**
At the end of each phase, deployment readiness must be verified.

- 依赖变更立即更新 `requirements.txt`
- Schema 变更必须通过 `Flask-Migrate` 迁移脚本
- 新环境配置项写入 `.env.example`

### 规则 7: 架构一致性贯穿全程 / Architecture Consistency Is Non-Negotiable

**架构规范执行不能虎头蛇尾，第一个模块做到位不等于后面可以放松。**
Don't relax architecture standards partway through. Doing it right for module A doesn't excuse doing it wrong for module B.

- 每个 Blueprint 必须有对应的 Service 层，不能有的有有的没有
- 新增模块时立即遵循项目结构，不留"以后再改"的借口
- Code Review 时必须检查是否遵循架构规范

### 规则 8: 批量操作必须事务保护 / Batch Operations Require Transaction Safety

**批量操作中途失败必须全部回滚，不允许部分成功。**
Batch operations must roll back entirely on failure — partial success is data corruption.

- 所有 `batch_` 路由操作必须包裹 `db.session.begin_nested()` 或 try/except + rollback
- 禁止在循环中逐条 `session.add()` / `session.commit()`
- 测试必须覆盖批量操作中途失败的回滚场景

### 规则 9: 前端技术栈统一 / Frontend Stack Must Be Unified

**不混用 jQuery 和原生 JS，不在一个模块里同时用两种风格。**
Don't mix jQuery and vanilla JS in the same project or module.

- 统一选择一种风格（推荐原生 JS + fetch）并坚持使用
- 避免在 Jinja2 模板中写复杂业务逻辑（权限判断除外）
- 超过 200 行的内联 JS 必须拆分到独立 `.js` 文件

### 规则 10: 依赖完整性 / Dependency Completeness

**requirements.txt 必须在每次新增依赖时同步更新，禁止"装完代码再补"。**
Every new dependency must be added to requirements.txt immediately. No "I'll add it later."

- 新增任何 `import` 必须确保在 requirements.txt 中
- 首次运行 `pip install -r requirements.txt` 必须能完整运行所有功能
- 推荐同时生成 `requirements.lock` 锁定所有传递依赖版本

---

## 项目信息 / Project Info

- **项目路径:** /Users/ice/PycharmProjects/CertMgr
- **类型:** Python Flask Web Application
- **状态:** Phase 1-5 + v1.1 完成，v1.2 OCR 优化完成（速度 15-20s → 7-8s），工程改进计划进行中

## 技术栈 / Tech Stack

- Python 3.11+
- Flask 3.1.x + Flask-SQLAlchemy
- PostgreSQL 15+ (开发用 SQLite)
- Bootstrap 5.3.8
- Waitress 3.0.x
- Playwright (UI 测试)
- Ollama VLM (glm-ocr) + qwen2.5vl:7b (OCR 识别 + 字段提取)
- Pillow (跨平台图片预处理)

---

## 测试流程 / Test Workflow

**每实现一个功能，必须通过全面测试验证后再继续。**

### 开发节奏 / Development Rhythm

```
实现功能 → 单元测试 → API 测试 → UI 测试 → 全部通过 → 下一功能
```

### 测试类型 / Test Types

1. **单元测试 (Unit Tests)** - 业务逻辑
   ```bash
   python3 -m pytest tests/unit/
   ```
   - Service 层逻辑
   - 数据验证
   - 权限检查

2. **API 测试 (API Tests)** - 后端接口
   ```bash
   python3 -m pytest tests/api/
   ```
   - REST API 端点
   - 请求/响应格式
   - 认证和授权

3. **UI 测试 (UI Tests)** - 端到端
   ```bash
   python3 tests/test_ui.py
   ```
   - 页面加载无错误
   - 表单提交正常
   - 按钮点击响应
   - 页面跳转正确
   - Console 无 JavaScript 错误

### 测试检查清单 / Test Checklist

- [ ] 功能代码编写完成
- [ ] 单元测试：Service/Model 逻辑测试
- [ ] API 测试：Flask test client 测试
- [ ] UI 测试：Playwright 浏览器测试
- [ ] 运行全部测试，全部通过
- [ ] 功能交付完美，才进行下一个

### 测试目录结构 / Test Directory Structure

```
tests/
├── unit/           # 单元测试
│   ├── test_services.py
│   └── test_models.py
├── api/            # API 测试
│   └── test_routes.py
├── test_ui.py      # Playwright UI 测试
└── screenshots/    # UI 测试截图
```

### 依赖安装 / Dependencies

```bash
pip3 install playwright pytest
python3 -m playwright install chromium
```
