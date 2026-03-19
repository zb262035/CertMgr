# CertMgr 项目综合摘要 / SUMMARY

**项目:** 学校证书管理系统 (School Certificate Management System)
**生成日期:** 2026-03-19
**状态:** 研究阶段完成 ✓ → 等待规划

---

## 1. 项目定位 / Project Scope

**一句话描述：** 数字化管理全校教职工的各类证书，支持上传、存储、搜索、统计和导出打印。

**目标用户：** ~1000名教职工 + 若干管理员
**部署环境：** 学校内部服务器（Windows Server 或 Linux）
**用户规模：** 1000人，100-5000张证书（估算）

---

## 2. 技术栈推荐 / Recommended Stack

### 核心框架

| 技术 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.11 LTS | 运行时 |
| **Flask** | 3.1.x | Web框架 |
| **Flask-SQLAlchemy** | 3.1.x | ORM |
| **Flask-Migrate** | 4.1.x | 数据库迁移 |
| **Flask-Login** | 0.6.x | 会话管理 |
| **Flask-WTF** | 1.2.x | 表单+CSRF |

### 数据库

| 技术 | 版本 | 用途 |
|------|------|------|
| **PostgreSQL** | 15+ | **推荐生产数据库** |
| **SQLite** | — | 仅限开发/测试 |

**注意：** 研究建议 PostgreSQL > SQLite，原因：并发支持更好、ACID更可靠、备份更简单。但 v1 可用 SQLite 快速起步。

### 前端

| 技术 | 版本 | 用途 |
|------|------|------|
| **Bootstrap** | 5.3.8 | UI框架 |
| **DataTables** | 1.11+ | 表格/分页/搜索 |

### 文件处理 & PDF

| 技术 | 版本 | 用途 |
|------|------|------|
| **Pillow** | 12.1.x | 图片处理/缩略图 |
| **ReportLab** | 4.4.x | PDF生成 |

**注意：** 不用 WeasyPrint（依赖系统库，Windows部署困难）

### WSGI 服务器

| 技术 | 版本 | 用途 |
|------|------|------|
| **Waitress** | 3.0.x | **Windows兼容WSGI服务器** |

**注意：** 不用 Gunicorn（Unix-only，Windows不支持）

---

## 3. 架构设计 / Architecture

### 项目结构

```
CertMgr/
├── app/
│   ├── __init__.py          # 应用工厂
│   ├── config.py            # 配置类
│   ├── extensions.py        # 共享扩展实例
│   ├── models/              # 数据模型
│   │   ├── user.py
│   │   ├── certificate.py
│   │   ├── certificate_type.py
│   │   └── field_definition.py
│   ├── blueprints/          # 模块化路由
│   │   ├── auth/            # 认证模块
│   │   ├── certificates/    # 证书CRUD
│   │   ├── admin/           # 管理功能
│   │   └── api/             # REST API(未来)
│   ├── services/            # 业务逻辑层
│   │   ├── certificate_service.py
│   │   ├── file_storage_service.py
│   │   ├── auth_service.py   # 可插拔认证
│   │   └── export_service.py
│   └── static/uploads/     # 证书文件存储
├── instance/                # 实例特定文件(不进入git)
├── migrations/              # Alembic迁移
├── tests/
└── run.py
```

### 核心设计决策

#### 3.1 动态证书字段 — JSONB方案

不同证书类型字段差异大，用 JSONB 存储动态字段，而不是每种类型单独表：

```sql
certificates (
    id, user_id, certificate_type_id,
    title, issuer, issue_date,
    file_path, file_hash, original_filename,
    dynamic_fields JSONB,  -- 动态字段
    created_at, updated_at
)
```

好处：字段灵活、查询方便（GIN索引）、无需每次改表

#### 3.2 可插拔认证架构

```
AUTH_BACKEND = 'local'   # v1: 本地账号
AUTH_BACKEND = 'sso'     # 未来: OA/企业微信/统一身份认证
```

定义 AuthAdapter 接口，未来换认证方式不改业务代码。

#### 3.3 文件存储 — UUID命名

上传文件重命名为 UUID，原始文件名存数据库：
```
/uploads/2026/03/{uuid}.pdf
```

防止：文件名冲突、中文编码问题、路径遍历攻击

---

## 4. 功能分级 / Feature Tiers

### 4.1 基础功能（必须有）

- [ ] 用户注册/登录/登出
- [ ] 角色：普通用户（看自己）、管理员（看全部）
- [ ] 单文件上传/下载
- [ ] 证书列表+分页
- [ ] 按姓名搜索

### 4.2 核心功能（功能完整）

- [ ] 多文件上传
- [ ] 批量导入（Excel）
- [ ] 动态元数据字段（不同证书类型不同字段）
- [ ] 多条件筛选（类型/日期/颁发机构）
- [ ] 统计面板（数量/趋势）
- [ ] PDF导出/打印

### 4.3 增强功能（未来）

- [ ] OCR自动提取证书文字
- [ ] 证书过期提醒
- [ ] 自定义证书模板
- [ ] 审计日志

---

## 5. 分阶段计划 / Phased Roadmap

### Phase 1: 基础架构 (Foundation)

**目标：** 搭建可运行的项目框架

1. Flask 应用工厂模式
2. 数据库模型（用户、证书、证书类型）
3. 认证模块（本地账号）
4. 文件存储服务

**交付物：** 能注册/登录/上传下载的最简单版本

### Phase 2: 核心功能 (Core)

**目标：** 完整的业务功能

1. 证书 CRUD + 动态字段
2. 多条件搜索/筛选
3. 管理员批量导入（Excel）
4. 统计面板

**交付物：** 满足主要业务需求

### Phase 3: 增强 (Enhancement)

**目标：** 提升体验

1. PDF导出/打印
2. OCR自动识别
3. SSO集成（可选）
4. 审计日志

**交付物：** 完整的生产系统

---

## 6. 已知风险 / Known Risks

| 风险 | 严重性 | 应对 |
|------|--------|------|
| Windows Server 部署兼容性 | 高 | 用 Waitress + pathlib |
| 中文文件名/字体 | 高 | UUID存储 + 捆绑中文字体 |
| JSONB 搜索性能 | 中 | GIN索引 + 适当索引策略 |
| Unicode 规范化 | 中 | 统一 NFC 标准化 |
| 数据库连接池 | 中 | SQLite 用 WAL，PG 用连接池 |

---

## 7. 研究置信度 / Confidence

| 领域 | 置信度 | 原因 |
|------|--------|------|
| 技术栈版本 | 高 | PyPI 验证 (2026-02/03) |
| Flask 架构 | 高 | 官方文档 |
| Windows 部署 | 中 | 因学校 IT 环境而异，需实测 |
| OCR 方案 | 低 | 待 Phase 3 再评估 |

---

*基于 4 个维度研究：Features / Architecture / Pitfalls / Stack*
