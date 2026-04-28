
# 任务：高质量实现 Nail 小红书图文笔记生产系统，并完成端到端验证

当前项目路径：

```bash
/Users/wiwi/Vibecoding/project/xhs_nail_agent
```

当前日期：2026-04-28

请你作为这个项目的资深工程实现者，基于项目内的 PRD：

```text
docs/PRD_Nail_Note_Workflow.md
```

实现一个可直接使用的 Nail 垂直行业小红书图文笔记生产工作流。

本任务的核心目标不是“写出一堆文件”，也不是“让单个函数看起来能运行”，而是最终交付一个经过端到端验证的、可以实际调用的工作流：

```python
from verticals.nail.schemas import UserInput
from verticals.nail.note_workflow import NailNoteWorkflow

workflow = NailNoteWorkflow()

package = workflow.generate_note(
    UserInput(
        brief="夏日蓝色猫眼短甲，适合黄皮，显白清透",
        style_id="single_seed_summer_cat_eye_short",
        skin_tone="黄皮",
        nail_length="短甲",
        nail_shape="短方圆",
        note_goal="seed",
        page_count=6,
        allow_text_on_image=True,
        generate_images=True,
        generate_copy=True,
        generate_tags=True,
        quality="final",
        aspect="3:4",
        direction="balanced",
    )
)
```

最终必须能生成：

```text
1. output/nail_*/ 目录
2. 6 页小红书美甲图文笔记图片
3. note_package.json
4. archive.json
5. 至少 10 个标题候选
6. 1 篇完整正文
7. 至少 15 个 TAG
8. 3 到 5 个评论钩子
9. 每页完整的 role、goal、visual_brief、prompt、image_path、status
10. 所有 JSON 路径均为项目相对路径
```

---

## 一、先以始为终：你必须先确认最终交付标准

在开始写代码前，请先阅读并理解：

```text
docs/PRD_Nail_Note_Workflow.md
```

然后从最终可用结果倒推实现路径。

本项目的最终产物不是单张图片，而是一篇完整的小红书美甲图文笔记发布包：

```python
NailNotePackage
```

请始终围绕这个最终产物设计，而不是围绕“生成一张图”设计。

最终交付必须满足：

```text
✅ 用户输入一句美甲需求
✅ 系统自动规划 6 页图文笔记结构
✅ 每页有明确传播任务
✅ 每页有独立 Prompt
✅ 每页可以调用底层图片生成器生成图片
✅ 标题、正文、TAG、评论钩子全部生成
✅ 输出 note_package.json
✅ 输出 archive.json
✅ 所有文件位于 output/nail_*/ 目录
✅ 所有路径为项目相对路径
✅ 不破坏现有 orchestrator_v2.run()
✅ 不破坏现有 verticals.nail.nail_workflow.NailWorkflow
```

不要只做局部实现。不要只创建空文件。不要只写伪代码。不要只实现 generate_images=False 后就停止。最终必须完成真实端到端验证。

---

## 二、重要前置条件：先确认基础单图链路已经可用

在实施 NailNoteWorkflow 之前，请先确认上一阶段的路径统一与图生图修复已经完成。

请检查以下文件：

```text
project_paths.py
orchestrator_v2.py
case_library.py
gpt_image2_generator.py
apimart_image_url_generator.py
case_reference_resolver.py
scripts/repair_case_metadata_paths.py
```

必须确认：

```text
✅ orchestrator_v2.py 使用 project_paths.OUTPUT_DIR
✅ case_library.py 使用 project_paths.CASE_LIBRARY_DIR
✅ gpt_image2_generator.py 默认输出到项目 output/
✅ apimart_image_url_generator.py 支持图生图并下载结果到本地 output/
✅ orchestrator_v2.step3_image_generator() 有参考图时真实调用 generate_image_with_reference()
✅ used_reference 只在真实使用参考图时为 true
✅ 核心运行代码不再使用 ~/.hermes/agents/multi-agent-image
```

