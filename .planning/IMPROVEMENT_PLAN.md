# CertMgr 改进计划 / Improvement Plan

> 日期 / Date: 2026-04-14
> 完成日期 / Completion Date: 2026-04-17
> 基于 / Based on: RETROSPECTIVE.md 复盘报告

---

## 执行状态 / Execution Status

**✅ 全部完成 / All Completed — 2026-04-17**

| 阶段 | 状态 | 说明 |
|------|------|------|
| P0 0.1 | ✅ 完成 | dashboard.html 双重 HTML 标签修复 |
| P0 0.2 | ✅ 完成 | requirements.txt 补全 paddleocr/pdf2image/numpy/requests |
| P0 0.3 | ✅ 完成 | run.py 已使用 Waitress 生产模式 |
| P1 1.1 | ✅ 完成 | `permission_service.py` 统一权限检查，8 个 admin 路由已重构 |
| P1 1.2 | ✅ 完成 | `get_field_schemas()` 从数据库加载，`SEED_SCHEMAS` 仅作空库种子 |
| P1 1.3 | ✅ 完成 | CSRF 豁免已移除，4 个端点正确传递 token |
| P2 2.1 | ✅ 完成 | `user_service.py` 拆分 admin 业务逻辑，12 个函数 |
| P2 2.2 | ✅ 完成 | Flask-Migrate 已初始化，`migrate = Migrate(app, db)` 已添加 |
| P2 2.3 | ✅ 完成 | 所有批量操作已加 `try/except + rollback` 事务保护 |
| P3 3.1 | ✅ 完成 | 99 个单元测试（permission/file_storage/ocr/certificate_service） |
| P3 3.2 | ✅ 完成 | 27 个权限边界 API 测试（admin routes） |
| P4 4.1 | ✅ 完成 | Dockerfile/docker-compose.yml/.env.example/wsgi.py/start.sh/nginx.conf |
| P4 4.2 | ✅ 完成 | `SESSION_COOKIE_*` 配置 + MIME 类型检查 |

---

## 改进条目格式说明 / Item Format

每条改进包含：
- **根因 / Root Cause** — 一句话说清问题本质
- **目标 / Goal** — 一句话说清要达到什么状态
- **做法 / How** — 具体执行步骤
- **提升 / Improvement** — 一句话说清对项目的好处

---

## P0: 立即修复（不影响现有功能，风险极低）/ Immediate Fixes

### 0.1 修复 dashboard.html 结构错误

- **根因 / Root Cause:** 模板同时写了完整 HTML 结构和 `extends base.html`，导致双重标签嵌套。
- **目标 / Goal:** 模板只继承 `base.html`，去掉多余的 `<html>/<head>/<body>` 包裹。
- **做法 / How:**
  1. 打开 `app/templates/statistics/dashboard.html`
  2. 删除 `{% extends "base.html" %}` 之前的完整 HTML 头部（`<!DOCTYPE>`, `<html>`, `<head>`, `<body>` 开始标签）
  3. 删除文件末尾的 `</body></html>`
  4. 保留 `{% block content %}...{% endblock %}` 内的统计内容
- **提升 / Improvement:** 消除 HTML 语义错误，避免未来浏览器兼容问题。

### 0.2 补全 requirements.txt

- **根因 / Root Cause:** 只手动列了部分依赖，缺少 OCR 和 LLM 相关包。
- **目标 / Goal:** `pip install -r requirements.txt` 后能运行所有功能。
- **做法 / How:**
  1. 在当前虚拟环境中运行 `pip freeze > requirements.lock`
  2. 检查 `requirements.txt`，补充缺失的包：`paddleocr`, `pdf2image`, `numpy`, `requests`
  3. 为每个包标注最低版本要求
- **提升 / Improvement:** 换机器部署时不再因缺依赖而报错。

### 0.3 run.py 使用 Waitress 启动

- **根因 / Root Cause:** import 了 Waitress 但实际用 `app.run()`（Flask 开发服务器）。
- **目标 / Goal:** 生产模式用 Waitress，开发模式保留 `app.run()` 调试支持。
- **做法 / How:**
  1. 修改 `run.py`，在非 debug 模式下使用 `waitress.serve()`
  2. 保留 `debug=True` 时走 `app.run()` 用于开发热重载
  ```python
  if __name__ == '__main__':
      if os.getenv('FLASK_ENV') == 'development':
          app.run(debug=True, port=5002)
      else:
          serve(app, host='0.0.0.0', port=5002)
  ```
