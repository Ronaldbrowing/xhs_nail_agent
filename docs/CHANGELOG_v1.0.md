# Vertical Content Studio v1.0 MVP Checkpoint

**Release Date**: 2026-05-03  
**Checkpoint Tag**: `v1.0-checkpoint`  
**Tag Object SHA**: `507bcfd45e1130851833017ef148c6f2c2ce2ad9`  
**Tag Target Commit**: `4763994c560c3589855dadb544dfe3adc54143ec`  
**Release Branch Source**: `milestone-0-requirements-baseline` @ `0fa3ee4`  
**Main Branch**: `main` (merged via `merge --no-ff`)

---

## Release Summary

v1.0 MVP checkpoint of the Vertical Content Studio nail content generation web app.
Delivers a functional studio UI for generating nail content previews, managing history,
and exporting content packages.

---

## Completed Milestones

| Milestone | Slices | Status |
|-----------|--------|--------|
| M4: Preview Copy & Export | A / B / C / D | ✅ Completed |
| M5: History Enhancement | A / B / C | ✅ Completed |
| M6: History Delete | A / B | ✅ Completed |

---

## Completed Feature Requirements

| FR | Description | Status |
|----|-------------|--------|
| FR-016 | 基础复制与内容使用能力 | ✅ 已完成 |
| FR-017 | 空状态与加载状态 | ✅ 已完成 |
| FR-019 | History 搜索、过滤与排序 | ✅ 已完成 |
| FR-020 | History Item 增强展示与回放保护 | ✅ 已完成 |
| FR-021 | Single Package Export | ✅ 已完成 |
| FR-022 | History 单条删除 | ✅ 已完成 |
| FR-023 | History 批量删除 | ✅ 已完成 |

---

## Key Capabilities Delivered

- **内容生成预览**: 标题 / 正文 / 标签 / 多页结构 / 图片 / 诊断信息
- **History 列表**: 服务端来源，支持搜索 / 过滤 / 排序
- **History replay**: 点击历史记录恢复完整预览
- **Preview copy buttons**: 复制标题 / 正文 / 标签 / 完整内容 / Markdown / JSON
- **JSON / Markdown export**: 触发浏览器下载
- **Single delete**: 单条历史记录删除
- **Bulk delete**: 批量选择 + 批量删除
- **Reference image upload**: 图片参考上传 API
- **Job progress metadata**: 实时任务进度 / stage / elapsed_seconds
- **Acceptance matrix coverage**: `docs/v1_acceptance_matrix.md` FR-016~FR-023 全部完成

---

## Verification

| Check | Result |
|-------|--------|
| `node --check app.js` | ✅ 通过 |
| `py_compile` (app.py, routes.py, schemas.py, history_service.py) | ✅ 通过 |
| 手动浏览器 smoke test | ✅ 通过 |
| `no dedicated e2e automation added` | ✅ 确认 |

---

## Deferred Items (Not in v1.0 Scope)

The following items are documented but not addressed in v1.0:

- `local_path` 文件选择器上传仍待人工点验（FR-002 备注）
- Cases 空态全量人工点验可后续补充（FR-017 备注）
- `created_at` backfill — 旧 package `created_at` 缺失，排序 fallback 不稳定
- `has_package` semantics — 仅基于文件存在性，未校验内容有效性
- History pagination — 无分页参数，大数据集时全表扫描
- soft delete / trash / restore / undo
- no-refresh precise state synchronization（当前使用 `window.location.reload()`）
- e2e automation framework
- artifact hygiene follow-up

---

## Release Integrity

- `origin/main` pushed: `4763994` ✅
- `v1.0-checkpoint` tag pushed: `507bcfd` → `4763994` ✅
- No release blockers at time of v1.0 finalization ✅
- Tracked working tree clean at time of merge ✅

---

*Next: v1.1 — See `docs/v1.1_backlog.md` for planned slices and priority.*