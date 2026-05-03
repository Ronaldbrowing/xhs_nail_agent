# post-v1.0 Hygiene Inventory

**Date**: 2026-05-03  
**Branch**: `v1.1-slice-a-artifact-hygiene`  
**Purpose**: Record current untracked file inventory; take no destructive action.

---

## Overview

After v1.0 release, the working tree contains numerous untracked files that were
generated during development and testing. This document classifies them and
determines which should be covered by `.gitignore` vs. left for manual decision.

**Policy**: No automatic deletion in this slice. Files are either ignored or left
as-is for future manual review.

---

## Untracked File Classification

### Category A — Should Be Ignored (Add to `.gitignore`)

These are generated runtime artifacts that should never be committed:

| Pattern | Count | Description |
|---------|-------|-------------|
| `case_library/poster/case_*/image.png` | ~40 | Generated case images |
| `case_library/ppt/case_*/` | ~1 | Empty generated directory |
| `case_library/product/case_*/` | ~1 | Empty generated directory |
| `case_library/infographic/` | 1 | Empty generated directory |
| `case_library/teaching/` | 1 | Empty generated directory |
| `case_library/poster/case_ref_test/` | 1 | Test artifact |
| `case_library/poster/case_test_001/` | 1 | Test artifact |
| `input/` | 1 | Local upload staging directory |
| `tools/` | 1 | Dev utility scripts |
| `examples/` | 1 | Example scripts |
| `*.png / *.jpg / *.jpeg / *.webp / *.gif` | — | Already in .gitignore but overlapping |
| `AGENTS.md` | 1 | Workspace agent config |

### Category B — Curated Sample (Do NOT Ignore — Archive Later)

These are real generated case images that may have future value as curated samples:

| Pattern | Count | Recommendation |
|---------|-------|----------------|
| `case_library/poster/case_001_*` through `case_009_*` | ~9 | May be useful as sample cases. Do NOT bulk ignore. Manual review before adding to curated set. |
| `case_library/poster/case_017_*` | 1 | Has Chinese metadata describing content |
| `case_library/poster/case_019_*`, `case_021_*`, `case_024_*` | 3 | "春日限定樱花冰透美甲" theme |
| `case_library/poster/case_025_*` | 1 | Cat image (橘猫) — unrelated to nail |
| `case_library/poster/case_026_*` | 1 | 封面图 |
| `case_library/poster/case_027_*` | 1 | 细节特写 |
| `case_library/poster/case_028_*` | 1 | 肤色对比图 |
| `case_library/poster/case_030_*` | 1 | 生活场景图 |
| `case_library/poster/case_032_*` | 1 | 抓点击 |
| `case_library/poster/case_033_*` | 1 | 猫眼光泽 |
| `case_library/poster/case_034_*` | 1 | 黄皮显白 |
| `case_library/poster/case_035_*` | 1 | 颜色甲型质感 |
| `case_library/poster/case_036_*` | 1 | 生活方式代入 |
| `case_library/poster/case_037_*` | 1 | 美甲笔记总结 |
| `case_library/poster/case_038_*` | 1 | 抓点击 |
| `case_library/poster/case_040_*` | 1 | 黄皮显白 |
| `case_library/poster/case_041_*` | 1 | 颜色甲型质感 |
| `case_library/poster/case_042_*` | 1 | 生活方式代入 |
| `case_library/poster/case_043_*` | 1 | 美甲笔记总结 |
| `case_library/poster/case_044_*` | 1 | 抓点击 |
| `case_library/poster/case_045_*` | 1 | 猫眼光泽 |
| `case_library/poster/case_046_*` | 1 | 黄皮显白 |
| `case_library/poster/case_047_*` | 1 | 颜色甲型质感 |
| `case_library/poster/case_048_*` | 1 | 生活方式代入 |
| `case_library/poster/case_049_*` | 1 | 美甲笔记总结 |

### Category C — Workspace Internal Docs (Do NOT Ignore)

These are valid documentation files that happen to be untracked:

| Path | Description |
|------|-------------|
| `docs/superpowers/plans/2026-04-29-nail-web-mvp.md` | Workspace planning doc |
| `docs/Vertical Content Studio MVP v1.0 产品需求、技术方案与验收基准.md` | Large requirements doc |

### Category D — Untracked Tests (Do NOT Delete)

| Path | Status |
|------|--------|
| `tests/test_phase05_e2e_strict.py` | Untracked test file. Not currently integrated into CI. Do NOT delete — represents testing work in progress. |

---

## Recommended `.gitignore` Additions

```
# Case library generated images — always generated at runtime
case_library/poster/*/image.png
case_library/ppt/
case_library/product/
case_library/infographic/
case_library/teaching/

# Reference test artifacts
case_library/poster/case_ref_test/
case_library/poster/case_test_001/

# Local runtime staging
input/
tools/
examples/

# Workspace agent config (personal)
AGENTS.md
```

**NOT adding to gitignore** (Category B + C):
- `case_library/poster/case_001_*` through `case_049_*` metadata.json + image.png pairs — these are potentially curated samples; manual review needed before ignoring
- `docs/` — valid docs, not artifacts
- `tests/test_phase05_e2e_strict.py` — testing artifact, keep for future integration

---

## Files Explicitly NOT Deleted

The following were inspected and intentionally NOT deleted:

- `tests/test_phase05_e2e_strict.py` — untracked test artifact, not deleted per user constraint
- `case_library/poster/case_013_untitled/` — potentially valid case metadata, left for manual review
- `case_library/poster/case_025_一只可爱的橘猫坐在窗台上/` — cat image not nail-related, but left for manual review

---

## Audit Trail

| Date | Action |
|------|--------|
| 2026-05-03 | Created inventory; added `.gitignore` rules for Category A runtime artifacts |
| 2026-05-03 | Did NOT delete any files — dry-run only |
| 2026-05-03 | Did NOT modify business code |