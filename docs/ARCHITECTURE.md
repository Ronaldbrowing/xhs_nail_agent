# Multi-Agent Image 业务逻辑图

## 整体架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              入口层                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐    │
│  │ quick_start │  │interactive_ │  │batch_       │  │ orchestrator_v2 │    │
│  │    .py      │  │  run.py      │  │generator_v2 │  │     .py         │    │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └────────┬────────┘    │
└─────────┼────────────────┼────────────────┼──────────────────┼──────────────┘
          │                │                │                  │
          ▼                ▼                ▼                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        run() — 主工作流引擎                                   │
│                         (orchestrator_v2.py)                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 完整业务流程（orchestrator_v2.py）

```
用户输入 (user_input)
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 1: Prompt 工程师 (step1_prompt_engineer)                  │
│  ─────────────────────────────────────────────────────────────  │
│  输入: user_input                                                │
│  处理: 轻量透传（当前为 fallback 模式，无 AI 优化）                 │
│  输出: { core_subject, optimized_brief, mode }                  │
│                                                                  │
│  判断: precompiled_brief ?                                       │
│    ├─ True  → 跳过，brief = user_input                          │
│    └─ False → 调用 step1_prompt_engineer()                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: 风格研究员 (step2_style_scout)                          │
│  ─────────────────────────────────────────────────────────────  │
│  输入: brief                                                    │
│  处理: 任务类型检测 + 参数推荐                                    │
│  输出: { task, direction, aspect, quality }                      │
│                                                                  │
│  判断: task/direction/aspect 已强制指定 ?                       │
│    ├─ Yes → 使用强制参数，返回 style_data (reasoning="强制参数")  │
│    └─ No  → 调用 step2_style_scout() 获取推荐                    │
│                                                                  │
│  task: poster | product | ppt | infographic | teaching         │
│  direction: conservative | balanced | bold                      │
│  aspect: 1:1 | 3:4 | 4:3 | 16:9 | 9:16 | ...                   │
│  quality: draft | final | premium                                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  参考图解析                                                       │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  判断: use_reference=True 且 case_id 已提供 ?                   │
│    ├─ Yes → get_case_image_path(case_id, task)                  │
│    │         │                                                  │
│    │         ▼                                                  │
│    │    找到 ? ──No──→ try_resolve_case_image_path() 二次解析    │
│    │      │                     │                                │
│    │     Yes                    ▼                                │
│    │      │              也找到 ? ──No──→ reference_image = None │
│    │      │               │                                     │
│    │      │              Yes                                    │
│    │      ▼               ▼                                     │
│    │   使用该路径    也使用该路径                                  │
│    │      │              │                                      │
│    └──────┼──────────────┼──────────────────────────────────────┘
│           │              │
│           ▼              ▼
┌─────────────────────────────────────────────────────────────────┐
│  DNA 摘要注入（可选）                                              │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  判断: dna_summary 未提供 且 use_reference=True 且 case_id ?    │
│    ├─ Yes → get_case_metadata(case_id, task)                    │
│    │         │                                                  │
│    │         ▼                                                  │
│    │    找到 metadata ?                                         │
│    │      ├─ Yes → build_dna_summary_from_case_meta()          │
│    │      │         │                                            │
│    │      │         ▼                                            │
│    │      │      brief = brief + "\n\n【参考图DNA摘要】\n" + dna │
│    │      └─ No → 跳过                                           │
│    └─ No → 跳过                                                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 3: 图片生成引擎 (step3_image_generator)                     │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  ① compile_prompt_package() — 设计编译器                         │
│     输入: brief, task, direction, aspect, quality                │
│     处理: TASK_PROFILES + DIRECTION_PROFILES + ASPECT_SIZES     │
│     输出: final_prompt (结构化设计 Prompt)                        │
│                                                                  │
│  ② 判断: reference_image 存在 ?                                  │
│                                                                  │
│     ┌──────────┐    Yes    ┌──────────────────────────────────┐ │
│     │ 纯文生图  │ ◄────────│ 图生图 (img2img)                  │ │
│     │          │          │                                   │ │
│     │generate_  │          │ generate_image_with_reference()  │ │
│     │ image()  │          │   │                                │ │
│     │ (gpt_    │          │   ├─ upload_reference_image()     │ │
│     │ image2_  │          │   ├─ create_image_generation_task │ │
│     │ generator│          │   └─ wait_for_task_result()       │ │
│     │ .py)     │          │                                   │ │
│     └────┬─────┘          └───────────────┬───────────────────┘ │
│          │                                  │                     │
│          │        API 调用（apimart.ai）     │                     │
│          │                                  │                     │
│          ▼                                  ▼                     │
│     ┌─────────────────────────────────────────────────────────┐   │
│     │  _normalize_generation_result() — 统一返回格式          │   │
│     │  输出: { success, filepath, url, task_id, used_ref }   │   │
│     └────────────────────────────┬────────────────────────────┘   │
└─────────────────────────────────┼─────────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │  generation.status !=      │
                    │  "success" ?               │
                    ▼                            ▼
┌────────────────────────────┐    ┌────────────────────────────────┐
│      直接返回失败           │    │  Step 4: QA (step4_qa)         │
│                            │    │  ────────────────────────────  │
│  { success: False,        │    │  判断: generation.status ==   │
│    stage: "generation",   │    │  "success" ?                    │
│    error: ... }           │    │    ├─ Yes → score=9.0, PASS     │
│                            │    │    └─ No  → score=0.0, FAIL    │
└────────────────────────────┘    └────────────────┬────────────────┘
                                                    │
                                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 5: 档案归档 (step5_metadata)                               │
│  ─────────────────────────────────────────────────────────────  │
│  输出: output/{timestamp}_archive.json                          │
│  内容: timestamp, user_input, prompt_analysis, style_params,   │
│        generation(normalized filepath), quality_check,          │
│        workflow_diagnostics, model_usage, dna_summary            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  案例库保存 (auto_save_to_library)                               │
│  ─────────────────────────────────────────────────────────────  │
│  判断: generation.status == "success" ?                          │
│    ├─ Yes → add_case(filepath, metadata, task)                  │
│    │         │                                                  │
│    │         ▼                                                  │
│    │    case_library/{task}/case_XXX_name/                      │
│    │      ├─ image.png                                          │
│    │      └─ metadata.json                                       │
│    └─ No → 跳过                                                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                       最终结果返回
```

