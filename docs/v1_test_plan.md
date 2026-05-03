# Vertical Content Studio MVP v1.0 测试计划

- **来源文档**：docs/vertical_content_studio_mvp_v1_requirements.md
- **生成日期**：2026-04-30
- **当前阶段**：Milestone 0
- **状态说明**：本文件是从 v1.md 派生的测试计划，不替代 v1.md。

## 1. 测试范围

### 1.1 平台级测试（所有 vertical 必须通过）

- GET /api/verticals 返回至少包含 nail
- GET /api/verticals 返回的 vertical 必须包含 required 字段
- 未知 vertical 请求返回 4xx
- 未知 vertical 不得 fallback 到 nail
- 所有 API 路径安全校验（不得返回本地绝对路径，不得允许路径穿越）
- 前端不得使用 innerHTML 渲染用户可控内容

### 1.2 nail 垂类级测试

- POST /api/verticals/nail/notes 可以创建任务（三种 reference_source 模式）
- GET /api/jobs/{job_id} 可以查询任务状态
- GET /api/verticals/nail/notes 返回服务端历史
- 清空 localStorage 后历史仍可从服务端恢复
- GET /api/verticals/nail/notes/{note_id}/package 可以回放历史 package
- POST /api/verticals/nail/reference-images 可以上传参考图
- GET /api/verticals/nail/cases 可以返回当前 vertical 的案例库
- case_id 选择后可回填到生成工作台
- 跨 vertical case_id 返回 4xx

### 1.3 API 测试

- POST /api/verticals/{vertical}/notes reference_source=none 合法
- POST /api/verticals/{vertical}/notes reference_source=local_path 必须携带 reference_image_path
- POST /api/verticals/{vertical}/notes reference_source=local_path 不得携带 case_id
- POST /api/verticals/{vertical}/notes reference_source=case_id 必须携带 case_id
- POST /api/verticals/{vertical}/notes reference_source=case_id 不得携带 reference_image_path
- POST /api/verticals/{vertical}/notes reference_source=none 时不得携带 reference_image_path 和 case_id

### 1.4 前端交互测试

- 页面显示当前 vertical=nail
- 三种生成模式可在 UI 中明确选择
- 切换模式时清理不适用字段
- 任务提交后进入 Progress 状态
- Progress 展示 job_id、status、stage、elapsed_seconds
- 任务成功后自动展示 Preview
- 失败任务展示错误原因
- 历史记录模块可加载服务端历史
- 案例库模块可加载并展示案例
- 案例选择后可回填生成工作台

### 1.5 历史记录测试

- 清空 localStorage 后 GET /api/verticals/nail/notes 仍返回历史
- 历史列表按 vertical 过滤
- 点击历史项可打开 package
- 损坏 package 不导致接口整体失败
- note_id 不存在时 package 接口返回 404
- 旧 package 缺少 vertical 字段时 fallback 推断

### 1.6 Package 回放测试

- GET /api/verticals/{vertical}/notes/{note_id}/package 返回完整 note_package
- package 缺少字段时前端不崩溃
- 图片缺失时显示"图片缺失"状态
- partial_failed 时展示成功部分并标记失败部分

### 1.7 案例库测试

- GET /api/verticals/nail/cases 返回 nail 案例列表
- 案例列表按 vertical 隔离（outfit vertical 看不到 nail 案例）
- case.vertical 与 request.vertical 不一致时返回 4xx

### 1.8 reference_source 三模式测试

- reference_source=none 时提交任务成功
- reference_source=local_path 时上传参考图后提交任务成功
- reference_source=case_id 时选择案例后提交任务成功

### 1.9 任务进度测试

- queued 状态正确展示
- running 状态正确展示，包含 stage 信息
- succeeded 状态正确展示
- failed 状态展示错误原因和 error_stage
- partial_failed 状态展示可用结果和失败标记
- elapsed_seconds 正确计算

### 1.10 内容预览测试

