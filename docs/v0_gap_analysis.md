# Web MVP v0 与 Vertical Content Studio MVP v1.0 差距分析

- **来源文档**：docs/v1.md
- **生成日期**：2026-04-30
- **当前阶段**：Milestone 0
- **扫描范围**：verticals/nail/, tests/, src/, project_paths.py, output/

---

## 概述

本文档对比 Web MVP v0 现有代码与 Vertical Content Studio MVP v1.0 目标之间的差距。差距分析基于代码扫描结果，不基于推测。

---

## 差距分析矩阵

| FR | v1.0 目标 | 当前代码证据 | 当前判断 | 差距 | 风险 | 建议 Milestone | 优先级 |
|---|---|---|---|---|---|---|---|
| FR-000 | GET /api/verticals 返回可用垂类列表 | **未找到** `/api/verticals` 路由或 endpoint | 未满足 | 无 /api/verticals 接口 | 高：无法获取 vertical 列表 | Milestone 1 | P0 |
| FR-000 | 前端显示当前 selectedVertical | `app.js` 第 3 行：`currentVertical: "nail"` 写死 | 部分满足 | vertical 以常量写死，非动态状态 | 高：无法切换 vertical | Milestone 2 | P0 |
| FR-000 | 未知 vertical 返回 4xx | **未找到** 校验逻辑 | 未满足 | 无 unknown vertical 校验 | 高：可能 fallback 到 nail | Milestone 1 | P0 |
| FR-001 | POST /api/verticals/{vertical}/notes 创建任务 | **已存在** `routes.py` 第 94 行：`POST /api/nail/notes` | 部分满足 | 旧路径已存在，新通用路径未实现 | 中：旧接口可作为兼容层 | Milestone 2 | P0 |
| FR-002 | reference_source 三模式互斥校验 | **未找到** 后端互斥校验逻辑 | 未满足 | 无后端校验 | 高：前后端未同步校验 | Milestone 2 | P0 |
| FR-003 | POST /api/verticals/{vertical}/reference-images | **已存在** `routes.py` 第 58 行：`POST /api/nail/assets/reference-image` | 部分满足 | 旧路径已存在，新路径未实现 | 低：功能已存在 | Milestone 2 | P1 |
| FR-004 | GET /api/jobs/{job_id} 返回 stage/elapsed_seconds | **已存在** `routes.py` 第 106 行：`GET /api/jobs/{job_id}`，`schemas.py` 有 `stage`/`elapsed_seconds` 字段 | 部分满足 | schema 有字段，需验证 job_store 是否填充 | 低：字段可能未填充 | Milestone 3 | P0 |
| FR-005 | Preview 展示标题/正文/标签/多页/图片/诊断 | `app.js` 第 348-349 行设置 `noteSummary.innerHTML`/`pagesGrid.innerHTML`，第 994 行设置 `container.innerHTML` | 有风险 | **使用 innerHTML 渲染用户可控内容**（见备注） | 高：XSS 风险 | Milestone 3 | P0 |
| FR-006 | GET /api/verticals/{vertical}/notes 服务端历史 | **未找到** `/api/verticals/{vertical}/notes` 路由 | 未满足 | 无服务端历史列表 API | 高：历史依赖 localStorage | Milestone 1 | P0 |
| FR-006 | 清空 localStorage 后历史仍可恢复 | `app.js` 第 228-260 行：`saveLastJob()`/`loadLastJob()` 使用 localStorage | 未满足 | localStorage 是唯一历史来源 | 高：换浏览器/清缓存后无历史 | Milestone 1 | P0 |
| FR-007 | GET /api/verticals/{vertical}/notes/{note_id}/package | **已存在** `routes.py` 第 114 行：`GET /api/nail/notes/{note_id}/package` | 部分满足 | 旧路径已存在，新路径未实现；`_ensure_output_path()` 有路径安全校验 | 低：功能已存在 | Milestone 1 | P0 |
| FR-008 | GET /api/verticals/{vertical}/cases 案例库列表 | **未找到** 案例库 API（仅 `case_library.py` 脚本，无 Web API） | 未满足 | 无案例库 Web API | 高：无案例库前端入口 | Milestone 2 | P0 |
| FR-008 | 案例库前端 UI | **未找到** 案例库 HTML/JS 模块 | 未满足 | 无案例库 UI | 高：case_id 只能手动输入 | Milestone 2 | P0 |
| FR-009 | 静态资源路径安全 | `app.py` 第 24-26 行：静态文件挂载在 `/static/output` 和 `/static/input` | 部分满足 | 需验证路径穿越防护 | 低：路径安全已实现 | Milestone 1 | P1 |
| FR-010 | job 404 fallback 到 package | `routes.py` 第 121-128 行：`find_job_by_note_id()` fallback 逻辑 | 部分满足 | fallback 已存在但需验证覆盖场景 | 低：已有 fallback | Milestone 3 | P1 |
| FR-011 | 前端不得 innerHTML 渲染用户内容 | `app.js` 第 348, 349, 994 行使用 innerHTML | 有风险 | innerHTML 用于渲染 note 内容 | 高：XSS 风险 | Milestone 3 | P0 |
| FR-012 | note_package.json 包含 content_platform/content_type/vertical | `output/` 下多个 `note_package.json` **均缺少** `content_platform`、`content_type`、`vertical` 字段 | 未满足 | 旧 package 缺少 v1.0 必需字段 | 高：无法按 vertical 过滤历史 | Milestone 1 | P0 |
| FR-013 | Vertical Adapter 架构 | **未找到** Vertical Registry 或 Adapter 实现 | 未满足 | 无多 vertical 扩展架构 | 高：新增 vertical 需复制整套代码 | Milestone 2 | P1 |
| FR-014 | 前端垂直状态管理 | `app.js` 第 3 行：`currentVertical: "nail"` 写死配置中 | 未满足 | 前端无动态 vertical 状态 | 高：无法切换/扩展 vertical | Milestone 2 | P1 |
| FR-015 | 兼容旧 /api/nail/... 接口 | `routes.py` 第 94 行：`POST /api/nail/notes`；第 114 行：`GET /api/nail/notes/{note_id}/package` | 部分满足 | 旧接口已存在 | 低：兼容层已实现 | Milestone 1 | P1 |
| FR-016 | 复制标题/正文/标签/单页内容 | **未找到** 复制功能实现 | 未满足 | 无复制功能 | 中：影响内容使用 | Milestone 3 | P2 |
| FR-017 | 空状态/加载状态展示 | 部分 UI 有空状态处理 | 部分满足 | 需系统检查各模块空状态 | 低：部分已有 | Milestone 3 | P2 |
| FR-018 | 每个 Milestone 验收报告 | Milestone 0 进行中 | 部分满足 | 本阶段为首次执行 | 低：流程已建立 | Milestone 0 | P2 |