---

## img2img 图生图详细流程

```
用户传入 reference_image_path
            │
            ▼
┌─────────────────────────────────────────────────────────────────┐
│  upload_reference_image()                                       │
│  ─────────────────────────────────────────────────────────────  │
│  POST /v1/uploads/images                                         │
│  (multipart/form-data, 携带 reference 图片)                      │
│                        │                                         │
│                        ▼                                         │
│                   返回 image_url                                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  create_image_generation_task()                                 │
│  ─────────────────────────────────────────────────────────────  │
│  POST /v1/images/generations                                    │
│  payload: {                                                     │
│    model: "gpt-image-2",                                        │
│    prompt: final_prompt,                                        │
│    image_urls: [image_url],  ← 参考图 URL                        │
│    size: aspect,                                                │
│    resolution: "1k",                                            │
│    n: 1                                                         │
│  }                                                              │
│                        │                                         │
│                        ▼                                         │
│                   返回 task_id                                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  wait_for_task_result() — 轮询                                   │
│  ─────────────────────────────────────────────────────────────  │
│  GET /v1/tasks/{task_id}  (轮询间隔 5s, 超时 300s)               │
│                        │                                         │
│                        ▼                                         │
│              status: completed ?                                 │
│                ├─ Yes → 提取 result_url                          │
│                ├─ failed → 抛出异常                              │
│                └─ pending/processing → 继续轮询                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  下载图片到 OUTPUT_DIR                                           │
│  GET result_url → 保存为 {timestamp}_{prompt[:20]}.png          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 交互式入口（interactive_run.py）— 两阶段

```
阶段1: prepare()
─────────────────
用户: "帮我做张海报"
            │
            ▼
get_selection_text(task, brief)
            │
            ▼
