# Multi-Agent Image Generation System

多 Agent 协作的图片生成系统，基于 GPT-Image-2（apimart.ai API），支持文生图和图生图两种模式。

## 快速开始

### 环境变量

```bash
export OPENAI_API_KEY=your_api_key_here
# 或
export APIMART_API_KEY=your_api_key_here
```

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
from verticals.nail.schemas import UserInput
from verticals.nail.nail_workflow import NailWorkflow

user_input = UserInput(
    brief="夏日蓝色猫眼短甲，适合黄皮，显白清透",
    style_id="single_seed_summer_cat_eye_short",  # 指定款式
    skin_tone="黄皮",
    nail_length="短甲",
    allow_text_on_image=False,
    reference_image_path="/path/to/ref.png",  # 可选参考图
)

workflow = NailWorkflow()
prepared = workflow.prepare(user_input)       # 生成 Prompt + 文案候选
result = workflow.generate_image(prepared)    # 调用 orchestrator_v2 生成图片
```

**不指定 style_id** 时，系统按关键词自动匹配款式（"合集"→合集封面、"教程"→DIY步骤、"避雷"→翻车对比等）。

每种款式包含完整的：视觉要求（构图/甲型/色系/质感/光线）、图文 Prompt 约束条件、小红书文案模板（标题公式/开头角度/正文结构/评论钩子）、参考图 DNA 继承策略。

## 目录结构

```
.
├── orchestrator_v2.py        # 主工作流编排
├── design_compiler.py        # Prompt 编译器
├── gpt_image2_generator.py  # 文生图 API
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
        ├── nail_workflow.py          # 行业工作流编排
        ├── image_runner_adapter.py   # 桥接到 orchestrator_v2
        ├── prompt_builder.py         # 行业专用 Prompt 构建
        ├── copy_generator.py         # 小红书文案生成
        ├── dna_extractor.py          # 参考图 DNA 提取
        ├── style_matcher.py          # 款式自动匹配
        ├── style_registry.py         # 款式加载
        ├── preview_builder.py         # 预览数据打包
        ├── schemas.py                # 数据模型定义
        └── styles/                   # 7 种款式配置 JSON
```

## 环境变量

| 变量名 | 说明 |
|--------|------|
| `OPENAI_API_KEY` | 主 API Key |
| `APIMART_API_KEY` | apimart API Key（备用） |
| `APIMART_API_BASE` | API 地址（默认 `https://api.apimart.ai`） |