- **提升 / Improvement:** 生产环境使用生产级 WSGI 服务器，性能和稳定性有保障。

---

## P1: 代码质量修正（本周）/ Code Quality Fixes

### 1.1 统一权限检查逻辑

- **根因 / Root Cause:** 部门管理员权限限制逻辑在 8 个路由函数中重复复制粘贴。
- **目标 / Goal:** 所有权限检查收敛为一个函数，路由层只调用一次。
- **做法 / How:**
  1. 在 `app/decorators.py` 或新建 `app/services/permission_service.py` 中创建：
     ```python
     def get_manageable_users(current_user):
         """获取当前用户可管理的用户查询集"""
         if current_user.is_school_admin():
             return User.query
         elif current_user.is_dept_admin():
             return User.query.filter_by(department_id=current_user.department_id)
         return User.query.filter_by(id=current_user.id)

     def get_manageable_user(current_user, target_user_id):
         """获取单个可管理用户，无权限返回 None"""
         user = User.query.get(target_user_id)
         if not user:
             return None
         if current_user.is_school_admin():
             return user
         if current_user.is_dept_admin():
             if user.department_id == current_user.department_id and not user.is_school_admin():
                 return user
         return None
     ```
  2. 逐个替换 `admin/routes.py` 中的重复权限检查（`toggle_admin`, `toggle_disabled`, `reset_password`, `delete_user`, `set_user_role`, `batch_set_role`, `batch_reset_password`, `batch_delete`）
  3. 每替换一个函数，运行测试确认无回归
- **提升 / Improvement:** 权限逻辑变更只需改一处，彻底消除"改了七处忘了第八处"的风险。

### 1.2 清理硬编码 Schema

- **根因 / Root Cause:** Phase 5 做了数据库动态字段管理，但代码中的硬编码 Schema 仍作为"降级"保留，造成数据源分裂。
- **目标 / Goal:** 以数据库为唯一 schema 来源，硬编码只用于数据库为空时的种子初始化。
- **做法 / How:**
  1. 在 `app/forms.py` 中，将 `FIELD_SCHEMAS` 改为 `get_field_schemas()` 函数，优先从数据库读取：
     ```python
     def get_field_schemas():
         """从数据库加载 schema，数据库为空时返回种子数据"""
         types = CertificateType.query.all()
         if types:
             return {t.name: t.get_field_schema() for t in types}
         return SEED_SCHEMAS  # 只在数据库空时使用
     ```
  2. 在 `llm_service.py` 中同理，`CERTIFICATE_SCHEMAS` 改为从数据库动态获取
  3. 保留 `SEED_SCHEMAS` 作为数据库初始化种子（仅在迁移脚本中使用）
  4. 测试：确认数据库有数据时走动态加载，空数据库时走种子
- **提升 / Improvement:** 消除"改了数据库 schema 但表单还是旧的"不一致问题。

### 1.3 修复 CSRF 豁免

- **根因 / Root Cause:** 为了方便用 AJAX 调用，直接 `@csrf.exempt` 绕过了保护。
- **目标 / Goal:** 所有状态修改端点正确传递和验证 CSRF token。
- **做法 / How:**
  1. 在 `base.html` 的 `<head>` 中添加 CSRF token meta 标签：
     ```html
     <meta name="csrf-token" content="{{ csrf_token() }}">
     ```
  2. 在前端 JS 中，所有 AJAX 请求添加 header：
     ```javascript
     fetch(url, {
         method: 'POST',
         headers: {
             'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
         }
     })
     ```
  3. 移除以下端点的 `@csrf.exempt`：
     - `/certificates/<id>/delete`
     - `/certificates/ocr/upload`
     - `/certificates/ocr/confirm`
     - `/certificates/import`
  4. 逐一测试确认 AJAX 请求正常
- **提升 / Improvement:** 消除 CSRF 攻击面，所有写操作都有 token 验证。

---

## P2: 架构改进（下周）/ Architecture Improvements

### 2.1 拆分 admin 路由，建立 Service 层

