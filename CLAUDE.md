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

## 项目信息 / Project Info

- **项目路径:** /Users/ice/PycharmProjects/CertMgr
- **类型:** Python Flask Web Application
- **状态:** Phase 1 已完成，Phase 2 已完成（CRUD、搜索、统计、OCR）

## 技术栈 / Tech Stack

- Python 3.11+
- Flask 3.1.x + Flask-SQLAlchemy
- PostgreSQL 15+ (开发用 SQLite)
- Bootstrap 5.3.8
- Waitress 3.0.x
