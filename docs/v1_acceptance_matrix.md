# Vertical Content Studio MVP v1.0 验收矩阵

- **来源文档**：docs/vertical_content_studio_mvp_v1_requirements.md
- **生成日期**：2026-04-30
- **当前阶段**：Milestone 1 已完成，Milestone 2 已验收通过，Milestone 3 Slice A/B 已完成
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
| FR-005 | 内容预览 | Preview 模块展示标题、正文、标签、多页结构、图片、诊断信息；支持复制标题/正文/标签；历史回放与实时预览统一渲染；不得使用 innerHTML 渲染用户可控内容 | N/A（渲染逻辑） | Preview 模块 | Package Service | Milestone 3 | P0 | 已覆盖 | 标题/正文/标签可见；多页内容可见；图片可见或显示缺失；复制功能可用；不使用 innerHTML | 部分满足 | Preview 在 active job 完成与 History replay 场景下均可稳定展示且未回归；当前尚未实现复制能力，因此该 FR 仍为部分满足 |
| FR-006 | 服务端历史列表 | GET /api/verticals/{vertical}/notes 扫描服务端 output 返回历史列表；按 vertical 过滤；清空 localStorage 后仍可恢复；损坏 package 跳过 | GET /api/verticals/{vertical}/notes | History 模块 | History Service | Milestone 1 | P0 | 已覆盖 | 清空 localStorage 后历史仍可加载；点击历史项可恢复预览 | 已完成 | History 面板主来源已切换为服务端历史，localStorage 已降级为最近任务/恢复入口 |
| FR-007 | 历史 package 回放 | GET /api/verticals/{vertical}/notes/{note_id}/package 读取 note_package；字段缺失 fallback；图片缺失显示状态；vertical 不匹配返回 4xx | GET /api/verticals/{vertical}/notes/{note_id}/package | Preview 模块 | Package Service | Milestone 1 | P0 | 已覆盖 | 点击历史项可完整恢复预览；note_id 不存在返回 404；旧 package 可 fallback | 已完成 | 前端已接入 package 回放，真实图片历史任务可恢复 6 张图，unknown vertical 不再 fallback |
| FR-008 | 案例库列表与选择 | GET /api/verticals/{vertical}/cases 返回案例列表；用户可浏览/选择案例；选择后回填生成工作台；case 按 vertical 隔离；跨 vertical case_id 校验 | GET /api/verticals/{vertical}/cases | Cases 模块 | Case Service | Milestone 2 | P0 | 已覆盖 | 案例库有前端入口；可浏览 nail 案例；点击后生成模式切换为 case_id | 已完成 | Cases API、case vertical 匹配校验、案例库 UI、案例选择与 `case_id` 模式浏览器 payload 已完成；unknown vertical 不 fallback 到 nail，unknown case_id 返回 404 |
| FR-009 | 静态资源访问 | 访问 output 图片、input 参考图、case preview 图片；路径安全校验；不得返回本地绝对路径；不得允许路径穿越 | N/A（静态文件服务） | Preview/参考图 | Static File Server | Milestone 1 | P1 | 已覆盖 | 图片 URL 可打开；路径穿越被拒绝 | 已完成 | `static/output`、`static/input`、cases `preview_url` / `preview-image` 已打通；unknown vertical / unknown case / case 无图均返回 4xx，不允许路径穿越或任意文件读取 |
| FR-010 | 错误处理与恢复 | 结构化错误码；job 404 时尝试 package fallback；partial_failed 展示成功部分；网络错误允许重试 | N/A（错误处理） | Progress/Preview | Job Store/Package Service | Milestone 3 | P1 | 已覆盖 | 失败任务展示错误原因和阶段；可 fallback 恢复 | 已完成 | 已实现 job 404→package fallback、`partial_failed` 保留可用结果并返回 `error_summary`；前端 Progress/Debug 会显示 `failed_stage` 与 `error_summary`，History replay 不会被 active job 状态覆盖 |
| FR-011 | 安全渲染与输入校验 | 前端不得使用 innerHTML 渲染用户可控内容；上传文件校验类型和大小；跨 vertical case_id 校验；package 接口路径安全校验 | N/A（安全校验） | All | All | Milestone 1 | P0 | 已覆盖 | innerHTML 不用于渲染用户可控内容；文件上传校验生效 | 已完成 | History/package/recent jobs 的动态文本已改为安全渲染；上传接口校验类型/大小；unknown vertical 不 fallback 到 nail；case_id 与 vertical 匹配校验和 package 路径安全均已落地 |
| FR-012 | note_package 标准化 | note_package.json 必须包含 content_platform、content_type、vertical；旧 package 可 fallback 推断 | N/A（数据模型） | N/A | Package Writer | Milestone 1 | P0 | 待开发 | 新生成 package 包含三个字段；旧 package fallback 推断 | 待开发 | 当前 package 缺少 content_platform、content_type、vertical |
| FR-013 | 垂类适配器与工作流分发 | 通过 vertical registry/adapter 查找对应 workflow；新增 vertical 时不复制整套系统 | N/A（架构） | N/A | Vertical Adapter | Milestone 2 | P1 | N/A | 新增 vertical 只需新增 registry/adapter 配置 | 待开发 | 架构设计阶段，尚未实现 |
| FR-014 | 前端垂类状态管理 | 前端状态包含 selectedVertical；UI 显示 content_platform、content_type、vertical；不再将文案写死为"美甲" | N/A（前端状态） | Studio/All | N/A | Milestone 2 | P1 | 已覆盖 | 页面显示当前 vertical；切换 vertical 时状态同步 | 部分满足 | `selectedVertical` 已由 `/api/verticals` 驱动，History/Cases/上传接口会随 vertical 变化；当前 UI 仍以 nail 为唯一已启用 vertical，内容类型与平台展示未完全抽象 |
| FR-015 | 兼容旧接口与旧数据 | 旧 /api/nail/... 作为兼容层保留；旧 package fallback 推断 vertical；兼容层不得绕过新安全规则 | /api/nail/... 兼容层 | N/A | 兼容适配层 | Milestone 1 | P1 | 已覆盖 | 旧接口仍可工作；旧数据可 fallback | 部分满足 | 旧 `/api/nail/...` 与新 vertical 历史/package API 当前并存，兼容层仍需在后续统一梳理 |
| FR-016 | 基础复制与内容使用能力 | 复制标题、正文、标签、单页文案、全部文案；剪贴板不可用时显示失败提示 | N/A（UI 能力） | Preview 模块 | N/A | Milestone 3 | P2 | 待开发 | 复制按钮可正常复制对应内容 | 待开发 | 尚未实现复制功能 |
| FR-017 | 空状态与加载状态 | 历史为空时展示空状态；案例为空时展示空状态；加载中展示 loading；package 损坏展示损坏提示 | N/A（UI 状态） | All | N/A | Milestone 3 | P2 | 已覆盖 | 各模块空状态/加载状态展示正确 | 部分满足 | History 与 Preview 的 empty-state 互斥已修复，真实页面视觉确认空状态不会与已有内容同时显示；Progress 会在 running/completed/failed/replay 间切换清晰状态，但 Cases 空态的全量人工点验仍可继续补充 |
| FR-018 | 基础文档与验收报告 | 每个 Milestone 输出验收报告；报告记录 commit、测试结果、手动验收、范围偏差 | N/A（文档） | N/A | N/A | Milestone 0 | P2 | N/A | 每个 Milestone 有验收报告 | Milestone 0 进行中 | 本阶段目标 |

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

---

**注意**：当前状态为"待开发"或"部分满足"的项，表示尚未完全实现 v1.0 要求，需在后续 Milestone 中完成。