- **根因 / Root Cause:** 业务逻辑直接写在路由函数里，admin 模块没有 Service 层。
- **目标 / Goal:** 每个蓝图都有对应的 service 模块，路由只负责 HTTP 请求/响应。
- **做法 / How:**
  1. 创建 `app/services/user_service.py`，从 `admin/routes.py` 提取：
     - `create_user(username, password, role, department_id, extra_fields)`
     - `batch_set_department(user_ids, department_id, operator)`
     - `batch_set_role(user_ids, role, operator)`
     - `batch_reset_password(user_ids)`
     - `batch_delete_users(user_ids, operator)`
     - `toggle_admin(user_id, operator)`
     - `toggle_disabled(user_id, operator)`
  2. 创建 `app/services/department_service.py`，从 `departments/routes.py` 提取
  3. 路由层只做：参数提取 → 调用 service → 返回响应
  4. 为每个新 service 函数写单元测试
- **提升 / Improvement:** 业务逻辑可独立测试，路由文件从 500+ 行降到 100-150 行。

### 2.2 引入 Flask-Migrate 正式迁移

- **根因 / Root Cause:** 依赖 `db.create_all()` 启动建表，无法做 schema 变更和回滚。
- **目标 / Goal:** 所有数据库变更通过迁移脚本管理，支持 upgrade/downgrade。
- **做法 / How:**
  1. 运行 `flask db init`（如果 migrations/ 目录结构不完整）
  2. 运行 `flask db migrate -m "capture current state"` 生成当前 schema 的迁移
  3. 验证 `flask db upgrade` 在空数据库上能正确建表
  4. 在 `create_app()` 中移除 `db.create_all()` 调用
  5. 文档化迁移流程
- **提升 / Improvement:** 未来任何表结构变更都有迁移记录，可回滚、可追踪。

### 2.3 批量操作加事务保护

- **根因 / Root Cause:** 批量操作在循环中逐条处理，没有用数据库事务包裹。
- **目标 / Goal:** 批量操作要么全部成功，要么全部回滚。
- **做法 / How:**
  1. 在 service 层（见 2.1）的批量方法中包裹事务：
     ```python
     def batch_delete_users(user_ids, operator):
         manageable = get_manageable_users(operator)
         users = manageable.filter(User.id.in_(user_ids)).all()
         try:
             for user in users:
                 db.session.delete(user)
             db.session.commit()
         except Exception:
             db.session.rollback()
             raise
     ```
  2. 路由层捕获异常返回友好错误信息
- **提升 / Improvement:** 批量操作不再出现"删了一半报错"的数据不一致。

---

## P3: 测试补全（持续）/ Test Coverage

### 3.3 OCR 速度优化（v1.2）/ OCR Speed Optimization

- **根因 / Root Cause:** LLM 字段提取使用 `deepseek-r1:8b`（thinking 模型），推理时间长（5-15秒），导致 OCR 总耗时 15-20秒。
- **目标 / Goal:** OCR 总耗时降到 3-5 秒。
- **做法 / How:**
  1. **简化 prompt** — 减少输入 token，移除冗长的说明文字
  2. **用非 thinking 模型** — 切换到 `qwen2.5vl:7b`（已实施，降到 7-8秒）
  3. **进一步测试更小模型** — `qwen2.5vl:3b` 或其他轻量 vision 模型
  4. **规则匹配降级** — 对简单证书类型（如毕业证）用关键词匹配代替 LLM
- **提升 / Improvement:** 用户体验提升，OCR 从"等待明显"变成"几乎即时"。

### 3.1 补服务层单元测试

- **根因 / Root Cause:** Phase 3-5 的核心服务（OCR/LLM/FileStorage）无任何测试覆盖。
- **目标 / Goal:** 所有 service 函数有对应的单元测试，覆盖正常路径和边界情况。
- **做法 / How:**
  1. `tests/unit/test_file_storage.py`
     - `test_validate_file_allowed_extensions` — 合法扩展名通过
     - `test_validate_file_disallowed_extensions` — 非法扩展名拒绝
     - `test_validate_file_size_limit` — 超大文件拒绝
     - `test_secure_path_prevents_traversal` — 路径穿越防护
     - `test_save_creates_date_directory` — 按日期分目录存储
     - `test_delete_removes_file` — 删除文件
     - `test_delete_nonexistent_raises` — 删除不存在的文件
  2. `tests/unit/test_ocr_service.py`
     - `test_detect_type_by_keywords` — 关键词识别证书类型
     - `test_detect_type_fallback` — 无法识别时的降级
     - `test_preprocess_image_grayscale` — 灰度处理
     - `test_extract_from_pdf` — PDF 文字提取
     - `test_quality_assessment_high_confidence` — 高置信度质量评估
  3. `tests/unit/test_certificate_service.py`
     - `test_parse_excel_valid_file` — 有效 Excel 解析
     - `test_parse_excel_invalid_format` — 无效格式报错
     - `test_parse_excel_missing_columns` — 缺少必要列报错
  4. `tests/unit/test_permission_service.py`（配合 2.1 新建）
     - 部门管理员可管理本部门用户
     - 部门管理员不能管理其他部门
     - 部门管理员不能管理校级管理员
     - 校级管理员可管理所有用户
