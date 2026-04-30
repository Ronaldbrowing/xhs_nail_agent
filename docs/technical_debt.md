# 技术债务清单

- **来源文档**：docs/v1.md
- **生成日期**：2026-04-30
- **当前阶段**：Milestone 0
- **状态说明**：本文档记录 v1.0 开发过程中发现和积累的技术债务

---

## 概述

本文档跟踪 Vertical Content Studio MVP v1.0 开发过程中发现的技术债务。技术债务影响开发效率、系统稳定性和未来扩展能力，需要明确记录并在后续版本中逐步偿还。

---

## 技术债务列表

| 编号 | 类型 | 描述 | 影响范围 | 风险等级 | 是否阻塞 v1.0 | 建议处理阶段 | 备注 |
|---|---|---|---|---|---|---|---|
| TD-001 | 架构 | **/api/nail 兼容层遗留**：旧 API 路径 `/api/nail/...` 与新主路径 `/api/verticals/{vertical}/...` 并存，长期增加维护成本 | API 路由层 | 中 | 否 | v1.1 | 需明确兼容层退出时间表 |
| TD-002 | 数据 | **历史扫描性能**：HistoryService 扫描整个 output/ 目录获取历史记录，目录文件增多后性能下降 | HistoryService | 中 | 否 | v1.1 | 建议 v1.1 引入索引或数据库 |
| TD-003 | 数据 | **output 目录结构不标准**：当前 output/{note_id}/note_package.json，缺少 vertical 子目录，跨垂类资产管理可能混乱 | HistoryService, PackageService | 中 | 否 | v1.1 | v1.0 允许兼容，v1.1 建议 output/{vertical}/{note_id}/ |
| TD-004 | 数据 | **旧 package 字段缺失**：现有 note_package.json 不包含 content_platform、content_type、vertical 字段，v1.0 需 fallback 推断 | HistoryService, PackageService | 高 | 是 | v1.0 必须在 HistoryService 中处理 | 需在生成新 package 时写入这些字段 |
| TD-005 | 前端 | **localStorage 残留**：历史记录主要依赖 localStorage，换浏览器/清缓存后不可见，与"服务端历史"目标不符 | 前端 History 模块 | 高 | 是 | v1.0 Milestone 1 | 需降级为快捷入口，Milestone 1 必须实现服务端历史 |
| TD-006 | 安全 | **innerHTML 风险**：app.js 第 348、349、994 行使用 innerHTML 渲染用户可控内容，存在 XSS 风险 | Preview 模块 | 高 | 是 | v1.0 Milestone 3 | 需改为 textContent 或 createElement |
| TD-007 | 架构 | **缺少数据库**：历史记录、案例库、job 状态均依赖文件系统或内存，缺少持久化数据库，影响可靠性 | 全局 | 中 | 否 | v1.2 | v1.0 允许依赖文件系统，v1.1 可选引入 SQLite |
| TD-008 | 架构 | **缺少用户体系**：当前无用户认证和隔离，多用户场景无法支持 | 全局 | 中 | 否 | v1.2 | v1.0 定位单用户工具 |
| TD-009 | 测试 | **缺少完整前端自动化测试**：前端主要靠手动验收，缺少 Jest/Cypress 等自动化测试 | 前端 | 中 | 否 | v1.1 | v1.0 以手动验收为主 |
| TD-010 | 架构 | **多 vertical 仅 nail 真实落地**：系统架构虽然抽象了 vertical，但除 nail 外无其他 vertical 真实验证，扩展架构正确性未经验证 | VerticalRegistry, VerticalAdapter | 高 | 否 | v1.1 | v1.0 需保留 sample vertical 扩展点 |
| TD-011 | 安全 | **静态资源路径安全**：需持续验证静态文件服务不返回本地绝对路径，不允许路径穿越 | Static File Server | 高 | 是 | v1.0 Milestone 1 | 需持续回归测试 |
| TD-012 | API | **错误码不统一**：部分接口返回 {detail: string}，部分返回 {error_code, message}，v1.0 建议统一 | API 响应层 | 低 | 否 | v1.1 | v1.0 接受混用，v1.1 统一 |
| TD-013 | 测试 | **测试覆盖不足**：部分 FR 缺少自动化测试，主要靠手动验收 | 测试 | 中 | 否 | v1.0 Milestone 4 | 需在 Milestone 4 补齐 |
| TD-014 | 前端 | **前端文案写死**：APP_CONFIG 中文案如"小红书美甲图文"写死，非动态按 vertical 展示 | 前端 UI | 中 | 否 | v1.0 Milestone 2 | 需支持动态 vertical 文案 |
| TD-015 | 数据 | **case_library 结构不标准**：案例库分布在 poster/ppt/product 子目录，但 metadata.json 结构不统一 | CaseService | 低 | 否 | v1.1 | 需标准化案例 metadata schema |
| TD-016 | 架构 | **Vertical Adapter 缺失**：当前无 VerticalAdapter 实现，新增 vertical 需复制 workflow 代码 | 工作流层 | 高 | 否 | v1.1 | v1.0 仅验证 nail，adapter 可在 v1.1 实现 |
| TD-017 | API | **job status 字段不完整**：当前 job status 可能缺少 stage、elapsed_seconds、error_stage 等信息 | JobStore, job status API | 中 | 否 | v1.0 Milestone 3 | 需 Milestone 3 增强 |
| TD-018 | 前端 | **前端无 vertical 动态状态**：currentVertical 以常量写死，无法动态切换 | 前端状态管理 | 高 | 否 | v1.0 Milestone 2 | 需从 API 获取 vertical 列表 |
| TD-019 | 文档 | **API 文档缺失**：缺少 OpenAPI/Swagger 完整文档 | API 文档 | 低 | 否 | v1.1 | FastAPI 自动生成，v1.0 接受基础 |
| TD-020 | 部署 | **无容器化部署**：缺少 Docker/Docker Compose，部署依赖手动环境配置 | 部署 | 低 | 否 | v1.2 | v1.0 定位本地开发工具 |

