# Vertical Content Studio MVP v1.0 验收矩阵

- **来源文档**：docs/v1.md
- **生成日期**：2026-04-30
- **当前阶段**：Milestone 0
- **状态说明**：本文件是从 v1.md 派生的执行跟踪矩阵，不替代 v1.md。

## 概述

本文档记录 MVP v1.0 所有功能需求（FR）的验收状态。FR 编号严格对应 docs/v1.md 中定义的编号（FR-000 至 FR-018）。

---

## 验收矩阵

| FR | 功能名称 | 需求摘要 | 相关 API | 前端模块 | 后端模块 | Milestone | 优先级 | 自动化测试 | 手动验收 | 当前状态 | 备注 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| FR-000 | 垂类注册与选择 | 系统必须支持 vertical 概念，提供 vertical registry；GET /api/verticals 返回可用垂类列表；前端显示当前 selectedVertical；未知 vertical 返回 4xx，不得 fallback 到 nail | GET /api/verticals | 前端状态管理 | Vertical Registry | Milestone 1 | P0 | 待开发 | 前端显示 vertical，清空 localStorage 后仍显示 | 待开发 | v1.0 核心扩展维度，尚未实现 /api/verticals |
| FR-001 | 创建生成任务 | POST /api/verticals/{vertical}/notes 创建任务；支持 reference_source 三模式；后端校验 vertical、reference_source 互斥、case.vertical 匹配 | POST /api/verticals/{vertical}/notes | Studio 表单 | Note Service | Milestone 2 | P0 | 待开发 | 三种模式均可创建任务并返回 job_id | 待开发 | 旧接口 /api/nail/notes 已存在，新接口未实现 |
| FR-002 | reference_source 模式管理 | 三种模式（none/local_path/case_id）UI 明确区分；前后端均校验互斥规则；非法组合返回 4xx | N/A（业务逻辑） | Studio 模式切换 | Request Validation | Milestone 2 | P0 | 待开发 | 切换模式时清理不适用字段；后端拒绝非法组合 | 待开发 | 需在前后端同时实现互斥校验 |
| FR-003 | 参考图上传 | POST /api/verticals/{vertical}/reference-images 上传参考图；返回 safe relative path；校验文件类型和大小 | POST /api/verticals/{vertical}/reference-images | Studio 参考图区 | File Upload Handler | Milestone 2 | P1 | 待开发 | nail 下可上传参考图，返回路径可用于 local_path 模式 | 待开发 | 旧接口 /api/nail/assets/reference-image 已存在 |
| FR-004 | 任务进度观察 | GET /api/jobs/{job_id} 返回 job 状态；展示 status、stage、elapsed_seconds、error 信息；前端 Progress 模块轮询展示 | GET /api/jobs/{job_id} | Progress 模块 | Job Store | Milestone 3 | P0 | 待扩展 | queued/running/succeeded/failed/partial_failed 状态可正确展示；失败展示错误原因 | 部分满足 | 已有 /api/jobs/{job_id}，但 stage/elapsed_seconds/error_stage 需增强 |
| FR-005 | 内容预览 | Preview 模块展示标题、正文、标签、多页结构、图片、诊断信息；支持复制标题/正文/标签；历史回放与实时预览统一渲染；不得使用 innerHTML 渲染用户可控内容 | N/A（渲染逻辑） | Preview 模块 | Package Service | Milestone 3 | P0 | 待开发 | 标题/正文/标签可见；多页内容可见；图片可见或显示缺失；复制功能可用；不使用 innerHTML | 待开发 | 需检查 innerHTML 风险（app.js 第 348/349/994 行） |
| FR-006 | 服务端历史列表 | GET /api/verticals/{vertical}/notes 扫描服务端 output 返回历史列表；按 vertical 过滤；清空 localStorage 后仍可恢复；损坏 package 跳过 | GET /api/verticals/{vertical}/notes | History 模块 | History Service | Milestone 1 | P0 | 待开发 | 清空 localStorage 后历史仍可加载；点击历史项可恢复预览 | 待开发 | 当前依赖 localStorage，服务端历史列表未实现 |
| FR-007 | 历史 package 回放 | GET /api/verticals/{vertical}/notes/{note_id}/package 读取 note_package；字段缺失 fallback；图片缺失显示状态；vertical 不匹配返回 4xx | GET /api/verticals/{vertical}/notes/{note_id}/package | Preview 模块 | Package Service | Milestone 1 | P0 | 待开发 | 点击历史项可完整恢复预览；note_id 不存在返回 404；旧 package 可 fallback | 待开发 | 旧接口 /api/nail/notes/{note_id}/package 已存在 |
| FR-008 | 案例库列表与选择 | GET /api/verticals/{vertical}/cases 返回案例列表；用户可浏览/选择案例；选择后回填生成工作台；case 按 vertical 隔离；跨 vertical case_id 校验 | GET /api/verticals/{vertical}/cases | Cases 模块 | Case Service | Milestone 2 | P0 | 待开发 | 案例库有前端入口；可浏览 nail 案例；点击后生成模式切换为 case_id | 待开发 | 当前 case_id 仅为参数，无案例库 UI |
| FR-009 | 静态资源访问 | 访问 output 图片、input 参考图、case preview 图片；路径安全校验；不得返回本地绝对路径；不得允许路径穿越 | N/A（静态文件服务） | Preview/参考图 | Static File Server | Milestone 1 | P1 | 待开发 | 图片 URL 可打开；路径穿越被拒绝 | 部分满足 | 静态文件服务已配置，但需验证路径安全 |
| FR-010 | 错误处理与恢复 | 结构化错误码；job 404 时尝试 package fallback；partial_failed 展示成功部分；网络错误允许重试 | N/A（错误处理） | Progress/Preview | Job Store/Package Service | Milestone 3 | P1 | 待开发 | 失败任务展示错误原因和阶段；可 fallback 恢复 | 部分满足 | 部分 fallback 能力已存在 |
| FR-011 | 安全渲染与输入校验 | 前端不得使用 innerHTML 渲染用户可控内容；上传文件校验类型和大小；跨 vertical case_id 校验；package 接口路径安全校验 | N/A（安全校验） | All | All | Milestone 1 | P0 | 待开发 | innerHTML 不用于渲染用户可控内容；文件上传校验生效 | 待确认 | 需修复 app.js 中 innerHTML 用法 |
| FR-012 | note_package 标准化 | note_package.json 必须包含 content_platform、content_type、vertical；旧 package 可 fallback 推断 | N/A（数据模型） | N/A | Package Writer | Milestone 1 | P0 | 待开发 | 新生成 package 包含三个字段；旧 package fallback 推断 | 待开发 | 当前 package 缺少 content_platform、content_type、vertical |
| FR-013 | 垂类适配器与工作流分发 | 通过 vertical registry/adapter 查找对应 workflow；新增 vertical 时不复制整套系统 | N/A（架构） | N/A | Vertical Adapter | Milestone 2 | P1 | N/A | 新增 vertical 只需新增 registry/adapter 配置 | 待开发 | 架构设计阶段，尚未实现 |
| FR-014 | 前端垂类状态管理 | 前端状态包含 selectedVertical；UI 显示 content_platform、content_type、vertical；不再将文案写死为"美甲" | N/A（前端状态） | Studio/All | N/A | Milestone 2 | P1 | 待开发 | 页面显示当前 vertical；切换 vertical 时状态同步 | 待开发 | 当前 APP_CONFIG.currentVertical = "nail"，需升级为动态状态 |
| FR-015 | 兼容旧接口与旧数据 | 旧 /api/nail/... 作为兼容层保留；旧 package fallback 推断 vertical；兼容层不得绕过新安全规则 | /api/nail/... 兼容层 | N/A | 兼容适配层 | Milestone 1 | P1 | 待开发 | 旧接口仍可工作；旧数据可 fallback | 部分满足 | 旧接口已存在，需确认兼容范围 |
| FR-016 | 基础复制与内容使用能力 | 复制标题、正文、标签、单页文案、全部文案；剪贴板不可用时显示失败提示 | N/A（UI 能力） | Preview 模块 | N/A | Milestone 3 | P2 | 待开发 | 复制按钮可正常复制对应内容 | 待开发 | 尚未实现复制功能 |
| FR-017 | 空状态与加载状态 | 历史为空时展示空状态；案例为空时展示空状态；加载中展示 loading；package 损坏展示损坏提示 | N/A（UI 状态） | All | N/A | Milestone 3 | P2 | 待开发 | 各模块空状态/加载状态展示正确 | 待开发 | 部分模块已有空状态处理 |
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
| 2026-04-30 | Codex/Hermes | 初始创建，基于 docs/v1.md FR 定义 |

---

**注意**：当前状态为"待开发"或"部分满足"的项，表示尚未完全实现 v1.0 要求，需在后续 Milestone 中完成。