- **提升 / Improvement:** 核心业务逻辑有测试保护，重构不再"改了不知道哪里会炸"。

### 3.2 补权限边界 API 测试

- **根因 / Root Cause:** 现有 API 测试只覆盖了"能跑通"，没有测试权限边界。
- **目标 / Goal:** 每种角色 × 每种操作的权限组合都有测试。
- **做法 / How:**
  1. 在 `tests/api/test_routes.py` 中添加：
     - 普通用户访问 admin 路由 → 403
     - 部门管理员操作非本部门用户 → 403
     - 部门管理员操作校级管理员 → 403
     - 部门管理员操作本部门普通用户 → 200
     - 校级管理员操作任意用户 → 200
  2. 每个批量操作端点同理测试
- **提升 / Improvement:** 权限漏洞在测试阶段就能被捕获。

---

## P4: 部署准备（v2 前）/ Deployment Readiness

### 4.1 Docker 部署方案

- **根因 / Root Cause:** 没有容器化部署方案，部署依赖手动环境配置。
- **目标 / Goal:** `docker-compose up` 一键启动完整应用。
- **做法 / How:**
  1. 创建 `Dockerfile`（Python 基础镜像 + PaddleOCR 依赖）
  2. 创建 `docker-compose.yml`（Flask + PostgreSQL + Nginx）
  3. 创建 `.env.example` 模板
  4. 创建 Nginx 反向代理配置
  5. 测试 `docker-compose up` 完整流程
- **提升 / Improvement:** 部署从"手动配环境"变成"一条命令"。

### 4.2 生产配置加固

- **根因 / Root Cause:** 生产环境缺少安全配置（Session cookie、HTTPS、密码复杂度）。
- **目标 / Goal:** 生产配置满足基本安全标准。
- **做法 / How:**
  1. `config.py` 的 `ProductionConfig` 添加：
     ```python
     SESSION_COOKIE_SECURE = True
     SESSION_COOKIE_HTTPONLY = True
     SESSION_COOKIE_SAMESITE = 'Lax'
     ```
  2. 添加密码复杂度验证（最少 8 字符 + 大小写 + 数字）
  3. 文件上传增加 MIME 内容检测（`python-magic`）
- **提升 / Improvement:** 满足生产环境基本安全要求。

---

## 执行顺序依赖图 / Dependency Graph

```
P0 (立即) ─────────────────────────────────────────────
  0.1 dashboard.html 修复     ── 无依赖
  0.2 requirements.txt 补全   ── 无依赖
  0.3 Waitress 启动           ── 无依赖
  三者可并行执行

P1 (本周) ─────────────────────────────────────────────
  1.1 统一权限检查             ── 无依赖（但 2.1 会用到）
  1.2 清理硬编码 Schema        ── 无依赖
  1.3 修复 CSRF 豁免           ── 无依赖
  三者可并行执行

P2 (下周) ─────────────────────────────────────────────
  2.1 拆分 admin Service 层   ── 依赖 1.1（权限逻辑已统一）
  2.2 Flask-Migrate           ── 无依赖（但建议在 2.1 之前做）
  2.3 批量操作事务保护         ── 依赖 2.1（service 层建立后才有地方加事务）

P3 (持续) ─────────────────────────────────────────────
  3.1 服务层单元测试           ── 依赖 2.1（service 层建好后测 service）
  3.2 权限边界 API 测试        ── 依赖 1.1（权限逻辑统一后测边界）

P4 (v2 前) ────────────────────────────────────────────
  4.1 Docker 部署             ── 依赖 0.2（依赖完整后再容器化）
  4.2 生产配置加固             ── 无依赖
```

---

*此计划基于 RETROSPECTIVE.md 复盘报告制定，按优先级从 P0 到 P4 分级执行。*
*This plan is based on the RETROSPECTIVE.md retrospective report, prioritized from P0 to P4.*