---

## 关键差距详解

### 1. /api/verticals 缺失（FR-000）

**证据**：
- `verticals/nail/api/routes.py` 无 `/api/verticals` 相关路由
- 搜索关键词 "verticals" 在 routes.py 中无结果

**影响**：无法获取可用 vertical 列表，前端无法动态切换 vertical

**建议**：Milestone 1 优先实现

---

### 2. 历史记录依赖 localStorage（FR-006）

**证据**：
- `verticals/nail/web/app.js` 第 228-260 行：`saveLastJob()`/`loadLastJob()` 使用 `window.localStorage`
- `STORAGE_KEY = "nail_studio_last_job"`
- 无 `/api/verticals/{vertical}/notes` 服务端历史 API

**影响**：
- 清空浏览器缓存后历史不可恢复
- 换浏览器后历史不可见
- 无法按 vertical 隔离历史

**建议**：Milestone 1 优先实现服务端历史列表

---

### 3. 案例库 UI 缺失（FR-008）

**证据**：
- `verticals/nail/web/app.js` 无案例库相关 DOM 元素或 API 调用
- `case_library.py` 是命令行工具，无 Web API
- 无 `/api/verticals/{vertical}/cases` 路由

**影响**：case_id 只能作为隐藏参数手动输入，不是有界面的产品能力

**建议**：Milestone 2 实现

---

### 4. innerHTML 风险（FR-011）

**证据**：
- `app.js` 第 348 行：`noteSummary.innerHTML = ""`
- `app.js` 第 349 行：`pagesGrid.innerHTML = ""`
- `app.js` 第 994 行：`container.innerHTML = ""`
- `app.js` 第 142 行：`selectElement.innerHTML = ""`（用于填充下拉选项，低风险）

**影响**：用户可控内容（如 note 标题、正文、标签）如果通过 innerHTML 渲染，存在 XSS 风险

**需确认**：第 348/349/994 行的 innerHTML 渲染内容是否来自用户输入。如果是，需改为 textContent 或 createElement

**建议**：Milestone 3 前修复

---

### 5. note_package.json 缺少 v1.0 必需字段（FR-012）

**证据**：
- `output/nail_20260430_013126_single_seed_summer_cat_eye_short_job_adcf2f652f48/note_package.json` 缺少 `content_platform`、`content_type`、`vertical` 字段
- 现有字段：note_id, brief, style_id, note_goal, note_template, visual_dna, pages, selected_title, caption, tags 等