---

## 技术债务详情

### TD-004：旧 package 字段缺失（高优先级）

**描述**：
现有 `output/` 目录下所有 `note_package.json` 不包含 `content_platform`、`content_type`、`vertical` 字段。

**证据**：
```json
// 当前 note_package.json 结构
{
  "note_id": "nail_20260430_xxx",
  "brief": "...",
  "style_id": "...",
  "pages": [...]
  // 缺少 content_platform, content_type, vertical
}
```

**影响**：
- 无法直接从 package 判断 note 属于哪个 vertical
- 历史扫描服务必须通过路径推断
- 无法支持跨 vertical 精确过滤

**偿还方案**：
1. v1.0 中 HistoryService 必须处理缺失字段，fallback 推断 vertical
2. 新生成任务必须在 PackageWriter 中写入这三个字段
3. v1.1 可选批量迁移旧 package

**阻塞 v1.0**：是，Milestone 1 必须处理

---

### TD-005：localStorage 残留（高优先级）

**描述**：
前端主要依赖 `window.localStorage` 存储最近任务和历史记录。

**证据**：
`app.js` 第 228-260 行：
```javascript
function saveLastJob(context) {
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(context));
}
```

**影响**：
- 清空浏览器缓存后历史不可恢复
- 换浏览器后历史不可见
- 无法实现"服务端历史"目标

**偿还方案**：
1. Milestone 1 实现 `GET /api/verticals/{vertical}/notes` 服务端历史 API
2. 前端 History 模块改为调用服务端 API
3. localStorage 降级为"最近任务快捷入口"

**阻塞 v1.0**：是，Milestone 1 必须实现

---

### TD-006：innerHTML 风险（高优先级）

**描述**：
`app.js` 多处使用 `innerHTML` 渲染用户可控内容。

**证据**：
- 第 348 行：`noteSummary.innerHTML = ""`
- 第 349 行：`pagesGrid.innerHTML = ""`
- 第 994 行：`container.innerHTML = ""`

**影响**：
- XSS 安全风险
- 用户输入的标题、正文、标签可能包含恶意脚本

**偿还方案**：
1. 审计 innerHTML 使用位置
2. 区分用户可控内容和系统生成内容
3. 用户可控内容改用 `textContent` 或 `createElement`
4. 特殊 HTML 场景需严格转义

**阻塞 v1.0**：是，Milestone 3 前必须修复

---

### TD-010：多 vertical 扩展未验证（高优先级）

**描述**：
系统架构设计支持多 vertical，但除 nail 外无其他 vertical 真实落地验证。

**影响**：
- VerticalRegistry、VerticalAdapter 架构正确性未经验证
- 新增 vertical 路径可能存在问题
- 可能在不知情的情况下写死了 nail 逻辑

**偿还方案**：
1. v1.0 保留 sample vertical 扩展点（即使不实现真实 workflow）
2. v1.1 优先实现一个简单 vertical（如 outfit）验证架构
3. 单元测试覆盖 vertical 切换逻辑

**阻塞 v1.0**：否，但需保留扩展点

---

## 技术债务趋势

| 阶段 | 新增债务 | 已偿还 | 剩余债务 |
|---|---|---|---|
| Milestone 0 | 20 | 0 | 20 |
| Milestone 1（预计） | 0 | 2 (TD-004, TD-005) | 18 |
| Milestone 2（预计） | 0 | 1 (TD-006) | 17 |
| Milestone 3（预计） | 0 | 1 (TD-017) | 16 |
| Milestone 4（预计） | 0 | 0 | 16 |

---

## 偿还优先级

### P0（v1.0 必须处理）

1. **TD-004**：旧 package 字段缺失 → Milestone 1 HistoryService fallback
2. **TD-005**：localStorage 残留 → Milestone 1 服务端历史
3. **TD-006**：innerHTML XSS 风险 → Milestone 3 安全渲染
4. **TD-011**：静态资源路径安全 → Milestone 1 持续验证

### P1（v1.1 推荐处理）

1. **TD-001**：/api/nail 兼容层整理
2. **TD-002**：历史扫描性能优化
3. **TD-007**：数据库引入
4. **TD-010**：sample vertical 验证
5. **TD-016**：Vertical Adapter 实现
6. **TD-018**：前端 vertical 动态状态

### P2（v1.2+ 考虑）

1. **TD-003**：output 目录结构标准化
2. **TD-008**：用户体系
3. **TD-009**：前端自动化测试
4. **TD-012**：错误码统一
5. **TD-013**：测试覆盖补齐
6. **TD-014**：前端文案动态化
7. **TD-015**：case_library 结构标准化
8. **TD-017**：job status 字段完整化
9. **TD-019**：API 文档完善
10. **TD-020**：容器化部署

---

## 更新记录

| 日期 | 更新人 | 更新内容 |
|---|---|---|
| 2026-04-30 | Codex/Hermes | 初始创建 |