- Preview 展示标题（selected_title）
- Preview 展示正文（caption/body）
- Preview 展示标签（tags）
- Preview 展示多页内容（pages）
- Preview 展示图片或"图片缺失"
- Preview 展示诊断信息（diagnostics）
- 支持复制标题
- 支持复制正文
- 支持复制标签
- 支持复制单页内容
- 复制全部文案能力

### 1.11 安全渲染测试

- 前端不使用 innerHTML 渲染用户可控内容
- 使用 textContent/createElement 等安全 DOM API

### 1.12 静态资源访问测试

- output 图片 URL 可访问
- input 参考图 URL 可访问
- 路径穿越请求返回 4xx
- 不返回本地绝对路径

### 1.13 回归测试

- /api/nail/... 兼容接口仍可工作
- 旧 package 格式兼容
- 已有自动化测试不因新增代码而失败

---

## 2. 不测试范围

- 多个真实垂直行业的内容质量验证
- 用户登录和多用户隔离
- 云端权限管理
- 自动发布到小红书
- 复杂图片编辑器
- SQL/数据库化改造
- 批量任务队列管理
- 复杂数据看板
- history_note/url/brand_asset/knowledge_base/manual_brief 等扩展 reference_source

---

## 3. 核心测试用例

| 测试编号 | 对应 FR | 测试类型 | 测试目标 | 前置条件 | 操作步骤 | 预期结果 | 自动化/手动 | 优先级 |
|---|---|---|---|---|---|---|---|---|
| TC-000-01 | FR-000 | API 测试 | GET /api/verticals 返回 nail | 服务启动 | GET /api/verticals | 返回 200，body 包含 verticals 数组，nail 在其中 | 自动化 | P0 |
| TC-000-02 | FR-000 | API 测试 | 未知 vertical 返回 4xx | 服务启动 | GET /api/verticals/unknown_vertical | 返回 4xx | 自动化 | P0 |
| TC-000-03 | FR-000 | 前端测试 | 前端显示当前 vertical | Web 页面加载 | 检查页面是否显示 vertical=nail | 显示当前垂类：美甲 nail | 手动 | P0 |
| TC-001-01 | FR-001 | API 测试 | POST /api/verticals/nail/notes 创建任务 | 服务启动 | POST /api/verticals/nail/notes {brief:"测试",reference_source:"none"} | 返回 job_id 和 status=queued | 自动化 | P0 |
| TC-001-02 | FR-001 | API 测试 | 未知 vertical 创建任务失败 | 服务启动 | POST /api/verticals/unknown/notes {brief:"测试"} | 返回 4xx | 自动化 | P0 |
| TC-001-03 | FR-001 | API 测试 | 跨 vertical case_id 创建任务失败 | 服务启动，已有 outfit case | POST /api/verticals/nail/notes {case_id:"case_outfit_xxx"} | 返回 4xx | 自动化 | P0 |
| TC-002-01 | FR-002 | API 测试 | reference_source=none 时不传其他字段 | 服务启动 | POST /api/verticals/nail/notes {reference_source:"none",reference_image_path:"xxx"} | 返回 4xx | 自动化 | P0 |
| TC-002-02 | FR-002 | API 测试 | reference_source=local_path 时必须传 reference_image_path | 服务启动 | POST /api/verticals/nail/notes {reference_source:"local_path"} | 返回 4xx | 自动化 | P0 |
| TC-002-03 | FR-002 | API 测试 | reference_source=case_id 时必须传 case_id | 服务启动 | POST /api/verticals/nail/notes {reference_source:"case_id"} | 返回 4xx | 自动化 | P0 |
| TC-002-04 | FR-002 | 前端测试 | 切换模式时清理不适用字段 | Web 页面加载 | 在基础生成模式填入 brief，切换到参考图模式 | 参考图字段出现，brief 保留 | 手动 | P0 |
| TC-003-01 | FR-003 | API 测试 | POST /api/verticals/nail/reference-images 上传参考图 | 服务启动 | POST /api/verticals/nail/reference-images file=图片文件 | 返回 reference_image_path | 自动化 | P1 |
| TC-003-02 | FR-003 | API 测试 | 非法文件类型被拒绝 | 服务启动 | POST /api/verticals/nail/reference-images file=文本文件 | 返回 4xx | 自动化 | P1 |
| TC-004-01 | FR-004 | API 测试 | GET /api/jobs/{job_id} 返回状态 | 有进行中的 job | GET /api/jobs/{job_id} | 返回 job 对象包含 status | 自动化 | P0 |
| TC-004-02 | FR-004 | API 测试 | 失败任务展示错误信息 | 有失败 job | GET /api/jobs/{job_id} | 返回对象包含 error_message | 自动化 | P0 |
| TC-004-03 | FR-004 | 前端测试 | Progress 展示 stage 和 elapsed_seconds | 有进行中的任务 | 观察 Progress 面板 | 显示当前阶段和已耗时 | 手动 | P0 |
| TC-005-01 | FR-005 | 前端测试 | Preview 展示标题 | 任务成功 | 查看 Preview 模块 | 标题可见 | 手动 | P0 |
| TC-005-02 | FR-005 | 前端测试 | Preview 展示正文 | 任务成功 | 查看 Preview 模块 | 正文可见 | 手动 | P0 |
| TC-005-03 | FR-005 | 前端测试 | Preview 展示标签 | 任务成功 | 查看 Preview 模块 | 标签可见 | 手动 | P0 |
| TC-005-04 | FR-005 | 前端测试 | Preview 展示多页内容 | 任务成功 | 查看 Preview 模块 | pages 可见 | 手动 | P0 |
| TC-005-05 | FR-005 | 前端测试 | 图片缺失时显示状态 | 任务成功但图片缺失 | 查看 Preview 模块 | 显示"图片缺失"而非崩溃 | 手动 | P0 |
| TC-005-06 | FR-005 | 前端测试 | 复制标题功能 | 任务成功 | 点击复制标题按钮 | 剪贴板包含标题 | 手动 | P0 |
| TC-005-07 | FR-005 | 前端测试 | 复制正文功能 | 任务成功 | 点击复制正文按钮 | 剪贴板包含正文 | 手动 | P0 |
| TC-005-08 | FR-005 | 前端测试 | 复制标签功能 | 任务成功 | 点击复制标签按钮 | 剪贴板包含标签 | 手动 | P0 |
| TC-005-09 | FR-005 | 安全测试 | 不使用 innerHTML 渲染用户内容 | 代码审查 | 检查 app.js 中 innerHTML 使用位置 | 用户可控内容不使用 innerHTML | 手动 | P0 |
| TC-006-01 | FR-006 | API 测试 | GET /api/verticals/nail/notes 返回历史列表 | 有历史记录 | GET /api/verticals/nail/notes | 返回 notes 数组 | 自动化 | P0 |
| TC-006-02 | FR-006 | API 测试 | 清空 localStorage 后历史仍可加载 | 有历史记录 | 清空浏览器 localStorage，刷新页面 | 历史记录仍可加载 | 手动 | P0 |
| TC-006-03 | FR-006 | API 测试 | 历史按 vertical 过滤 | 有 nail 和 outfit 历史 | GET /api/verticals/nail/notes | 只返回 nail 历史 | 自动化 | P0 |
| TC-006-04 | FR-006 | API 测试 | 损坏 package 不导致整体失败 | 有损坏 package | GET /api/verticals/nail/notes | 跳过损坏项返回其他记录 | 自动化 | P0 |
| TC-007-01 | FR-007 | API 测试 | GET /api/verticals/nail/notes/{note_id}/package 返回 package | 有历史 note | GET /api/verticals/nail/notes/{note_id}/package | 返回完整 note_package | 自动化 | P0 |
| TC-007-02 | FR-007 | API 测试 | note_id 不存在返回 404 | 无此 note | GET /api/verticals/nail/notes/nonexistent/package | 返回 404 | 自动化 | P0 |
| TC-007-03 | FR-007 | API 测试 | 路径穿越被拒绝 | 恶意请求 | GET /api/verticals/nail/notes/../../../etc/passwd/package | 返回 4xx | 自动化 | P0 |
| TC-008-01 | FR-008 | API 测试 | GET /api/verticals/nail/cases 返回案例列表 | 有案例数据 | GET /api/verticals/nail/cases | 返回 cases 数组 | 自动化 | P0 |
| TC-008-02 | FR-008 | 前端测试 | 案例库有前端入口 | Web 页面加载 | 检查是否有案例库入口 | 有案例库入口或入口 | 手动 | P0 |
| TC-008-03 | FR-008 | 前端测试 | 选择案例后回填生成工作台 | Web 页面加载 | 在案例库选择案例 | 生成模式切换为 case_id，case_id 已填入 | 手动 | P0 |
| TC-008-04 | FR-008 | API 测试 | 跨 vertical case_id 校验 | 已有 outfit case | POST /api/verticals/nail/notes {case_id:"case_outfit_xxx"} | 返回 4xx | 自动化 | P0 |
| TC-011-01 | FR-011 | 安全测试 | 上传文件类型校验 | 服务启动 | POST /api/verticals/nail/reference-images file=非法类型 | 返回 4xx | 自动化 | P0 |
| TC-011-02 | FR-011 | 安全测试 | 路径穿越拒绝 | 服务启动 | 尝试通过 note_id 读取任意文件 | 返回 4xx | 自动化 | P0 |
| TC-011-03 | FR-011 | 安全测试 | 不返回本地绝对路径 | 服务启动 | GET /api/verticals/nail/notes/{note_id}/package | 返回路径不含 /home/、C:\ 等 | 自动化 | P0 |