如果这些条件未满足，请先修复基础单图链路，再实现本 PRD。不要在有旧路径和伪图生图的基础上继续扩展多页工作流。

路径审计命令：

```bash
grep -RIn "\.hermes\|multi-agent-image\|Path.home()\|/Users/wiwi\|/root/.hermes" \
  --exclude-dir=.git \
  --exclude-dir=.venv \
  --exclude="*.bak*" \
  --exclude="PRD_Nail_Note_Workflow.md" \
  .
```

核心运行代码不得出现旧路径。文档中的禁止示例可以保留，但代码和新生成 JSON 中不能出现旧路径。

---

## 三、总体架构原则

请严格遵守以下架构边界。

### 1. orchestrator_v2.py 只做单图生成底座

`orchestrator_v2.py` 负责：

```text
文生图
图生图
单图 Prompt 编译
单图输出落盘
单图 QA
单图 archive
案例库保存
```

不要把小红书笔记规划、标题、正文、TAG、评论钩子逻辑塞进 `orchestrator_v2.py`。

### 2. verticals/nail/note_workflow.py 做完整笔记编排

新入口应该是：

```python
from verticals.nail.note_workflow import NailNoteWorkflow
```

`NailNoteWorkflow` 负责：

```text
视觉 DNA 构建
笔记页面规划
每页 Prompt 构建
多页图片生成
标题生成
正文生成
TAG 生成
评论钩子生成
笔记级 QA
note_package.json 保存
archive.json 保存
```

### 3. 不破坏旧入口

以下旧入口必须保持可用：

```python
from orchestrator_v2 import run
```

以及：

```python
from verticals.nail.nail_workflow import NailWorkflow
```

如果需要新增能力，优先新增文件和新类，不要粗暴重写旧逻辑。

---

## 四、必须实现的文件和职责

请根据 PRD 实现或扩展以下文件。

```text
verticals/nail/
├── schemas.py
├── note_workflow.py
├── note_templates.py
├── visual_dna_builder.py
├── note_planner.py
├── page_prompt_builder.py
├── note_image_generator.py
├── title_generator.py
├── caption_generator.py
├── tag_generator.py
├── comment_hook_generator.py
├── note_qa.py
├── package_writer.py
└── image_runner_adapter.py
```

职责如下：

```text
schemas.py
- 定义或扩展 UserInput
- 新增 NoteGoal
- 新增 PageRole
- 新增 VisualDNA
- 新增 NotePageSpec
- 新增 NailNotePackage

note_templates.py
- 根据 note_goal 或 style_id 返回页面角色模板

visual_dna_builder.py
- 从用户输入、style_id、reference_image_path、case_id 构建 VisualDNA

note_planner.py
- 根据模板生成 NotePageSpec 列表

page_prompt_builder.py
- 将 NotePageSpec + VisualDNA + UserInput 编译成每页图片 Prompt

note_image_generator.py
- 批量调用单图生成器生成每页图片
- 将生成结果写回 page.image_path、page.status、page.used_reference

title_generator.py
- 生成至少 10 个标题候选

caption_generator.py
- 生成完整正文

tag_generator.py
- 生成至少 15 个 TAG，最多 25 个

comment_hook_generator.py
- 生成 3 到 5 个评论钩子

note_qa.py
- 对整篇 NailNotePackage 做规则 QA

package_writer.py
- 保存 note_package.json 和 archive.json
- 确保所有路径为项目相对路径

note_workflow.py
- 顶层编排入口 NailNoteWorkflow.generate_note()

image_runner_adapter.py
- 桥接到 orchestrator_v2.run()
- 不要在上层直接散落调用 run()
```

---

## 五、Schema 要求

请优先实现 Schema，因为它是模块之间的数据契约。

`UserInput` 必须向后兼容已有字段，并新增以下字段：

