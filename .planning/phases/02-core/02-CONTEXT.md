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

---

## Canonical References

No external specs — requirements fully captured above.

---

## Deferred Ideas

None — all Phase 2 scope addressed.