---

## 4. 每个 Milestone 的测试准入和退出条件

### Milestone 0：需求冻结与基线确认

**准入条件**：
- docs/vertical_content_studio_mvp_v1_requirements.md 已定稿
- 所有 FR 已编号并进入验收矩阵
- 每个 FR 有测试或手动验收方式
- v0 差距已扫描

**退出条件**：
- docs/v1_acceptance_matrix.md 已生成
- docs/v1_test_plan.md 已生成
- docs/v0_gap_analysis.md 已生成
- tasks/v1.0_task_breakdown.md 已生成
- docs/reports/milestone_0_acceptance_report.md 已生成

### Milestone 1：服务端历史与 package 回放

**准入条件**：
- Milestone 0 验收通过
- GET /api/verticals 已实现
- History Service 设计完成

**退出条件**：
- TC-000-01, TC-000-02, TC-006-01, TC-006-03, TC-006-04, TC-007-01, TC-007-02, TC-007-03, TC-009-01（静态资源）, TC-011-02, TC-011-03 通过
- 清空 localStorage 后历史仍可恢复
- package 接口路径安全校验通过

### Milestone 2：生成模式与案例库

**准入条件**：
- Milestone 1 验收通过
- reference_source 三模式设计完成
- Case Service 设计完成

**退出条件**：
- TC-001-01, TC-001-02, TC-001-03, TC-002-01, TC-002-02, TC-002-03, TC-002-04, TC-003-01, TC-003-02, TC-008-01, TC-008-04 通过
- 三种生成模式均可提交任务
- 案例库有前端入口
- case_id 选择后可回填

