# 工程完善修正计划 / Engineering Improvement Plan

> 生成时间: 2026-04-14
> 目标: 修复 Phase 1-5 + v1.1 积累的工程债务，不加新功能
> 优先级: P0 立即 → P1 本周 → P2 下周 → P3 v2

---

## P0 — 立即修复（1-2 小时）

### P0-1: 修复 dashboard.html 结构性错误

**根本原因:** 模板同时作为独立 HTML 文档（第1行 `<html>`）又继承了 `base.html`（第37行 `{% extends %}`），两个 `<html>/<body>` 嵌套。

**目标:** `statistics/dashboard.html` 语义正确，移除独立的 `<html>/<head>/<body>` 标签，只保留 `{% extends "base.html" %}` 和内容区块。

**怎么做:**
1. 读取 `app/templates/statistics/dashboard.html`
2. 删除顶部的 `<!DOCTYPE html>`, `<html>`, `<head>`, `</head>`, `<body>` 标签
3. 确保只保留 `{% extends "base.html" %}` 和 `{% block content %}` 包裹的内容
4. 运行 UI 测试验证统计页面正常加载

**提升:** 消除浏览器兼容隐患，HTML 语义正确。

---

### P0-2: 补全 requirements.txt

**根本原因:** `paddleocr`, `pdf2image`, `numpy`, `requests` 被代码使用但未写入 requirements.txt，导致新环境无法运行。

**目标:** `pip install -r requirements.txt` 后 OCR 和 LLM 功能完整可用。

**怎么做:**
1. 读取所有源码文件，收集所有 `import` 语句
2. 识别未在 requirements.txt 中的包
3. 追加到 requirements.txt（`paddleocr`, `pdf2image`, `pdf2image` 需要 poppler，`numpy` 通常自动装但显式声明）
4. 运行 `pip freeze > requirements.lock` 生成版本锁定
5. 验证：创建新虚拟环境，`pip install -r requirements.txt`，启动应用，OCR 上传功能可正常初始化

**提升:** 项目可移植性，团队成员和环境重建不破坏功能。

---

### P0-3: run.py 使用 Waitress

**根本原因:** `run.py` 导入了 Waitress 但实际调用 `app.run()`，开发服务器暴露在公网有安全风险。

**目标:** `python run.py` 生产级别启动（支持多线程、端口绑定）。

**怎么做:**
1. 读取 `run.py`
2. 将 `app.run(host='0.0.0.0', port=5002, debug=False)` 替换为 `serve(app, host='0.0.0.0', port=5002)`
3. 添加 `if __name__ == '__main__':` 保护

**提升:** 生产级并发处理，修复"导入了但没用"的工程债务。

---

## P1 — 本周修复

### P1-1: 权限检查逻辑抽取公共方法

**根本原因:** 部门管理员权限检查逻辑（`current_user.is_dept_admin() and user.department_id == ...`）在 admin 路由中复制至少 8 次。

**目标:** 所有 admin 路由不再内联权限检查，改为调用统一的 Service 函数或装饰器参数。

**怎么做:**
1. 在 `app/services/` 下新建 `permission_service.py`
2. 实现 `get_manageable_users_query(current_user)` 返回 `User.query` 的过滤版本
3. 实现 `can_manage_user(current_user, target_user_id)` 判断单用户操作权限
4. 实现 `can_manage_department(current_user, dept_id)` 判断部门操作权限
5. 修改 `admin/routes.py` 中所有涉及权限检查的函数，替换为调用 Service
6. 修改 `decorators.py` 中的 `@admin_required` 支持参数化权限范围

**提升:** 权限逻辑修改只需改一处，bug 不会在 8 个地方遗漏。

---

### P1-2: 清理硬编码 Schema

**根本原因:** `forms.py` 的 `FIELD_SCHEMAS` 和 `llm_service.py` 的 `CERTIFICATE_SCHEMAS` 与数据库中 CertificateType/UserField 动态 schema 并存，造成数据源分裂。

**目标:** 数据库 schema 为唯一数据源，代码中的硬编码种子仅在数据库为空时使用。

**怎么做:**
1. 识别 `forms.py` 中 `FIELD_SCHEMAS` 的使用位置
2. 改为从 `CertificateType.query.all()` 动态读取，删掉硬编码
3. `llm_service.py` 同理，改为从数据库读取 type definitions
4. 仅在 `app/__init__.py` 或 migration 脚本中保留初始种子逻辑（带 `# 仅用于初始化，数据库有值时跳过` 注释）
5. 补全对应的 Service 层单元测试

**提升:** Phase 5 的动态字段管理不再被硬编码绕过，数据一致性得到保证。

---

### P1-3: 补核心服务层单元测试