```python
brief: str

style_id: str | None = None
skin_tone: str | None = None
nail_length: str | None = None
nail_shape: str | None = None

note_goal: str = "seed"
note_template: str | None = None
page_count: int = 6

allow_text_on_image: bool = False
reference_image_path: str | None = None
case_id: str | None = None

generate_images: bool = True
generate_copy: bool = True
generate_tags: bool = True

quality: str = "final"
aspect: str = "3:4"
direction: str = "balanced"
```

请注意 Pydantic 版本兼容。如果项目是 Pydantic v1，不要只写 v2 API。如果项目是 Pydantic v2，也要确保序列化 helper 能兼容。

建议提供 helper：

```python
def model_to_dict(model):
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()
```

必须新增：

```python
class NoteGoal(str, Enum):
    seed = "seed"
    tutorial = "tutorial"
    comparison = "comparison"
    warning = "warning"
    collection = "collection"
    conversion = "conversion"
```

必须新增：

```python
class PageRole(str, Enum):
    cover = "cover"
    detail_closeup = "detail_closeup"
    skin_tone_fit = "skin_tone_fit"
    style_breakdown = "style_breakdown"
    scene_mood = "scene_mood"
    avoid_mistakes = "avoid_mistakes"
    save_summary = "save_summary"
    materials = "materials"
    step_by_step = "step_by_step"
    comparison_grid = "comparison_grid"
    collection_grid = "collection_grid"
```

必须新增：

```python
class VisualDNA(BaseModel):
    skin_tone: str | None = None
    hand_model: str | None = None
    nail_length: str | None = None
    nail_shape: str | None = None
    main_color: str | None = None
    finish: str | None = None
    lighting: str | None = None
    background: str | None = None
    style: str | None = None
    negative: list[str] = []
    source_reference: str | None = None
```

必须新增：

```python
class NotePageSpec(BaseModel):
    page_no: int
    role: PageRole
    goal: str

    visual_brief: str
    text_overlay: str | None = None
    caption: str | None = None

    prompt: str | None = None
    negative_prompt: str | None = None

    image_path: str | None = None
    image_url: str | None = None
    used_reference: bool = False

    status: str = "planned"
    score: float | None = None
    issues: list[str] = []
```

必须新增：

```python
class NailNotePackage(BaseModel):
    note_id: str
    brief: str
    style_id: str | None = None
    note_goal: NoteGoal = NoteGoal.seed
    note_template: str | None = None

    visual_dna: VisualDNA
    pages: list[NotePageSpec]

    title_candidates: list[str] = []
    selected_title: str | None = None
    body: str | None = None
    tags: list[str] = []
    comment_hooks: list[str] = []

    output_dir: str | None = None
    package_path: str | None = None
    archive_path: str | None = None

    success: bool = False
    partial_failure: bool = False
    diagnostics: dict = {}
```

---

## 六、必须支持 generate_images=False

这是第一阶段必须跑通的模式。

当：

```python
generate_images=False
```

时，系统不得调用图片 API，但必须完整输出：

```text
NailNotePackage
pages
每页 role
每页 goal
每页 visual_brief
每页 prompt
title_candidates
selected_title
body
tags
comment_hooks
note_package.json
archive.json
```

每页状态可以是：

```text
prompt_ready
```

或者：

```text
planned
```

但 package 应该成功：

```python
package.success == True
package.partial_failure == False
```

这是快速调试模式，必须稳定可用。

---

## 七、必须支持 generate_images=True

当：

```python
generate_images=True
```

时，系统必须真实调用底层图片生成链路。

每页应：

```text
1. 构建 page.prompt
2. 调用 image_runner_adapter
3. image_runner_adapter 调用 orchestrator_v2.run()
4. 获取图片路径
5. 将图片移动或复制到当前 note 输出目录
6. 重命名为 page_XX_role.png
7. 写回 page.image_path
8. 设置 page.status = "generated"
```