案例库有案例 ?
  ├─ Yes → 返回格式化列表 + 选项说明
  │         Hermes 展示给用户，等待回复
  │
  └─ No  → "案例库暂无相关案例，直接生成"
            Hermes 询问"确认生成请回复 y"


阶段2: execute()
─────────────────
用户回复: choice
            │
            ▼
判断 choice 类型
  │
  ├─ "y"/"yes"/"是" → run(user_input, use_reference=False)
  │
  ├─ "n"/"no"/"否"  → run(user_input, use_reference=False)
  │
  └─ 其他（案例编号）
      │
      ▼
   parse_user_choice(choice, task)
      │
      ▼
   找到 case_id ?
      ├─ Yes → run(user_input, use_reference=True, case_id=case_id)
      └─ No  → run(user_input, use_reference=False)
```

---

## 批量生成（batch_generator_v2.py）

```
BatchGeneratorV2
     │
     ├── batch_styles(brief)        ─→ 3次 run()，direction 不同
     │     directions: [conservative, balanced, bold]
     │
     ├── batch_aspects(brief)       ─→ N次 run()，aspect 不同
     │     aspects: [1:1, 16:9, 9:16] (默认)
     │
     └── batch_briefs(briefs)       ─→ N次 run()，brief 不同
           briefs: [brief1, brief2, ...]
```

每次 `run()` 都是完整的 5 阶段工作流，独立执行。

---

## 设计编译器 (design_compiler.py) — Prompt 构建逻辑

```
compile_prompt_package(brief, task, direction, aspect, quality)
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  make_design_reasoning()                                        │
│  ─────────────────────────────────────────────────────────────  │
│  合并多层配置:                                                   │
│                                                                  │
│  TASK_PROFILES[task]           ← 任务基础配置                    │
│    + DIRECTION_PROFILES[dir]   ← 风格强度配置                   │
│    + GLOBAL_DIRECTIVES         ← 全局反作弊规则                  │
│                                                                  │
│  输出: design_reasoning (dict, 20+ 字段)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  compile_design_brief()                                        │
│  ─────────────────────────────────────────────────────────────  │
│  把 design_reasoning 压缩为简短描述                               │
│  输出: compiled_brief (dict)                                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  build_prompt()                                                │
│  ─────────────────────────────────────────────────────────────  │
│  把 compiled_brief 拼接成自然语言 Prompt                         │
│  最终返回: "Create a {task} image for {channel}..."            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                       final_prompt
```

---

## 案例库结构 (case_library.py)

```
case_library/
├── poster/
│   ├── case_001_xxx/
│   │   ├── image.png          ← 生成图片
│   │   └── metadata.json       ← 元数据
│   ├── case_002_xxx/
│   │   ├── image.png
│   │   └── metadata.json
│   └── ...
├── product/
├── ppt/
├── infographic/
└── teaching/

metadata.json 内容:
{
  "case_id": "case_001",
  "task": "poster",
  "created_at": "2026-04-28T...",
  "image_path": "case_library/poster/case_001_xxx/image.png",
  "brief": "AI训练营海报",
  "prompt": "Create a poster image...",
  "params": { "task": "poster", "direction": "bold", ... },
  "tags": [],
  "rating": 5
}
```

---

## 路径解析（project_paths.py）

```
resolve_project_path(path)
    │
    ├── path 是绝对路径 → Path(path).resolve()
    │
    └── path 是相对路径 → (PROJECT_ROOT / path).resolve()


to_project_relative(path)
    │
    └── path 在 PROJECT_ROOT 下 → 返回相对路径
       否则 → 返回原字符串
```

---

## 垂直行业工作流（verticals/nail — 小红书美甲图文）

`verticals/nail/` 是独立于通用图片工作流的**垂直行业适配层**，面向小红书美甲图文场景。它有自己专属的：

- **Style 体系**（款式配置）
- **DNA 提取**（参考图视觉特征分析）
- **Prompt 构建**（图文场景专用）
- **文案生成**（小红书风格文案）

通过 `MultiAgentImageRunner` 适配器桥接到通用 `orchestrator_v2.run()`。

### 核心类：NailWorkflow

```python
class NailWorkflow:
    def __init__(self, llm_client=None, multimodal_client=None, image_runner=None):
        # llm_client        → 生成文案（LLM）
        # multimodal_client → 提取参考图 DNA（多模态模型）
        # image_runner      → 实际生成图片（桥接到 orchestrator_v2）

    def prepare(user_input: UserInput):
        # 返回: { style, dna, bundle, preview }

    def generate_image(prepared_result):
        # 调用 image_runner.generate() 执行生成
