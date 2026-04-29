# Multi-Agent Image Generation System

多 Agent 协作的图片生成系统，支持通过统一 `LLMProvider` 配置接入 OpenAI-compatible LLM 与图像 provider，当前内置 `openai` 与 `apimart` 两个 provider。

## 快速开始

### 环境变量

```bash
export LLM_PROVIDER=apimart
export APIMART_API_KEY=your_api_key_here
export APIMART_API_BASE=https://api.apimart.ai/v1

# 或切到 OpenAI 官方
export LLM_PROVIDER=openai
export OPENAI_API_KEY=your_api_key_here

# 可选：按业务别名覆盖模型
export TEXT_MODEL_COPY_SMALL=gpt-4o-mini
export TEXT_MODEL_PLANNER_SMALL=gpt-4o-mini
export TEXT_MODEL_TAG_SMALL=gpt-4o-mini
export TEXT_MODEL_HOOK_SMALL=gpt-4o-mini
export TEXT_MODEL_VISION_SMALL=gpt-4o-mini
export IMAGE_MODEL_DEFAULT=gpt-image-2
```

说明：

- 所有 provider key 只应保存在服务端环境变量中。
- 未来 Web 或手机 App 接入时，前端应调用你自己的后端接口，而不是直接持有 provider key。
- 业务模块不再依赖固定厂商模型名，而是通过模型别名解析真实模型。

### 快速生成

```bash
# 交互模式
python interactive_run.py

# 直接生成（文生图）
python gpt_image2_generator.py '一张夏日清凉感海报' 3:4

# 快速启动
python quick_start.py

# 批量生成
python batch_generator_v2.py
```

## 核心模块

### orchestrator_v2.py — 主工作流

五阶段处理管道：

1. **Prompt 工程师** — 需求分析与优化（当前为透传模式）
2. **风格研究员** — 确定任务类型、方向、比例
3. **图片生成引擎** — 调用 GPT-Image-2 生成图片
4. **质量审核** — 评估生成结果
5. **档案管理** — 保存生成记录

```
用户输入 → Prompt工程师 → 风格研究员 → 设计编译器 → 图片生成引擎
                                                              ↓
              ← QA ← 档案管理 ← 案例库 ← 生成结果
```

### LLMProvider — 统一 provider 配置层

`src/llm_provider.py` 负责：

- 选择当前活跃 provider：`openai` 或 `apimart`
- 解析 provider 的 `api_key` 与 `base_url`
- 提供统一的 OpenAI-compatible client factory
- 通过业务别名解析文本与图片模型

当前业务别名包括：

- `planner_small`
- `copy_small`
- `tag_small`
- `hook_small`
- `vision_small`
- `image_default`

### 文生图 vs 图生图

- **文生图**：`gpt_image2_generator.py` → `submit_task()` + `wait_for_completion()` + `download_image()`
- **图生图**：`apimart_image_url_generator.py` → `upload_reference_image()` + `create_image_generation_task()` + `wait_for_task_result()`

生成结果统一通过 `_normalize_generation_result()` 标准化处理。

### design_compiler.py — 设计 Prompt 编译器

将自然语言需求编译成结构化 Prompt，包含：

| 维度 | 选项 |
|------|------|
| 任务类型 | `poster` / `product` / `ppt` / `infographic` / `teaching` |
| 风格方向 | `conservative` / `balanced` / `bold` |
| 图片比例 | `1:1` / `3:4` / `4:3` / `16:9` / `9:16` 等 |
| 质量档位 | `draft`（2K）/ `final` / `premium`（3K） |

### case_library.py — 案例库

保存历史生成案例，支持风格复用：

```bash
python case_library.py list          # 列出所有案例
python case_library.py search 关键词   # 搜索案例
```

案例按任务类型分类存放：`case_library/{poster,product,ppt,infographic,teaching}/`

每个案例包含：`image.png` + `metadata.json`

### verticals/nail — 小红书美甲图文垂类

独立垂直行业工作流，面向小红书美甲图文场景，通过 `MultiAgentImageRunner` 桥接到通用 orchestrator。

**7 种款式：**

| style_id | 场景 | 方向 | 比例 |
|---|---|---|---|
| `single_seed_summer_cat_eye_short` | 单款种草 | balanced | 3:4 |
| `collection_cover_6_grid_whitening` | 合集封面（6款） | bold | 3:4 |
| `tutorial_diy_step_by_step` | 教程/DIY步骤 | balanced | 3:4 |
| `warning_before_after_nail_fail` | 避雷/翻车对比 | conservative | 3:4 |
| `comparison_color_skin_tone_test` | 颜色测评/显白 | balanced | 3:4 |
| `story_mood_date_travel_nail` | 故事/氛围/旅行 | bold | 3:4 |
| `trend_fast_follow_from_viral` | 爆款/跟款趋势 | bold | 3:4 |