输出目录示例：

```text
output/
└── nail_20260428_230000_summer_blue_cat_eye/
    ├── page_01_cover.png
    ├── page_02_detail_closeup.png
    ├── page_03_skin_tone_fit.png
    ├── page_04_style_breakdown.png
    ├── page_05_scene_mood.png
    ├── page_06_save_summary.png
    ├── note_package.json
    └── archive.json
```

图片路径写入 JSON 时必须是：

```text
output/nail_20260428_230000_summer_blue_cat_eye/page_01_cover.png
```

禁止写入绝对路径。

---

## 八、默认 6 页种草模板必须正确

对于输入：

```text
夏日蓝色猫眼短甲，适合黄皮，显白清透
```

且：

```python
note_goal="seed"
page_count=6
style_id="single_seed_summer_cat_eye_short"
```

默认页面结构必须是：

```text
1. cover
2. detail_closeup
3. skin_tone_fit
4. style_breakdown
5. scene_mood
6. save_summary
```

每页必须有明确任务：

```text
cover：抓点击，展示最终效果
detail_closeup：展示猫眼光泽和甲面质感
skin_tone_fit：解决黄皮显白顾虑
style_breakdown：提供颜色、甲型、质感等复刻信息
scene_mood：增加夏日生活方式代入
save_summary：促收藏，给美甲师看的总结
```

如果 page_count=7，可以加入：

```text
avoid_mistakes
```

---

## 九、视觉 DNA 必须贯穿所有页面

必须构建 `VisualDNA`，并注入每一页 Prompt。

对于示例输入，默认 DNA 应接近：

```python
VisualDNA(
    skin_tone="黄皮",
    hand_model="自然亚洲女性手型",
    nail_length="短甲",
    nail_shape="短方圆",
    main_color="清透冰蓝",
    finish="猫眼磁粉，玻璃感，高光泽",
    lighting="夏日自然光，柔和明亮",
    background="干净浅色背景，小红书风格",
    style="清透、显白、日常、精致",
    negative=[
        "长尖甲",
        "暗沉灰蓝",
        "欧美夸张风",
        "廉价闪粉",
        "过度磨皮",
        "多余手指",
        "畸形手部"
    ]
)
```

每页 Prompt 都必须包含这些信息，避免多页图像发生手型、肤色、甲型、颜色漂移。

---

## 十、标题、正文、TAG、评论钩子要求

### 标题

必须生成至少 10 个标题候选，覆盖：

```text
痛点型
结果型
人群型
场景型
收藏型
反差型
细节型
趋势型
轻种草型
转化型
```

示例：

```text
黄皮别怕蓝色！这组猫眼短甲真的显白
做完手白一个度的冰蓝猫眼短甲
短甲姐妹一定要试试这款蓝猫眼
夏天去海边就做这款清透蓝猫眼
给美甲师看这张就够了
```

`selected_title` 默认可以选第一个。

### 正文

正文必须包含：

```text
开头钩子
款式描述
适合人群
细节亮点
避雷建议
给美甲师看的复刻关键词
互动结尾
```

不能只写空泛描述。

### TAG

必须生成至少 15 个，最多 25 个，且去重。

必须包含类似：

```text
美甲
夏日美甲
猫眼美甲
蓝色美甲
短甲美甲
清透美甲
黄皮显白美甲
美甲参考
给美甲师看
```

### 评论钩子

必须生成 3 到 5 个。

示例：

```text
你们觉得这款蓝猫眼更适合短甲还是中长甲？
黄皮姐妹会不会敢尝试这种清透蓝？
想要我整理一组不显黑的蓝色美甲吗？
如果拿去给美甲师看，你会选第几页？
下一期想看粉色显白款还是裸色通勤款？
```

---

## 十一、路径要求

所有新代码必须使用：

```python
from project_paths import PROJECT_ROOT, OUTPUT_DIR, to_project_relative, resolve_project_path
```

