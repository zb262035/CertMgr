# Phase 2: Core — Context

**Gathered:** 2026-03-24
**Status:** Ready for planning
**Source:** discuss-phase via user decisions

---

## Phase Boundary

Full certificate management: upload, list, edit, delete, search, filter, batch import, statistics dashboard.

---

## Decisions

### Certificate List Layout
- **Card layout** — Each certificate displayed as a card with thumbnail preview, title, type, date
- Rationale: Better visual clarity, supports image previews

### Dynamic Fields
- **Single page dynamic switching** — Same form/page, fields change based on selected certificate type
- Rationale: Smoother user experience
- Certificate types: 比赛获奖证书, 荣誉证书, 资格证, 职业技能等级证书

### Search & Filter Location
- **On list page top** — Search box and filters at top of certificate list
- Rationale: Clear and accessible, no extra navigation step

### Statistics Dashboard
- **Detailed statistics** — Time trend charts, department/unit distribution, type breakdown
- Rationale: Richer insights for admin users

### Excel Batch Import
- **Auto-parse without template** — Upload file, system automatically identifies columns
- No template download required
- Rationale: Simpler workflow

### Certificate Edit/Delete
- **Detail page operation** — Open certificate detail page first, then edit/delete
- Rationale: Safer operations, clearer context

### Certificate Entry Flow（Phase 2 补充）
**核心变化：** 从手动填表 → 系统自动识别 + 用户确认

#### 入口方式
- **上传入口**：用户登录后上传证书图片/PDF，单张或批量，支持拖拽
- **目录监控**：指定服务器目录，定时扫描新文件自动识别（适合批量处理）
- 两种方式并存

#### OCR 识别流程
1. 用户上传证书图片/PDF（或放入监控目录）
2. 系统自动识别：
   - **证书类型自动判断**（比赛获奖/荣誉/资格/职业技能）
   - **字段提取**：标题、颁发机构、日期、获奖信息等
3. 识别结果展示给用户**确认/修改**
4. 用户确认后**直接入库**（无需管理员审核）

#### 字段模式（混合）
- **标准证书**（4种固定类型）：定义标准字段模板，OCR 识别结果匹配模板
- **特殊证书**：自由识别，用户确认后存储

#### OCR 技术
- **本地部署 OCR 模型**（如 PaddleOCR）
- 不依赖云服务，保护数据隐私

---

## Canonical References

No external specs — requirements fully captured above.

---

## Deferred Ideas

- Phase 2 原实现（手动填表）需重构为 OCR 自动识别
- 此更新影响：上传页面、编辑页面、证书模型字段设计