### Milestone 3：任务进度与内容预览增强

**准入条件**：
- Milestone 2 验收通过
- job status 增强设计完成
- Preview 增强设计完成

**退出条件**：
- TC-004-01, TC-004-02, TC-004-03, TC-005-01, TC-005-02, TC-005-03, TC-005-04, TC-005-05, TC-005-06, TC-005-07, TC-005-08, TC-005-09 通过
- Progress 展示 stage 和 elapsed_seconds
- 复制功能全部可用
- innerHTML 风险已修复

### Milestone 4：整体联调、回归测试与验收冻结

**准入条件**：
- Milestone 3 验收通过
- 所有 Must Have 功能开发完成

**退出条件**：
- 所有 P0 测试通过
- 所有核心用户流程手动跑通
- 无未解释的范围偏差
- 最终验收报告完成

---

## 5. 测试环境要求

### 5.1 本地测试环境

- Python 3.x with FastAPI
- Node.js (for frontend if applicable)
- 端口 8000 可用（API 服务）
- output/ 和 input/ 目录可写

### 5.2 测试数据要求

- 至少 3 条 nail 历史记录
- 至少 3 个 nail 案例
- 至少 1 个损坏的 note_package.json（用于损坏 package 测试）
- 参考图上传测试用图片文件

---