**根本原因:** `ocr_service.py`(468行)、`llm_service.py`(280行)、`file_storage_service.py`(192行) 完全没有测试，是最大的 bug 风险点。

**目标:** 三大服务层函数有可运行的单元测试，覆盖正常路径和错误路径。

**怎么做:**
```python
# tests/unit/test_services.py 新建
# FileStorageService:
- test_secure_path_rejects_path_traversal()
- test_secure_path_allows_valid_filename()
- test_validate_file_rejects_extension_bypass()
- test_save_file_generates_uuid_and_dated_path()

# OCRService:
- test_detect_type_returns_correct_type_by_keywords()
- test_detect_type_returns_none_for_unknown()
- test_process_image_file_not_found()  # 错误处理

# LLMService:
- test_extract_fields_returns_dict()
- test_extract_fields_handles_llm_unavailable()  # 降级逻辑
```

**提升:** OCR/LLM/FileStorage 的 bug 可被测试捕获，重构有安全网。

---

## P2 — 下周修复

### P2-1: admin/routes.py 路由函数拆分

**根本原因:** admin 路由函数超过 30 行，业务逻辑（数据查询、权限判断、业务处理、响应）全在路由中，无法单元测试。

**目标:** admin 路由函数不超过 30 行，业务逻辑全部移入 `services/admin_service.py`。

**怎么做:**
1. 新建 `app/services/admin_service.py`
2. 从 `admin/routes.py` 抽取:
   - `batch_toggle_admin()` → `AdminService.batch_toggle_admin()`
   - `batch_toggle_disabled()` → `AdminService.batch_toggle_disabled()`
   - `batch_reset_password()` → `AdminService.batch_reset_password()`
   - `batch_delete_user()` → `AdminService.batch_delete_user()`
   - `batch_set_role()` → `AdminService.batch_set_role()`
   - `create_user()` → `AdminService.create_user()`
   - `reset_password()` → `AdminService.reset_password()`
   - `toggle_admin()` / `toggle_disabled()` / `delete_user()` → 对应 Service 方法
3. 路由层只保留: 参数提取 → 调用 Service → 返回响应
4. 补全单元测试覆盖 Service 层

**提升:** admin 业务逻辑可独立测试，路由层简单到不需要测试。

---

### P2-2: 修复 CSRF 豁免问题

**根本原因:** 4 个端点（删除、OCR上传、OCR确认、批量导入）使用 `@csrf.exempt`，绕过了 CSRF 保护。

**目标:** 全部移除 CSRF 豁免，前端正确传递 CSRF token。

**怎么做:**
1. 移除以下路由的 `@csrf.exempt`:
   - `/certificates/<id>/delete`
   - `/certificates/ocr/upload`
   - `/certificates/ocr/confirm`
   - `/certificates/import`
2. 检查 `base.html` 是否通过 meta 标签或全局变量暴露了 CSRF token
3. 如果没有，在 `base.html` 的 `<head>` 添加:
   ```html
   <meta name="csrf-token" content="{{ csrf_token() }}">
   ```
4. 修改前端 JS（`schema-loader.js`, `admin-list.js`）使用:
   ```javascript
   fetch(url, {
     headers: { 'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content }
   })
   ```
5. 验证: 正常提交表单和 AJAX 请求均通过，恶意跨域请求被拦截

**提升:** 消除 4 个安全漏洞，所有状态修改操作均受 CSRF 保护。

---

### P2-3: 批量操作加事务保护

**根本原因:** `batch_delete`, `batch_set_role` 等批量操作在循环中逐条 `session.add()/commit()`，中途失败导致部分成功，数据不一致。

**目标:** 批量操作使用事务，要么全部成功，要么全部回滚。

**怎么做:**
1. 修改 `AdminService.batch_delete_user()`:
   ```python
   def batch_delete_user(user_ids, current_user):
       try:
           users = User.query.filter(User.id.in_(user_ids)).all()
           for user in users:
               db.session.delete(user)
           db.session.commit()  # 一次性提交
       except Exception:
           db.session.rollback()
           raise
   ```
2. 同理修复其他 batch_ 方法
3. 在 Service 测试中添加"中途异常触发 rollback"的测试用例

**提升:** 批量操作的数据一致性有保证，不会出现"删了 5 个剩 3 个"的状态。

---

### P2-4: 初始化 Flask-Migrate

**根本原因:** 依赖 `db.create_all()` 启动时建表，无法做 schema 变更和回滚，`Flask-Migrate` 装了但未用。

**目标:** 数据库迁移通过 Flask-Migrate 管理，支持 schema 版本化和回滚。

**怎么做:**
```bash
flask db init                    # 如果 migrations/ 目录不存在
flask db migrate -m "initial"    # 生成初始迁移
flask db upgrade                 # 应用迁移
```
注意: 当前 SQLite 生产环境可能需要 `flask db stamp head` 来标记当前状态。

