# Vertical Content Studio MVP v1.0 验收矩阵

- **来源文档**：docs/vertical_content_studio_mvp_v1_requirements.md
- **生成日期**：2026-04-30
- **当前阶段**：Milestone 1 已完成，Milestone 2 已验收通过，Milestone 3 Slice A/B 已完成，Milestone 4 Slice A/B/C/D 已完成，Milestone 5 Slice A/B/C 已完成，Milestone 6 Slice A/B 已完成
- **状态说明**：本文件是从 v1.md 派生的执行跟踪矩阵，不替代 v1.md。

## 概述

本文档记录 MVP v1.0 所有功能需求（FR）的验收状态。FR 编号严格对应 docs/vertical_content_studio_mvp_v1_requirements.md 中定义的编号（FR-000 至 FR-018）。

---

## 验收矩阵

| FR | 功能名称 | 需求摘要 | 相关 API | 前端模块 | 后端模块 | Milestone | 优先级 | 自动化测试 | 手动验收 | 当前状态 | 备注 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| FR-000 | 垂类注册与选择 | 系统必须支持 vertical 概念，提供 vertical registry；GET /api/verticals 返回可用垂类列表；前端显示当前 selectedVertical；未知 vertical 返回 4xx，不得 fallback 到 nail | GET /api/verticals | 前端状态管理 | Vertical Registry | Milestone 1 | P0 | 已覆盖 | 前端显示 vertical，清空 localStorage 后仍显示 | 已完成 | 已接入 Vertical Registry、`GET /api/verticals`，unknown vertical 明确返回 4xx，不再 fallback 到 nail |
| FR-001 | 创建生成任务 | POST /api/verticals/{vertical}/notes 创建任务；支持 reference_source 三模式；后端校验 vertical、reference_source 互斥、case.vertical 匹配 | POST /api/verticals/{vertical}/notes | Studio 表单 | Note Service | Milestone 2 | P0 | 已覆盖 | 三种模式均可创建任务并返回 job_id | 部分满足 | 新的 vertical 创建接口尚未实现；当前通过兼容接口 `/api/nail/notes` 完成 none / local_path / case_id 三模式创建与校验 |
| FR-002 | reference_source 模式管理 | 三种模式（none/local_path/case_id）UI 明确区分；前后端均校验互斥规则；非法组合返回 4xx | N/A（业务逻辑） | Studio 模式切换 | Request Validation | Milestone 2 | P0 | 已覆盖 | 切换模式时清理不适用字段；后端拒绝非法组合 | 部分满足 | 后端已完成 `reference_source` 推断与互斥校验；浏览器已实测 `case_id`/`none` 模式，`local_path` 文件选择器上传因 runtime 限制仍待人工点验 |
| FR-003 | 参考图上传 | POST /api/verticals/{vertical}/reference-images 上传参考图；返回 safe relative path；校验文件类型和大小 | POST /api/verticals/{vertical}/reference-images | Studio 参考图区 | File Upload Handler | Milestone 2 | P1 | 已覆盖 | nail 下可上传参考图，返回路径可用于 local_path 模式 | 部分满足 | 新旧上传接口均可用：`/api/verticals/{vertical}/reference-images` 与兼容接口 `/api/nail/assets/reference-image`；接口与任务创建链路已验证，浏览器 file-picker 上传待人工点验 |
| FR-004 | 任务进度观察 | GET /api/jobs/{job_id} 返回 job 状态；展示 status、stage、elapsed_seconds、error 信息；前端 Progress 模块轮询展示 | GET /api/jobs/{job_id} | Progress 模块 | Job Store | Milestone 3 | P0 | 已覆盖 | queued/running/succeeded/failed/partial_failed 状态可正确展示；失败展示错误原因 | 已完成 | `/api/jobs/{job_id}` 已返回 `stage`、`started_at`、`updated_at`、`completed_at`、`elapsed_seconds`、`failed_stage`、`error_summary`；老 job 记录可按 `status` fallback 推导 stage；前端 Progress 已接入 stage 中文文案与耗时展示 |
| FR-005 | 内容预览 | Preview 模块展示标题、正文、标签、多页结构、图片、诊断信息；支持复制标题/正文/标签；历史回放与实时预览统一渲染；不得使用 innerHTML 渲染用户可控内容 | N/A（渲染逻辑） | Preview 模块 | Package Service | Milestone 3 | P0 | 已覆盖 | 标题/正文/标签可见；多页内容可见；图片可见或显示缺失；6个复制按钮可用（复制标题/正文/标签/完整内容/Markdown/JSON）；不使用 innerHTML | 已完成 | M4 Slice A/B/C 已完成复制标题、正文、标签、完整内容（含页面结构）、Markdown 格式、JSON 格式；M4 Slice D 完成 Preview 状态优化：空态显示 placeholder 无复制按钮误触；生成中显示"正在生成内容预览"；失败态保留 error_summary；history_replay 态显示"当前正在查看服务端历史内容回放"；`currentPreviewData` 在 empty/generating/failed 状态清空；`activeJobToken` 隔离保护 replay 不被 active job 覆盖 |
| FR-006 | 服务端历史列表 | GET /api/verticals/{vertical}/notes 扫描服务端 output 返回历史列表；按 vertical 过滤；清空 localStorage 后仍可恢复；损坏 package 跳过 | GET /api/verticals/{vertical}/notes | History 模块 | History Service | Milestone 1 | P0 | 已覆盖 | 清空 localStorage 后历史仍可加载；点击历史项可恢复预览 | 已完成 | History 面板主来源已切换为服务端历史，localStorage 已降级为最近任务/恢复入口 |
| FR-007 | 历史 package 回放 | GET /api/verticals/{vertical}/notes/{note_id}/package 读取 note_package；字段缺失 fallback；图片缺失显示状态；vertical 不匹配返回 4xx | GET /api/verticals/{vertical}/notes/{note_id}/package | Preview 模块 | Package Service | Milestone 1 | P0 | 已覆盖 | 点击历史项可完整恢复预览；note_id 不存在返回 404；旧 package 可 fallback | 已完成 | 前端已接入 package 回放，真实图片历史任务可恢复 6 张图，unknown vertical 不再 fallback |
| FR-008 | 案例库列表与选择 | GET /api/verticals/{vertical}/cases 返回案例列表；用户可浏览/选择案例；选择后回填生成工作台；case 按 vertical 隔离；跨 vertical case_id 校验 | GET /api/verticals/{vertical}/cases | Cases 模块 | Case Service | Milestone 2 | P0 | 已覆盖 | 案例库有前端入口；可浏览 nail 案例；点击后生成模式切换为 case_id | 已完成 | Cases API、case vertical 匹配校验、案例库 UI、案例选择与 `case_id` 模式浏览器 payload 已完成；unknown vertical 不 fallback 到 nail，unknown case_id 返回 404 |
| FR-009 | 静态资源访问 | 访问 output 图片、input 参考图、case preview 图片；路径安全校验；不得返回本地绝对路径；不得允许路径穿越 | N/A（静态文件服务） | Preview/参考图 | Static File Server | Milestone 1 | P1 | 已覆盖 | 图片 URL 可打开；路径穿越被拒绝 | 已完成 | `static/output`、`static/input`、cases `preview_url` / `preview-image` 已打通；unknown vertical / unknown case / case 无图均返回 4xx，不允许路径穿越或任意文件读取 |
| FR-010 | 错误处理与恢复 | 结构化错误码；job 404 时尝试 package fallback；partial_failed 展示成功部分；网络错误允许重试 | N/A（错误处理） | Progress/Preview | Job Store/Package Service | Milestone 3 | P1 | 已覆盖 | 失败任务展示错误原因和阶段；可 fallback 恢复 | 已完成 | 已实现 job 404→package fallback、`partial_failed` 保留可用结果并返回 `error_summary`；前端 Progress/Debug 会显示 `failed_stage` 与 `error_summary`，History replay 不会被 active job 状态覆盖 |
| FR-011 | 安全渲染与输入校验 | 前端不得使用 innerHTML 渲染用户可控内容；上传文件校验类型和大小；跨 vertical case_id 校验；package 接口路径安全校验 | N/A（安全校验） | All | All | Milestone 1 | P0 | 已覆盖 | innerHTML 不用于渲染用户可控内容；文件上传校验生效 | 已完成 | History/package/recent jobs 的动态文本已改为安全渲染；上传接口校验类型/大小；unknown vertical 不 fallback 到 nail；case_id 与 vertical 匹配校验和 package 路径安全均已落地 |
| FR-012 | note_package 标准化 | note_package.json 必须包含 content_platform、content_type、vertical；旧 package 可 fallback 推断 | N/A（数据模型） | N/A | Package Writer | Milestone 1 | P0 | 已覆盖 | 新生成 package 包含三个字段；旧 package fallback 推断 | 已完成 | content_platform、content_type、vertical 字段已添加到 schema 和 write path；相关 commit: 7711985 |
| FR-013 | 垂类适配器与工作流分发 | 通过 vertical registry/adapter 查找对应 workflow；新增 vertical 时不复制整套系统 | N/A（架构） | N/A | Vertical Adapter | Milestone 2 | P1 | N/A | 新增 vertical 只需新增 registry/adapter 配置 | 待开发 | 架构设计阶段，尚未实现 |
| FR-014 | 前端垂类状态管理 | 前端状态包含 selectedVertical；UI 显示 content_platform、content_type、vertical；不再将文案写死为"美甲" | N/A（前端状态） | Studio/All | N/A | Milestone 2 | P1 | 已覆盖 | 页面显示当前 vertical；切换 vertical 时状态同步 | 部分满足 | `selectedVertical` 已由 `/api/verticals` 驱动，History/Cases/上传接口会随 vertical 变化；当前 UI 仍以 nail 为唯一已启用 vertical，内容类型与平台展示未完全抽象 |
| FR-015 | 兼容旧接口与旧数据 | 旧 /api/nail/... 作为兼容层保留；旧 package fallback 推断 vertical；兼容层不得绕过新安全规则 | /api/nail/... 兼容层 | N/A | 兼容适配层 | Milestone 1 | P1 | 已覆盖 | 旧接口仍可工作；旧数据可 fallback | 部分满足 | 旧 `/api/nail/...` 与新 vertical 历史/package API 当前并存，兼容层仍需在后续统一梳理 |
| FR-016 | 基础复制与内容使用能力 | 复制标题、正文、标签、单页文案、全部文案、Markdown、JSON；剪贴板不可用时显示失败提示 | N/A（UI 能力） | Preview 模块 | N/A | Milestone 4 | P0 | 待开发 | 复制按钮可正常复制对应内容；复制成功显示"已复制"；Markdown 格式合法；JSON 可 JSON.parse；History replay 后复制内容来自 replay package | 已完成 | M4 Slice A: 复制标题/正文/标签/完整内容（含页面结构）+ `showCopyFeedback` UI反馈；M4 Slice B: 复制 Markdown（含 #标题、##标签、##页面结构、###第N页）；M4 Slice C: 复制 JSON（含 note_id/selected_title/body/tags/pages/vertical）；M4 Slice D: Preview 状态机（empty/generating/failed/quick_preview/history_replay）保护复制目标，`currentPreviewData` 在非 quick_preview/history_replay 状态清空，`activeJobToken` 隔离 replay 不被 active job 异步覆盖；相关 commits: ecffd35, 34bc2ac, d142d58, 975fc02 |
| FR-017 | 空状态与加载状态 | 历史为空时展示空状态；案例为空时展示空状态；加载中展示 loading；package 损坏展示损坏提示 | N/A（UI 状态） | All | N/A | Milestone 3 | P2 | 已覆盖 | 各模块空状态/加载状态展示正确 | 部分满足 | History 与 Preview 的 empty-state 互斥已修复；M4 Slice D 优化 Preview 空态文案，空态下不暴露可误触的复制按钮；Progress 会在 running/completed/failed/replay 间切换清晰状态；Cases 空态的全量人工点验仍可继续补充 |
| FR-018 | 基础文档与验收报告 | 每个 Milestone 输出验收报告；报告记录 commit、测试结果、手动验收、范围偏差 | N/A（文档） | N/A | N/A | Milestone 0 | P2 | N/A | 每个 Milestone 有验收报告 | Milestone 0 进行中 | 本阶段目标 |
| FR-019 | History 搜索、过滤与排序 | 支持 note_id 搜索；支持 selected_title 搜索（大小写不敏感）；支持 has_package 全部 / 有结果包 / 无结果包筛选；支持 created_at 升序 / 降序排序；搜索或筛选无结果时显示"没有匹配的历史内容"；sort 参数不参与 filter active 空状态判断；historyRequestToken 防止过期请求覆盖最新搜索结果；history_replay 与 M4 copy 功能不回退 | GET /api/verticals/{vertical}/notes（支持 search/has_package/sort params） | History 模块 | History Service | Milestone 5 | P0 | 已覆盖 | 搜索 note_id 片段仅显示匹配记录；搜索 selected_title 片段仅显示匹配记录；清空搜索后恢复；has_package=true 时仅显示有包记录；has_package=false 时仅显示无包记录；sort=created_at_desc 时新记录在前；sort=created_at_asc 时旧记录在前；无匹配结果显示"没有匹配的历史内容"；点击回放后 history_replay 状态正常，6 个复制按钮可用 | 已完成 | 后端 `HistoryService.list_notes` 支持 search/has_package/sort 参数；前端 filter bar 含搜索框、has_package 下拉、sort 下拉；`buildVerticalNotesUrl` 使用 URLSearchParams；`isHistoryFilterActive` 仅将 search 和 has_package（不含 sort）视为过滤条件；`historyRequestToken` 自增防乱序；smoke test 9/9 通过；相关 commit: 0df3449 |
| FR-020 | History Item 增强展示与回放保护 | History item 显示 content_platform badge（xhs → 小红书）；显示 content_type tag（image_text_note → 图文笔记，video_note → 视频笔记）；未知值显示原始值，空值显示"未知平台 / 未知类型"；scenario 非空字符串时显示 badge，缺失时不渲染；has_package=true 时回放按钮可点击；has_package=false 时回放按钮 disabled，文案"无法回放"，title"该记录没有结果包，无法回放"，且不绑定 replayHistoryItem | N/A（前端渲染逻辑） | History 模块 | N/A | Milestone 5 | P0 | 已覆盖 | platform badge 显示"小红书"；type tag 显示"图文笔记"；scenario 缺失时无空白 badge；has_package=true 时"回放预览"可点击；has_package=false 时"无法回放" disabled，hover 显示"该记录没有结果包，无法回放"；搜索/筛选/排序回归通过；history_replay + 6 个复制按钮回归通过 | 已完成 | `labelForPlatform`/`labelForContentType` 映射；scenario 条件渲染；`canReplay = !!(item.note_id && item.has_package)` 控制 disabled 与事件绑定；CSS `button:disabled.recent-job-open` 样式；smoke test API 9/9 通过；代码级复核 12/12 通过；相关 commit: e45c750 |
| FR-021 | Single Package Export | History item 提供"导出 JSON"和"导出 Markdown"按钮；有结果包时按钮可点击，触发浏览器下载；无结果包时按钮 disabled，title"该记录没有结果包，无法导出"；导出文件名 {note_id}_export.json / {note_id}_export.md；JSON 内容与 buildJson 一致；Markdown 内容与 buildMarkdown 一致；MIME application/json;charset=utf-8 / text/markdown;charset=utf-8；fetch 失败时按钮短暂显示"导出失败"后自动恢复；导出过程不触发 history_replay；不修改 previewState / currentPreviewData；M5 Slice A/B 与 M4 复制能力回归通过 | GET /api/verticals/{vertical}/notes/{note_id}/package | History 模块 | 无新增改动 | Milestone 5 | P1 | 已覆盖 | 有 package 的 item 可导出 JSON 和 Markdown；has_package=false 时导出按钮 disabled；fetch 失败时按钮短暂显示"导出失败"后 1500ms 恢复；导出后 Preview 状态不变；M5 Slice A/B 和 M4 复制功能正常 | 已完成 | `triggerDownload` 使用 Blob + createObjectURL + a.download；`exportHistoryItemAsJson/Markdown` 复用 buildJson/buildMarkdown；`failed` flag + `finally` 控制错误恢复；`canExport = !!(item.note_id && item.has_package)` 与回放 guard 对齐；`e.stopPropagation()` 防止冒泡；代码级复核 38/38 通过；smoke test API + code 15/15 通过；hotfix 3860f1b 修复：fetchJson 返回已解析的 packageData，export 函数不再调用 response.json()；真实浏览器验证 JSON/Markdown 下载通过；相关 commit: a05efcd, 3860f1b |
| FR-022 | History 单条删除 | DELETE /api/verticals/{vertical}/notes/{note_id} 删除单条历史记录；成功返回 204 No Content；不存在返回 404；非法 note_id 返回 400；路径穿越返回 403；前端"删除"按钮在每条 history item 上；点击后弹出确认框"确定删除该历史记录？删除后不可恢复。"；用户取消不发送请求；确认后调用 DELETE API；使用 raw fetch + response.ok 判断 204；删除成功后整个 Studio 回到干净空态（页面自动刷新）；删除失败时只记录 console.error，不弹 alert/toast；has_package=false 记录也可删除；不破坏 M5 replay/export/search/filter/sort | DELETE /api/verticals/{vertical}/notes/{note_id} | History 模块 | 无新增改动 | Milestone 6 | P0 | 已覆盖 | DELETE 已有 note_id 返回 204，页面自动刷新；DELETE 同一 note_id 再次返回 404；DELETE 不存在的 note_id 返回 404；DELETE 非法 note_id（含非法字符）返回 400；前端删除按钮出现在每条 history item；confirm 对话框存在；取消时不发请求；确认后 Studio 重置到空态；M5 replay/export/search/filter/sort 功能正常；smoke test 13/13 通过 | 已完成 | `shutil.rmtree` 删除 note 目录；`_reject_invalid_note_id` + `relative_to` 做路径安全校验；`window.confirm` 确认框；raw fetch 避免 204 空响应解析问题；`window.location.reload()` 在 response.ok 后执行全页刷新确保 Studio 状态干净；相关 commits: babf9d4, f980983 |
| FR-023 | History 批量删除 | POST /api/verticals/{vertical}/notes/delete 批量删除历史记录；Request body: `{"note_ids": ["id1","id2"]}`；Response 200: `{"deleted": ["id1"], "failed": [{"note_id": "id2", "status": 404, "reason": "not_found"}]}`；前端每条 history item 左侧显示 checkbox；无选择时批量删除按钮 disabled，文案"批量删除"；有选择时按钮 enabled，文案"删除选中（N）"；支持全选/取消全选；点击删除后 confirm："确定删除选中的 N 条历史记录？删除后不可恢复。"；confirm 取消不发送请求；confirm 确认发送 POST；deleted.length > 0 时 window.location.reload()；deleted.length === 0（全部失败）时 console.error，不 reload，保留选择状态；response 非 ok 时 console.error，不 reload，保留选择状态；不破坏 M6A 单条删除 / M5 replay/export/search/filter/sort；不引入 soft delete/trash/restore/undo；不删除 localStorage recent jobs | POST /api/verticals/{vertical}/notes/delete | History 模块 | 无新增改动 | Milestone 6 | P1 | 已覆盖 | POST 2 个已存在 note_id 返回 200 deleted=[2] failed=[]；重复删除返回 deleted=[] failed=[404×2]；混合已存在+不存在时已存在进 deleted 不存在进 failed 404；混合已存在+非法 note_id 时非法进 failed 400 已存在正常删除；note_ids=[] 返回 deleted=[] failed=[]；note_ids 非数组返回 422；重复 note_id 只处理一次；M6A 单条 DELETE 回归正常（204→404）；checkbox 不影响回放/导出/删除按钮；smoke test 9/9 通过 | 已完成 | M6 Slice B 分 B1（Backend API）+ B2（Frontend UI）+ B3（Docs）；B1 commit: 6ee7661；B2 commit: 197f554；Backend: `shutil.rmtree` + `_NOTE_ID_RE` 校验 + path traversal 保护 + 去重处理；Frontend: `selectedNoteIds` Set + checkbox DOM 注入 + 全选/取消全选 + `buildVerticalNotesUrl()+"/delete"` POST + `window.location.reload()` 策略；相关 commits: 6ee7661, 197f554 |
| FR-024 | History 元数据增强 | `created_at` Hybrid（写路径填充 datetime.now()，读路径旧包 fallback 到 st_mtime）；返回 `created_at_source`（"package" / "file_mtime" / "unknown"）；`has_body` = bool(selected_title or body)；`has_images` = any page has image_path/image_url/url；`package_status` = "no_content" / "empty_images" / "ok"；`canReplay` guard 使用 has_body || has_images；`canExport` guard 使用 has_body；modeLabel 显示三态：可回放 / 无内容 / 无结果包；不修改已有 note_package.json；不改变 has_package 原有语义 | GET /api/verticals/{vertical}/notes | History 模块 | History Service / Package Writer / Frontend | v1.1 Slice B | P1 | N/A | 新包 created_at 在 write 时填充；旧包 created_at 按 file mtime fallback；has_package=false 过滤器恢复正常；created_at_source 正确返回；canReplay 在无正文无图时 disabled；canExport 在无正文时 disabled；smoke test 通过 | 已完成 | v1.1 Slice B；Backend: `created_at` Hybrid + additive fields in `HistoryService.list_notes` + `created_at` write in `package_writer.py`；Frontend: updated `canReplay`/`canExport` guards + 3-state modeLabel；Docs: `v1_acceptance_matrix.md` 本条目；相关 commits: (待填) |