**影响**：
- 无法从 package 本身判断 note 属于哪个 vertical
- 历史扫描服务需通过路径或文件名推断 vertical

**建议**：Milestone 1 实现 History Service 时做 fallback 推断；新生成任务必须写入这三个字段

---

### 6. 前端 vertical 写死（FR-014）

**证据**：
- `app.js` 第 2-3 行：`const APP_CONFIG = { currentVertical: "nail", ... }`
- `app.js` 第 97 行：`const currentVertical = APP_CONFIG.verticals[APP_CONFIG.currentVertical]`
- `verticals/nail/api/app.py` 第 12 行：标题为 "xhs_nail_agent API"

**影响**：前端和 API 标题均绑定 nail，无法动态切换 vertical

**建议**：Milestone 2 实现前端 vertical 状态管理和 API 路径升级

---

### 7. 旧接口存在但新接口缺失（FR-001, FR-007）

**证据**：
- `routes.py` 第 94 行：`POST /api/nail/notes` ✅ 已存在
- `routes.py` 第 114 行：`GET /api/nail/notes/{note_id}/package` ✅ 已存在
- `routes.py` 第 58 行：`POST /api/nail/assets/reference-image` ✅ 已存在
- `routes.py` 第 106 行：`GET /api/jobs/{job_id}` ✅ 已存在
- `/api/verticals` ❌ 不存在
- `/api/verticals/{vertical}/notes` ❌ 不存在
- `/api/verticals/{vertical}/notes/{note_id}/package` ❌ 不存在
- `/api/verticals/{vertical}/reference-images` ❌ 不存在
- `/api/verticals/{vertical}/cases` ❌ 不存在

**建议**：Milestone 1-2 实现新 API，同时保留旧接口作为兼容层

---

## 测试覆盖现状

| 测试文件 | 覆盖范围 | 状态 |
|---|---|---|
| tests/test_nail_api.py | nail API 测试 | 已有，需扩展 |
| tests/test_nail_history_api.py | nail 历史 API | **文件不存在** |
| tests/test_nail_package_api.py | nail package API | **文件不存在** |
| tests/test_nail_cases_api.py | nail 案例 API | **文件不存在** |
| tests/test_reference_source_validation.py | reference_source 校验 | **文件不存在** |
| tests/test_phase05_e2e_strict.py | E2E 测试 | 已有 |

**结论**：API 测试基础已建立，但历史、package、案例相关测试文件不存在，需在 Milestone 1-2 创建

---

## 代码扫描文件清单

### API 路由

- `verticals/nail/api/routes.py` - 130 行，包含 /api/nail/... 路由
- `verticals/nail/api/app.py` - 27 行，FastAPI 应用入口
- `verticals/nail/api/schemas.py` - 包含请求/响应 schema 定义

### 服务层

- `verticals/nail/service/job_store.py` - Job 存储
- `verticals/nail/service/nail_note_service.py` - nail note 服务

### 前端

- `verticals/nail/web/app.js` - 主前端逻辑，约 1000+ 行
- `verticals/nail/web/index.html` - HTML 入口

### 测试

- `tests/test_nail_api.py` - API 测试
- `tests/test_nail_acceptance_regressions.py` - 验收回归测试
- `tests/test_phase05_e2e_strict.py` - E2E 测试
- `tests/test_llm_provider.py` - LLM provider 测试
- `tests/test_nail_service_models.py` - 服务模型测试
- `tests/test_nail_reference_context.py` - 参考上下文测试

### 数据

- `output/` - 包含多个 note_package.json，结构缺少 content_platform/content_type/vertical
- `case_library/poster/` - 案例库目录，包含 metadata.json

---

## 风险汇总

| 风险 | 等级 | 说明 |
|---|---|---|
| innerHTML XSS 风险 | 高 | 需确认渲染内容是否用户可控 |
| localStorage 历史不可靠 | 高 | 换浏览器/清缓存后无历史 |
| 无服务端历史列表 | 高 | 无法实现服务端历史能力 |
| 无案例库 UI | 高 | case_id 仅为隐藏参数 |
| 前端 vertical 写死 | 高 | 无法动态切换 vertical |
| 无 unknown vertical 校验 | 高 | 可能 fallback 到 nail |
| note_package 缺少 v1.0 字段 | 中 | 旧数据无法直接按 vertical 过滤 |
| 多 vertical 扩展架构缺失 | 中 | 新增 vertical 需复制代码 |

---

## 更新记录

| 日期 | 更新人 | 更新内容 |
|---|---|---|
| 2026-04-30 | Codex/Hermes | 初始创建，基于代码扫描 |