禁止新增：

```python
Path.home()
```

禁止新增：

```text
~/.hermes/agents/multi-agent-image
```

禁止将本机绝对路径写入：

```text
note_package.json
archive.json
```

所有输出路径必须是项目相对路径。

允许：

```text
output/nail_20260428_230000_summer_blue_cat_eye/page_01_cover.png
```

禁止：

```text
/Users/wiwi/Vibecoding/project/xhs_nail_agent/output/...
```

禁止：

```text
~/.hermes/agents/multi-agent-image/output/...
```

---

## 十二、错误处理要求

### 普通内页失败

如果普通内页失败：

```python
page.status = "failed"
page.issues.append(str(error))
package.partial_failure = True
```

继续生成后续页面。

### 封面页失败

如果封面页失败：

```python
package.success = False
package.partial_failure = True
package.diagnostics["failed_reason"] = "cover_generation_failed"
```

仍然保存 `note_package.json`，方便排查。

### 文案生成失败

如果标题、正文、TAG、评论钩子生成失败，必须有规则 fallback，不允许整个流程崩溃。

### package 保存失败

如果 `note_package.json` 保存失败，需要记录：

```python
package.diagnostics["package_write_error"] = str(error)
```

并返回内存中的 package。

---

## 十三、日志要求

请输出清晰日志，方便人类判断每一步是否成功。

建议格式：

```text
======================================================================
💅 Nail Note Workflow - 小红书美甲图文笔记生产
======================================================================
📝 需求: 夏日蓝色猫眼短甲，适合黄皮，显白清透
🎯 目标: seed
📄 页数: 6

[视觉DNA] ✅ 构建完成：黄皮 / 短甲 / 短方圆 / 清透冰蓝 / 猫眼玻璃感
[笔记规划] ✅ 已生成 6 页结构
[页面Prompt] ✅ page_01_cover prompt ready
[图片生成] 🖼️ 开始生成 page_01_cover
[图片生成] ✅ page_01_cover -> output/nail_.../page_01_cover.png
[标题生成] ✅ 已生成 10 个标题候选
[正文生成] ✅ 正文生成完成
[TAG生成] ✅ 已生成 18 个 TAG
[评论钩子] ✅ 已生成 5 个评论钩子
[QA] ✅ PASS score=9.1
[发布包] ✅ note_package.json 已保存
```

---

## 十四、实施阶段要求

请不要一次性盲目大改。请分阶段实现并验证。

---

### Phase 1：规划模式闭环

目标：不调用图片 API，先跑通完整发布包生成。

实现：

```text
schemas.py
note_templates.py
visual_dna_builder.py
note_planner.py
page_prompt_builder.py
title_generator.py
caption_generator.py
tag_generator.py
comment_hook_generator.py
note_qa.py
package_writer.py
note_workflow.py
```

必须通过以下命令：

```bash
python - <<'PY'
from pathlib import Path
from verticals.nail.schemas import UserInput
from verticals.nail.note_workflow import NailNoteWorkflow

workflow = NailNoteWorkflow()

package = workflow.generate_note(
    UserInput(
        brief="夏日蓝色猫眼短甲，适合黄皮，显白清透",
        style_id="single_seed_summer_cat_eye_short",
        skin_tone="黄皮",
        nail_length="短甲",
        nail_shape="短方圆",
        note_goal="seed",
        page_count=6,
        allow_text_on_image=True,
        generate_images=False,
        generate_copy=True,
        generate_tags=True,
    )
)

print("success:", package.success)
print("partial_failure:", package.partial_failure)
print("note_id:", package.note_id)
print("output_dir:", package.output_dir)
print("package_path:", package.package_path)
print("pages:", len(package.pages))
print("titles:", len(package.title_candidates))
print("tags:", len(package.tags))
print("comment_hooks:", len(package.comment_hooks))

assert package.success is True
assert len(package.pages) == 6
role = package.pages[0].role.value if hasattr(package.pages[0].role, "value") else package.pages[0].role
assert role == "cover"
assert all(p.goal for p in package.pages)
assert all(p.visual_brief for p in package.pages)
assert all(p.prompt for p in package.pages)
assert len(package.title_candidates) >= 10
assert package.selected_title
assert package.body
assert len(package.tags) >= 15
assert len(package.comment_hooks) >= 3
assert package.package_path
assert Path(package.package_path).exists()

print("✅ planning mode passed")
PY
```