---

## 优先级说明

- **P0**：MVP v1.0 必须完成，否则不能判定通过
- **P1**：建议 v1.0 完成，可降级到 v1.1 但需明确说明
- **P2**：提升体验稳定性，v1.0 可完成或延到 v1.1

---

## 模块与 FR 映射

| 模块 | 相关 FR |
|---|---|
| Vertical Context | FR-000、FR-014 |
| Studio | FR-001、FR-002、FR-003、FR-008 |
| Progress | FR-004、FR-010、FR-017 |
| Preview | FR-005、FR-012、FR-016、FR-017 |
| History | FR-006、FR-007、FR-010、FR-015 |
| Cases | FR-008、FR-011、FR-017 |
| Static Assets | FR-009、FR-011 |
| Platform Core | FR-000、FR-013、FR-015 |
| Documentation | FR-018 |

---

## 核心用户流程与 FR 映射

| 流程 | 相关 FR |
|---|---|
| 选择垂类并基础生成 | FR-000、FR-001、FR-002、FR-004、FR-005、FR-006 |
| 当前垂类下参考图生成 | FR-000、FR-001、FR-002、FR-003、FR-004、FR-005 |
| 当前垂类下案例复用生成 | FR-000、FR-001、FR-002、FR-008、FR-004、FR-005 |
| 服务端历史记录回放 | FR-000、FR-006、FR-007、FR-005、FR-012 |
| 任务失败与 fallback 恢复 | FR-004、FR-010、FR-007、FR-017 |
| 新增 vertical 扩展验证 | FR-000、FR-013、FR-014、FR-015 |
| 内容复制与生产使用 | FR-005、FR-016 |
| 基础安全与路径保护 | FR-011、FR-009 |