**使用方式：**

```python
from verticals.nail.note_workflow import NailNoteWorkflow
from verticals.nail.note_workflow_schemas import NailNoteUserInput

workflow = NailNoteWorkflow()

# generate_images=False：只生成文案，不生成图片
package = workflow.generate_note(
    NailNoteUserInput(
        brief="夏日蓝色猫眼短甲，适合黄皮，显白清透",
        style_id="single_seed_summer_cat_eye_short",
        skin_tone="黄皮",
        nail_length="短甲",
        nail_shape="短方圆",
        note_goal="seed",
        page_count=6,
        generate_images=False,
    )
)
print(f"success={package.success}, title={package.selected_title}")
```

```python
# generate_images=True：生成文案 + 图片
package = workflow.generate_note(
    NailNoteUserInput(
        brief="夏日蓝色猫眼短甲，适合黄皮，显白清透",
        style_id="single_seed_summer_cat_eye_short",
        skin_tone="黄皮",
        nail_length="短甲",
        nail_shape="短方圆",
        note_goal="seed",
        page_count=6,
        generate_images=True,
        reference_image_path="/path/to/ref.png",  # 可选参考图
    )
)
print(f"success={package.success}, pages={len(package.pages)}")
for page in package.pages:
    print(f"  page_{page.page_no}: status={page.status}, image={page.image_path}")
```

**兼容导入方式（PRD 验收可用）：**

```python
from verticals.nail.schemas import NailNoteUserInput
```

**不指定 style_id** 时，系统按关键词自动匹配款式（"合集"→合集封面、"教程"→DIY步骤、"避雷"→翻车对比等）。

每种款式包含完整的：视觉要求（构图/甲型/色系/质感/光线）、图文 Prompt 约束条件、小红书文案模板（标题公式/开头角度/正文结构/评论钩子）、参考图 DNA 继承策略。

## 目录结构

```
.
├── orchestrator_v2.py        # 主工作流编排
├── design_compiler.py        # Prompt 编译器
├── gpt_image2_generator.py   # 文生图 API
├── apimart_image_url_generator.py  # 图生图 API
├── case_library.py           # 案例库管理
├── project_paths.py          # 路径管理工具
├── batch_generator_v2.py     # 批量生成
├── interactive_run.py        # 交互式生成
├── quick_start.py            # 快速启动
├── output/                   # 生成结果输出目录
├── case_library/            # 案例库存储目录
│   ├── poster/
│   ├── product/
│   ├── ppt/
│   ├── infographic/
│   └── teaching/
└── verticals/               # 垂直行业工作流
    └── nail/                # 小红书美甲图文
        ├── note_workflow.py          # 笔记工作流编排（NailNoteWorkflow）
        ├── note_workflow_schemas.py  # 笔记数据模型（Pydantic）
        ├── note_planner.py           # 页面规划器
        ├── page_prompt_builder.py    # 页面 Prompt 编译器
        ├── note_image_generator.py   # 笔记图片生成器
        ├── note_qa.py                # 笔记 QA 检查
        ├── package_writer.py         # 发布包写入
        ├── title_generator.py        # 标题生成
        ├── caption_generator.py      # 正文生成
        ├── tag_generator.py          # TAG 生成
        ├── comment_hook_generator.py # 评论钩子生成
        ├── visual_dna_builder.py     # 视觉 DNA 构建
        ├── image_runner_adapter.py   # 桥接到 orchestrator_v2
        ├── schemas.py                # 数据模型定义（re-export）
        └── styles/                   # 款式配置 JSON
```

## 环境变量

| 变量名 | 说明 |
|--------|------|
| `LLM_PROVIDER` | 当前 provider，支持 `openai` / `apimart` |
| `OPENAI_API_KEY` | `openai` provider 的服务端 API Key |
| `OPENAI_API_BASE` | 可选，自定义 OpenAI-compatible base URL |
| `APIMART_API_KEY` | `apimart` provider 的服务端 API Key |
| `APIMART_API_BASE` | `apimart` base URL，默认 `https://api.apimart.ai/v1` |
| `TEXT_MODEL_PLANNER_SMALL` | 可选，覆盖页面规划类文本模型 |
| `TEXT_MODEL_COPY_SMALL` | 可选，覆盖标题/正文类文本模型 |
| `TEXT_MODEL_TAG_SMALL` | 可选，覆盖标签生成模型 |
| `TEXT_MODEL_HOOK_SMALL` | 可选，覆盖评论钩子生成模型 |
| `TEXT_MODEL_VISION_SMALL` | 可选，覆盖视觉分析/视觉DNA模型 |
| `IMAGE_MODEL_DEFAULT` | 可选，覆盖默认图片模型 |