如果失败，请修复，不要跳过。

---

### Phase 2：真实多页图片生成

目标：接入底层单图生成器，真实生成 6 页图片。

实现：

```text
note_image_generator.py
image_runner_adapter.py
```

并补齐必要的图片文件移动、复制、重命名逻辑。

必须通过：

```bash
python - <<'PY'
from pathlib import Path
from verticals.nail.schemas import UserInput
from verticals.nail.note_workflow import NailNoteWorkflow

workflow = NailNoteWorkflow()

package = workflow.generate_note(
    UserInput(
        brief="夏日蓝色猫眼短甲，适合黄皮，显白清透",
        style_id="single_seed_summer_cat_eye_short",
        skin_tone="黄皮",
        nail_length="短甲",
        nail_shape="短方圆",
        note_goal="seed",
        page_count=6,
        allow_text_on_image=True,
        generate_images=True,
        generate_copy=True,
        generate_tags=True,
        quality="final",
        aspect="3:4",
        direction="balanced",
    )
)

print("success:", package.success)
print("partial_failure:", package.partial_failure)
print("output_dir:", package.output_dir)
print("package_path:", package.package_path)

for page in package.pages:
    print(page.page_no, page.role, page.status, page.image_path, page.used_reference)

assert package.output_dir.startswith("output/nail_")
assert package.package_path.startswith("output/nail_")
assert len(package.pages) == 6
assert package.pages[0].image_path is not None
assert package.pages[0].image_path.startswith("output/")
assert Path(package.package_path).exists()

for page in package.pages:
    if page.status == "generated":
        assert page.image_path
        assert page.image_path.startswith("output/")
        assert Path(page.image_path).exists()

print("✅ image mode basic checks passed")
PY
```

如果环境变量中没有 API key，不要伪造成功。请明确说明缺少 API key，并保证 `generate_images=False` 已完整通过。同时保留 `generate_images=True` 的可执行代码和命令。

---

### Phase 3：case_id 和参考图链路

目标：支持参考图和案例库图生图。

必须支持：

```python
UserInput(
    ...,
    case_id="case_001",
    generate_images=True,
)
```

以及：

```python
UserInput(
    ...,
    reference_image_path="case_library/poster/case_001_xxx/image.png",
    generate_images=True,
)
```

要求：

```text
✅ 能解析 case_id
✅ 能找到项目内 case_library 图片
✅ 能传入每页图片生成链路
✅ 有参考图时真实走图生图
✅ used_reference 只在真实使用图生图时为 true
✅ note_package.json 记录 source_reference
```

验收命令：

```bash
python - <<'PY'
from verticals.nail.schemas import UserInput
from verticals.nail.note_workflow import NailNoteWorkflow

workflow = NailNoteWorkflow()

package = workflow.generate_note(
    UserInput(
        brief="生成一篇夏日蓝色猫眼短甲的小红书图文笔记，适合黄皮，清透显白",
        style_id="single_seed_summer_cat_eye_short",
        skin_tone="黄皮",
        nail_length="短甲",
        nail_shape="短方圆",
        note_goal="seed",
        page_count=6,
        case_id="case_001",
        allow_text_on_image=True,
        generate_images=True,
        generate_copy=True,
        generate_tags=True,
        quality="final",
        aspect="3:4",
        direction="balanced",
    )
)

print("success:", package.success)
print("source_reference:", package.visual_dna.source_reference)
for page in package.pages:
    print(page.page_no, page.role, page.status, page.used_reference, page.image_path)
PY
```