**提升:** Schema 变更可追踪、可回滚，生产环境升级不停机。

---

### P2-5: 前端 JS 模块化

**根本原因:** `app/templates/certificates/list.html` 533行，内联 JS 占一半，与业务逻辑混杂，难以维护和测试。

**目标:** 超过 200 行的内联 JS 拆分为独立 `.js` 文件。

**怎么做:**
1. 从 `list.html` 抽取 DataTables 初始化和操作逻辑 → `static/js/cert-list.js`
2. 从 `list.html` 抽取批量选择/操作逻辑 → `static/js/cert-batch.js`
3. 从 `upload.html` 抽取 OCR 上传逻辑 → `static/js/ocr-upload.js`
4. 在对应模板中 `<script src="{{ url_for('static', filename='js/cert-list.js') }}"></script>`
5. 确保所有 JS 使用统一的 CSRF token 获取方式

**提升:** 页面模板可读性提升，JS 可独立测试和复用。

---

## P3 — v2 规划（暂缓）

### P3-1: Docker 部署方案

- Docker + docker-compose（Flask + PostgreSQL + Nginx）
- systemd service 文件
- 部署脚本

### P3-2: 审计日志

- 用户操作审计（登录、修改、删除）
- 证书操作审计
- 独立的 `AuditLog` 模型 + Service

### P3-3: 前端技术栈统一

- 评估是否引入轻量前端框架
- 或统一使用原生 JS + fetch，移除 jQuery

---

## 修正计划汇总表

| ID | 状态 | 维度 | 根本原因 | 目标 | 怎么做 | 提升 |
|----|------|------|---------|------|--------|------|
| P0-1 | ✅ 完成 | 前端 | dashboard.html 同时独立又继承，两个 html/body 嵌套 | HTML 语义正确 | 删除独立标签，只保留 extends | 浏览器兼容隐患消除 |
| P0-2 | ✅ 完成 | 依赖 | requirements.txt 缺 paddleocr/numpy/requests | 新环境可完整运行 | 补全依赖，生成 lock 文件 | 可移植性 |
| P0-3 | ✅ 完成 | DevOps | run.py 导入 Waitress 但用 app.run() | 生产级启动 | 改用 serve() | 并发安全 |
| P1-1 | ✅ 完成 | 架构 | 权限检查复制 8 次，无公共方法 | 统一权限检查函数 | 新建 permission_service.py | 修改一处即可 |
| P1-2 | 🔄 进行中 | 代码质量 | 硬编码 schema 与数据库并存，分裂 | 数据库为唯一数据源 | 删硬编码，改从 DB 读 | 数据一致性 |
| P1-3 | 🔄 进行中 | 测试 | OCR/LLM/FileStorage 服务 0 测试 | 三大服务层有单元测试 | 写 test_ocr_service, test_llm_service, test_file_storage | 重构有安全网 |
| P2-1 | ⏳ 待开始 | 架构 | admin 路由函数超过 30 行，逻辑全内联 | 路由不超过 30 行，业务进 Service | 新建 admin_service.py 抽取业务逻辑 | 可测试性 |
| P2-2 | ✅ 完成 | 安全 | 4 个端点 CSRF 豁免 | 全部受 CSRF 保护 | 移除豁免，前端传 token | 安全漏洞消除 |
| P2-3 | ⏳ 待开始 | 安全 | 批量操作无事务，部分成功风险 | 事务保护，要么全成功要么全回滚 | try/except + rollback | 数据一致性 |
| P2-4 | ⏳ 待开始 | DevOps | db.create_all() 无法迁移 | Flask-Migrate 管理迁移 | init + migrate + upgrade | 可追踪可回滚 |
| P2-5 | ⏳ 待开始 | 前端 | list.html 533行，内联 JS 混杂 | 超过 200 行内联 JS 拆分 | 抽取 cert-list.js, cert-batch.js | 可维护性 |

### 批量上传 OCR 修复记录 (2026-04-23)

| 问题 | 状态 | 修复方案 |
|------|------|---------|
| `int is not defined` | ✅ 已修复 | 改用 `Math.floor(score)` |
| 上传失败 (CSRF) | ✅ 已修复 | 移除 formData 中重复的 csrf_token，只通过 header 发送 |
| 预览只显示第一个文件 | ✅ 已修复 | 改为多文件缩略图网格 |
| 动态字段不显示 | ✅ 已修复 | 实现 `renderDynamicFieldsForType()` |
| 动态字段不保存 | ✅ 已修复 | 收集 `dynamic_*` 输入序列化 |
| 多余的"加入队列"按钮 | ✅ 已移除 | 拖拽自动加入队列 |

---

*此文档为工程修正计划，不新增功能，专注修复已有工程债务。*