## 6. 测试命令

### API 测试

```bash
python3 -m unittest tests.test_nail_api -v
python3 -m unittest tests.test_nail_history_api -v
python3 -m unittest tests.test_nail_package_api -v
python3 -m unittest tests.test_nail_cases_api -v
python3 -m unittest tests.test_reference_source_validation -v
```

### 前端语法检查

```bash
node --check verticals/nail/web/app.js
```

### E2E 集成测试

```bash
RUN_REAL_IMAGE_TESTS=1 python3 scripts/run_real_nail_image_integration.py
RUN_REAL_IMAGE_TESTS=1 python3 scripts/run_real_nail_ref_image_integration.py /path/to/ref.png
RUN_REAL_IMAGE_TESTS=1 python3 scripts/run_real_nail_case_id_integration.py <case_id>
```

### Python 语法检查

```bash
python3 -m py_compile project_paths.py verticals/nail/api/app.py verticals/nail/api/routes.py verticals/nail/service/nail_note_service.py
```

---

## 7. 手动验收 checklist

### 平台级验收

- [ ] GET /api/verticals 返回 200
- [ ] 返回结果至少包含 nail
- [ ] 未知 vertical 请求返回 4xx
- [ ] 前端页面显示当前 vertical=nail

### nail 垂类验收

- [ ] 基础生成（none）可提交任务
- [ ] 参考图生成（local_path）可上传参考图并提交任务
- [ ] 案例复用（case_id）可选择案例并提交任务
- [ ] 任务进度展示 job_id、status、stage、elapsed_seconds
- [ ] 内容预览展示标题、正文、标签、多页内容、图片或缺失状态
- [ ] 复制标题、正文、标签功能正常
- [ ] 服务端历史列表可加载
- [ ] 清空 localStorage 后历史仍可加载
- [ ] 历史 package 回放正常
- [ ] 案例库有前端入口

### 安全验收

- [ ] 前端不使用 innerHTML 渲染用户可控内容
- [ ] 文件上传校验生效
- [ ] 路径穿越被拒绝
- [ ] 不返回本地绝对路径
- [ ] 跨 vertical case_id 被拒绝

---

## 8. 已知限制

以下限制在 v1.0 中已知但暂不修复，记录于此：

1. **旧 package 字段缺失**：当前 note_package.json 不包含 content_platform、content_type、vertical 字段，v1.0 需在 History Service 中做 fallback 推断
2. **stage 细分不完整**：当前 job status 可能无法提供完整的 stage 信息（如 planning/copywriting/image_generation/qa/saving），需在后续增强
3. **前端 innerHTML**：app.js 第 348/349/994 行使用 innerHTML，需评估是否为用户可控内容
4. **多个真实 vertical 质量验证**：v1.0 只验证 nail 一个 vertical，平台抽象正确性通过代码审查验证

---

## 9. 更新记录

| 日期 | 更新人 | 更新内容 |
|---|---|---|
| 2026-04-30 | Codex/Hermes | 初始创建，基于 docs/vertical_content_studio_mvp_v1_requirements.md 测试方案 |