```

---

### NailWorkflow.prepare() 完整流程

```
UserInput(brief, style_id, reference_image_path, ...)
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│  ① match_style(user_input) — 款式匹配                            │
│  ─────────────────────────────────────────────────────────────  │
│  输入: UserInput                                                  │
│  处理:                                                            │
│    • style_id 明确指定 → 直接返回对应 NailStyle                  │
│    • 否则按关键词规则匹配:                                         │
│                                                                  │
│      关键词 → style_id                                           │
│      "合集"、"6款" → collection_cover_6_grid_whitening          │
│      "教程"、"DIY" → tutorial_diy_step_by_step                   │
│      "避雷"、"翻车" → warning_before_after_nail_fail            │
│      "对比"、"测评" → comparison_color_skin_tone_test            │
│      "约会"、"旅行" → story_mood_date_travel_nail               │
│      "爆款"、"跟款" → trend_fast_follow_from_viral              │
│                                                                  │
│  输出: NailStyle (from verticals/nail/styles/*.json)           │
│                                                                  │
│  NailStyle 包含:                                                  │
│    • visual: composition, hand_model, nail_shape, color_palette,  │
│              finish, decorations, background, lighting, text_policy │
│    • image_prompt: positive_constraints, must_show, avoid, ...    │
│    • copywriting: title_formula, opening_angle, body_structure,   │
│                   comment_hooks, cta                            │
│    • reference_policy: dna_fields_to_use, must_preserve,          │
│                        allow_variation, inherit_strength        │
│    • task, direction, aspect                                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  ② extract_dna_from_model() — 参考图 DNA 提取（可选）             │
│  ─────────────────────────────────────────────────────────────  │
│  判断: user_input.reference_image_path ?                         │
│    ├─ 有 → 调用 multimodal_client.analyze_image()                │
│    │        输入: DNA_EXTRACTION_PROMPT (14 字段提取)            │
│    │        输出: ReferenceDNA                                    │
│    │          - subject, hand_model, nail_shape, nail_length  │
│    │          - dominant_colors, finish_types, decorations      │
│    │          - composition, background, lighting, mood         │
│    │          - title_area_hint, main_visual_identity          │
│    └─ 无 → dna = None                                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  ③ build_image_prompt() — 图文封面 Prompt 构建                   │
│  ─────────────────────────────────────────────────────────────  │
│  输入: user_input, style, dna                                    │
│  输出: image_prompt (str)                                        │
│                                                                  │
│  Prompt 组成片段:                                                 │
│    [场景描述] "你正在为小红书美甲图文笔记生成封面图..."           │
│    [用户需求] brief + 肤色/甲长/甲型/颜色偏好/避忌元素           │
│    [Style视觉] 构图、甲型、甲长、色系、质感、装饰、背景、光线    │
│    [参考图DNA] ← 有 dna 时注入:                                  │
│                  subject/hand_model/nail_shape/nail_length     │
│                  dominant_colors/finish_types/decorations      │
│                  composition/background/lighting                │
│                  main_visual_identity                           │
│                  reference_policy 中的 must_preserve/allow_var  │
│    [约束条件] positive_constraints, must_show, avoid            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  ④ generate_copy() — 小红书文案生成                              │
│  ─────────────────────────────────────────────────────────────  │
│  输入: llm_client, user_input, style, dna                       │
│  输出: { titles:[3], bodies:[3], tags:[3组] }                   │
│                                                                  │
│  Prompt 片段:                                                    │
│    "请为一篇小红书美甲图文笔记生成爆款文案。                     │
│     要求像真实小红书用户发布，不要像硬广。"                       │
│    + style.copywriting (title_formula, opening_angle, ...)     │
│    + dna.main_visual_identity / dominant_colors / ...          │
│                                                                  │
│  无 llm_client 时 → fallback_copy() 返回预设文案                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  ⑤ build_preview() — 预览数据打包                                │
│  ─────────────────────────────────────────────────────────────  │
│  输出: PreviewPayload                                            │
│    cover_prompt: image_prompt                                     │
│    titles, bodies, tags: 文案候选                               │
│    selected_style: style.style_name                              │
│    dna_summary: dna 各字段（用于后续传给 orchestrator）         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                   prepare() 返回
                   { style, dna, bundle, preview }
```

---

### NailWorkflow.generate_image() — 桥接到通用工作流

```
prepared_result = prepare() 的结果
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│  MultiAgentImageRunner.generate()                               │
│  ─────────────────────────────────────────────────────────────  │
│  内部调用: orchestrator_v2.run(                                  │
│    bundle.image_prompt,            ← 已编译好的 nail 专用 prompt  │
│    task=style.task,                                             │
│    direction=style.direction,                                    │
│    aspect=style.aspect,                                          │
│    precompiled_brief=True,        ← 跳过 prompt_engineer 阶段    │
│    dna_summary=dna_summary,      ← 传入 DNA 摘要               │
│  )                                                              │
│                                                                  │
│  返回格式:                                                       │
│  { ok, result: orchestrator_v2.run()返回, requested_params }   │
└─────────────────────────────────────────────────────────────────┘
```

**关键：NailWorkflow 自己构建完整的 image_prompt，通过 `precompiled_brief=True` 跳过通用 orchestrator 的 Step 1（Prompt 工程师），直接进入 Step 2（风格研究员），实现垂直行业的 Prompt 定制。**

---

### 款式注册表（style_registry.py）

```
verticals/nail/styles/*.json   ← 7 种款式配置

款式 ID                     │ style_name
────────────────────────────┼──────────────────────────────
collection_cover_6_grid_     │ 合集封面（6宫格美白）
  whitening
tutorial_diy_step_by_step    │ 教程/DIY 步骤图
warning_before_after_nail_   │ 避雷/翻车前后对比
  fail
comparison_color_skin_tone_  │ 对比/测评/显白测试
  test
story_mood_date_travel_nail  │ 故事/氛围/约会/旅行
trend_fast_follow_from_viral  │ 爆款/同款/跟款/趋势复刻
single_seed_summer_cat_eye_  │ 夏日单款猫眼短甲（默认 fallback）
  short

每种款式 JSON 包含:
  - visual: 构图/手部/甲型/甲长/色系/质感/装饰/背景/光线
  - image_prompt: 正负约束条件
  - copywriting: 标题公式/开头角度/正文结构/评论钩子/CTA
  - reference_policy: DNA字段策略
```

---

### 整体入口关系图

```
verticals/nail/
│
├── NailWorkflow           ──── 行业工作流编排层
│     │                        (prepare + generate_image)
│     ├── style_matcher.py   ──── 款式匹配（7 种款式）
│     ├── dna_extractor.py   ──── 参考图 DNA 提取（多模态）
│     ├── prompt_builder.py  ──── nail 专用 Prompt 构建
│     ├── copy_generator.py  ──── 小红书文案生成（LLM）
│     ├── preview_builder.py  ──── 预览数据打包
│     │
│     └── image_runner_adapter.py
│           MultiAgentImageRunner ──── 桥接器 → orchestrator_v2.run()
│
└── styles/*.json          ──── 7 种款式配置（垂直知识库）

调用链（完整）:
  NailWorkflow.prepare()
    → match_style()              → NailStyle
    → extract_dna_from_model()   → ReferenceDNA (可选)
    → build_image_prompt()      → image_prompt (str)
    → generate_copy()            → { titles, bodies, tags }
    → build_preview()            → PreviewPayload

  NailWorkflow.generate_image(prepared_result)
    → MultiAgentImageRunner.generate()
      → orchestrator_v2.run(precompiled_brief=True, dna_summary=...)
        → Step2 风格研究员
        → Step3 图片生成（文生图 or 图生图）
        → Step4 QA
        → Step5 归档
        → auto_save_to_library()
```