---

## 验收状态更新记录

| 日期 | 更新人 | 更新内容 |
|---|---|---|
| 2026-04-30 | Codex/Hermes | 初始创建，基于 docs/vertical_content_studio_mvp_v1_requirements.md FR 定义 |
| 2026-04-30 | Codex/Hermes | 同步 Milestone 1 已落地能力：vertical registry、服务端 history/package API、前端历史接入与 package 回放、localStorage 降级策略、`/health` 恢复 |
| 2026-05-01 | Codex/Hermes | M4 Slice A/B/C 完成：Preview 复制能力（标题/正文/标签/完整内容）、Markdown 导出、JSON 导出；FR-005 已完成；FR-016 已完成；相关 commits: ecffd35, 34bc2ac, d142d58 |
| 2026-05-02 | Codex/Hermes | M4 Slice D 完成：Preview 状态优化（empty/generating/failed/quick_preview/history_replay 五态）；空态无复制按钮误触；生成中显示"正在生成内容预览"；失败态保留 error_summary；history_replay 显示回放文案；`currentPreviewData` 在非内容态清空；`activeJobToken` 保护 replay 不被 active job 异步覆盖；删除未调用 `applyPreviewState` 死代码；相关 commit: 975fc02 |
| 2026-05-02 | Codex/Hermes | M5 Slice A 完成：History 搜索/过滤/排序（search、has_package、sort 参数）；filter bar UI；`historyRequestToken` 防乱序；`isHistoryFilterActive` 仅含 search 和 has_package；smoke test 9/9 通过；相关 commit: 0df3449 |
| 2026-05-02 | Codex/Hermes | M5 Slice B 完成：History item 增强展示（platform badge、type tag、scenario badge）；回放保护（has_package=false 时 disabled）；`canReplay` guard 分离 disabled 与事件绑定；smoke test API 9/9 通过；代码级复核 12/12 通过；相关 commit: e45c750 |
| 2026-05-02 | Codex/Hermes | M5 Slice C 完成：History item 导出 JSON/Markdown 功能；`triggerDownload` Blob + createObjectURL 实现；复用 buildJson/buildMarkdown；`failed` flag + `finally` 错误恢复；canExport guard 与回放对齐；smoke test API + code 15/15 通过；代码级复核 38/38 通过；相关 commit: a05efcd |
| 2026-05-02 | Codex/Hermes | M5 Slice C Hotfix：修复 export 函数错误调用 response.json()；fetchJson 已返回已解析 JSON 对象，不再需要二次解析；真实浏览器验证 JSON/Markdown 下载通过；相关 commit: 3860f1b |
| 2026-05-02 | Codex/Hermes | M6 Slice A Hotfix 2：replayToken 机制防止 stale response 导致旧 content 覆盖新 replay；双 Guard 点（fetch 成功和 catch）检查 token 一致性防止删除后渲染；相关 commit: f980983 |
| 2026-05-02 | Codex/Hermes | M6 Slice A Hotfix 3：删除成功后改用 `window.location.reload()` 全页刷新替代前端局部状态清理；彻底避免 DOM 残留 Preview 问题；验收标准更新为"删除任意 history item 后 Studio 回到干净空态"；相关 commits: f980983 |
| 2026-05-03 | Codex/Hermes | M6 Slice B1 完成：POST /api/verticals/{vertical}/notes/delete 批量删除 API；去重处理 + 路径安全校验 + partial success 响应；API smoke 9/9 通过；相关 commit: 6ee7661 |
| 2026-05-03 | Codex/Hermes | M6 Slice B2 完成：History 每条 item 左侧 checkbox + selectedNoteIds Set + 全选/取消全选 + 批量删除按钮 + confirm + reload 策略；checkbox 不影响回放/导出/单条删除；Frontend smoke 12/12 通过；相关 commit: 197f554 |
| 2026-05-03 | Codex/Hermes | M6 Slice B3 完成：FR-023 History 批量删除验收矩阵更新完成；M6 Slice B 全部 Closed |
| 2026-05-03 | Codex/Hermes | v1.1 Slice B 完成：FR-024 History 元数据增强（created_at Hybrid + has_body/has_images/package_status + frontend guards）；相关 commits: (待填) |
| 2026-05-03 | Codex/Hermes | FR-012 note_package 标准化完成：content_platform、content_type、vertical 字段已添加到 schema 和 write path；commit: 7711985 |
| 2026-05-03 | Codex/Hermes | Pagination 完成：limit/offset query params 添加到 GET /api/verticals/{vertical}/notes；test_invalid_note_id_format_returns_4xx URL encoding fix；相关 commits: 518f678, 4ff0daf |
| 2026-05-03 | Codex/Hermes | 依赖更新：requests + openai 已添加到 requirements.txt；commit: 442bb44 |

---

**注意**：当前状态为"待开发"或"部分满足"的项，表示尚未完全实现 v1.0 要求，需在后续 Milestone 中完成。