---

## 十五、最终路径审计

实现完成后必须执行：

```bash
grep -RIn "\.hermes\|multi-agent-image\|Path.home()\|/Users/wiwi\|/root/.hermes" \
  --exclude-dir=.git \
  --exclude-dir=.venv \
  --exclude="*.bak*" \
  --exclude="PRD_Nail_Note_Workflow.md" \
  .
```

要求：

```text
✅ 核心运行代码中不得出现旧路径
✅ 新生成的 output/nail_*/note_package.json 中不得出现旧路径
✅ 新生成的 output/nail_*/archive.json 中不得出现旧路径
```

如果 grep 命中代码中的旧路径，请修复后重新运行。

---

## 十六、最终 note_package.json 检查

请执行：

```bash
python - <<'PY'
import json
from pathlib import Path

candidates = sorted(Path("output").glob("nail_*/note_package.json"))
assert candidates, "No note_package.json found"

latest = candidates[-1]
print("checking:", latest)

data = json.loads(latest.read_text(encoding="utf-8"))

assert data["note_id"].startswith("nail_")
assert data["output_dir"].startswith("output/nail_")
assert data["package_path"].startswith("output/nail_")
assert len(data["pages"]) >= 6
assert data["pages"][0]["role"] == "cover"
assert len(data["title_candidates"]) >= 10
assert data["selected_title"]
assert data["body"]
assert len(data["tags"]) >= 15
assert len(data["comment_hooks"]) >= 3

text = latest.read_text(encoding="utf-8")
for forbidden in [".hermes", "multi-agent-image", "/Users/wiwi", "/root/.hermes"]:
    assert forbidden not in text, f"Forbidden path found: {forbidden}"

print("✅ note_package.json passed")
PY
```

---

## 十七、最终交付内容

完成后请输出以下内容：

```text
1. 修改文件列表
2. 新增文件列表
3. 核心实现说明
4. generate_images=False 验证结果
5. generate_images=True 验证结果
6. case_id / reference_image_path 验证结果
7. 路径审计 grep 结果
8. note_package.json 示例路径
9. output/nail_*/ 目录结构
10. 已知限制和后续建议
```

请注意：如果某个验证没有通过，不要只说明失败原因。你需要继续修复，直到通过为止。只有在外部条件缺失，例如 API key 未配置、网络不可用、图片 API 服务不可访问时，才允许说明阻塞原因。但即使如此，规划模式 `generate_images=False` 必须完整通过。

---

## 十八、Definition of Done

只有以下条件全部满足，才算完成本任务：

```text
✅ docs/PRD_Nail_Note_Workflow.md 已被正确理解并落实
✅ NailNoteWorkflow.generate_note() 可调用
✅ generate_images=False 完整通过
✅ generate_images=True 在 API key 可用时可真实生成多页图片
✅ 默认 6 页种草模板正确
✅ 每页有 role、goal、visual_brief、prompt、status
✅ 每页生成成功时有 image_path
✅ 图片输出到 output/nail_*/page_XX_role.png
✅ note_package.json 写入 output/nail_*/note_package.json
✅ archive.json 写入 output/nail_*/archive.json
✅ 标题候选不少于 10 个
✅ 正文非空且结构完整
✅ TAG 不少于 15 个
✅ 评论钩子不少于 3 个
✅ 所有 JSON 路径为项目相对路径
✅ 不出现旧 Hermes 路径
✅ 不破坏 orchestrator_v2.run()
✅ 不破坏 verticals.nail.nail_workflow.NailWorkflow
✅ 最终贴出真实验证命令输出
```

请从现在开始实施。先检查当前代码状态，再分阶段修改，最后执行完整验收。
