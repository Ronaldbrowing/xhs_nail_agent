
# **Vertical Content Studio MVP v1.0 产品需求、技术方案与验收基准**

## **文档定位**

本文档定义的是一个面向小红书图文笔记生产的多垂类内容生成工作台。系统的长期目标不是只服务于单一美甲场景，而是支持多个行业细分赛道的内容生产、历史回放、案例复用和资产管理。

在 MVP v1.0 阶段，系统采用：

```text
通用平台底座 + nail 美甲首个垂类落地
```

的范围策略。

也就是说，v1.0 不要求同时完成多个真实行业垂类的生产质量验证，但必须在产品架构、数据模型、API 合约、前端页面、历史记录、案例库和验收标准中保留 `vertical` 垂类维度，确保未来可以扩展到穿搭、家居、宠物、母婴、探店、健身、美食、旅行等更多细分赛道，而不需要重写整个系统。

本文档的目标不是“描述想法”，而是成为后面推进项目的：

```text
唯一需求输入
唯一范围边界
唯一技术路线依据
唯一测试基准
唯一验收依据
```

所有开发任务、测试用例、验收结论必须与本文档逐项对应。未在本文档定义的功能，不纳入 MVP v1.0 验收范围。如需新增或修改需求，必须通过变更记录追加，不得在开发过程中口头变更。

---

## **文档核心调整说明**

相较于原始 `Nail Web Studio MVP v1.0` 文档，本版做了以下关键调整。

第一，产品名称从 `Nail Web Studio` 调整为 `Vertical Content Studio`。原因是美甲只是首个行业场景，不应成为产品本体。产品本体应该是面向多个垂类的小红书图文内容生成工作台。

第二，所有核心能力从“美甲专用能力”调整为“通用平台能力”。生成工作台、任务进度、内容预览、历史记录、案例库、参考来源、静态资源访问、测试验收等模块，都必须支持 `vertical` 字段。

第三，v1.0 的真实落地范围仍然保持克制。v1.0 不要求一次性完成多个行业，但要求 nail 美甲作为首个垂类完整跑通，并且平台底座不能写死 nail。

第四，API 和数据模型从 `/api/nail/...` 的单垂类表达，升级为推荐使用 `/api/verticals/{vertical}/...` 的通用表达。现有 `/api/nail/...` 可以作为兼容层保留，但不再作为新开发和新文档的主接口。

第五，验收标准从“nail 功能验收”升级为“两层验收”：平台级验收和垂类级验收。平台级验收检查系统是否真的具备多垂类扩展能力；垂类级验收检查 nail 作为首个落地垂类是否端到端可用。

---

## **本文档需要解决的核心问题**

当前项目遇到的问题，本质上不是某个功能没做，而是“需求基准没有被工程化”和“产品抽象层级过低”。

之前的原始设想更多是围绕一个可视化 Web MVP 展开，后来开发过程中又切到了 P0-P3 的工程修复语境，导致最后形成了一个“工程可用但产品不完整”的版本。进一步看，当前版本还存在另一个更深层的问题：它把 nail 美甲场景当成了产品本体，而不是把 nail 作为第一个可插拔垂类。

因此，本文档需要明确回答以下问题：

```text
我们到底要做一个什么产品？
它是美甲工具，还是多垂类内容生产平台？
v1.0 到底做通用底座，还是只做 nail？
哪些能力必须通用化？
哪些能力可以先只在 nail 中落地？
页面应该如何体现 vertical？
后端 API 应该如何表达 vertical？
历史记录和案例库如何按 vertical 隔离？
新增一个 vertical 需要改哪些地方？
每个功能怎么测试？
做到什么程度才算完成？
中途新增或修改需求怎么处理？
每个阶段怎么检查有没有跑偏？
```

如果这些问题写不清楚，后续开发仍然可能出现以下问题：

```text
工程师做了 nail 接口，但未来无法扩展 outfit、pet、home；
做了 localStorage 历史，但没有服务端历史；
做了 case_id 参数，但没有案例库 UI；
做了 nail case，但没有 vertical 隔离；
做了进度轮询，但没有任务详情；
做了功能，但验收时不知道算不算完成；
写了新的行业，却复制了一整套 API 和页面。
```

因此，下一步必须先做“需求冻结与验收基线”，而不是继续直接改代码。

---

## **文档整体结构**

本文档分为 13 个部分。相比原文档，新增了第 0 章“核心术语与抽象层”，用于明确平台、内容形态、垂类、场景、工作流、案例、笔记、参考来源之间的关系。

```text
0. 核心术语与抽象层
1. 项目背景与目标
2. 当前实现状态与差距
3. 产品定位与用户场景
4. MVP v1.0 范围定义
5. 信息架构与页面结构
6. 核心用户流程
7. 功能需求明细
8. 数据模型与 API 合约
9. 技术路线与实现方案
10. 实施步骤与里程碑
11. 测试方案
12. 验收标准与防跑偏机制
```

这 13 个部分共同构成 MVP v1.0 的完整需求、技术、测试和验收基准。

---

# **0. 核心术语与抽象层**

## **0.1 产品名称**

本系统在 MVP v1.0 中统一命名为：

```text
Vertical Content Studio
```

中文名称可以使用：

```text
多垂类小红书图文内容生成工作台
```

其中：

```text
Vertical = 行业细分垂类
Content = 内容资产
Studio = 可视化生产工作台
```

系统不再命名为 `Nail Web Studio`，因为 nail 美甲只是第一个落地垂类，不是平台本体。

---

## **0.2 内容平台 content_platform**

`content_platform` 表示内容最终面向的发布平台。

MVP v1.0 固定支持：

```text
xhs
```

即小红书。

未来可扩展到：

```text
douyin
wechat
bilibili
kuaishou
```

但这些不纳入 MVP v1.0 的实现和验收范围。

v1.0 中所有 note、case、job、history item、package 都应保留 `content_platform` 字段，默认值为：

```json
"xhs"
```

这样做的原因是，虽然当前只做小红书图文笔记，但未来如果扩展到其他平台，内容结构、标题风格、标签策略、图片比例、文案语气都有可能变化。提前保留 `content_platform` 字段，可以避免后续大规模重构。

---

## **0.3 内容形态 content_type**

`content_type` 表示生成内容的类型。

MVP v1.0 固定支持：

```text
image_text_note
```

即小红书图文笔记。

未来可扩展到：

```text
short_video_script
carousel_post
product_note
live_script
comment_reply
```

但这些不纳入 MVP v1.0 的实现和验收范围。

v1.0 的所有生成结果都应围绕图文笔记展开，核心输出包括：

```text
标题
正文
标签
多页内容结构
图片或图片引用
诊断信息
历史 package
```

---

## **0.4 垂类 vertical**

`vertical` 表示行业细分赛道，是本系统最重要的扩展维度。

MVP v1.0 首个真实落地垂类为：

```text
nail
```

即美甲。

未来可扩展到：

```text
outfit
home
pet
food
travel
fitness
mom_baby
beauty
skincare
local_shop
wedding
education
```

但 MVP v1.0 不要求完成这些垂类的真实生产质量验证。v1.0 的要求是：系统架构、API、数据模型、前端状态、历史记录、案例库和验收标准必须支持未来新增这些 vertical。

也就是说：

```text
v1.0 真实可用垂类：nail
v1.0 必须具备的能力：多垂类扩展能力
```

所有 job、note、case、history item、package 都必须包含或能够推导出 `vertical` 字段。

---

## **0.5 场景 scenario**

`scenario` 表示某个 vertical 下更细的内容场景。

例如，在 `nail` 垂类下，可以有：

```text
summer_cat_eye
short_nail
wedding_nail
commuter_nail
french_nail
christmas_nail
new_year_nail
```

在未来的 `outfit` 垂类下，可以有：

```text
commute_outfit
date_outfit
vacation_outfit
winter_outfit
minimal_outfit
```

在未来的 `pet` 垂类下，可以有：

```text
cat_daily
dog_training
pet_product_review
pet_health
```

MVP v1.0 中，`scenario` 可以作为可选字段，不强制要求前端提供完整场景选择器。但数据模型和接口应允许传入 `scenario`，并允许 note_package.json 中记录该字段。

如果用户没有选择 `scenario`，系统可以将其设为：

```json
null
```

或：

```json
"general"
```

具体采用哪种方式由后端 schema 统一定义。

---

## **0.6 工作流 workflow**

`workflow` 表示某个 vertical/scenario 对应的生成流程。

不同垂类可能共享相同的通用流程，也可能有自己的垂类适配逻辑。例如：

```text
nail_note_workflow_v1
outfit_note_workflow_v1
pet_note_workflow_v1
```

MVP v1.0 中，真实可执行的 workflow 可以仍然是 nail 相关工作流，但平台层不应写死为 `NailNoteWorkflow`。更合理的方式是通过 `vertical registry` 或 `vertical adapter` 查找对应 workflow。

目标结构是：

```text
用户选择 vertical
        ↓
平台 API 接收任务
        ↓
Vertical Registry 查找垂类配置
        ↓
Vertical Adapter 调用对应 workflow
        ↓
生成 note_package
        ↓
统一历史、预览、案例逻辑处理
```

这样做的原因是，新增一个垂类时，不应该复制一整套 Web 页面、API 路由和历史系统，而应该只新增垂类配置、垂类适配器、垂类案例和必要的 workflow 实现。

---

## **0.7 案例 case**

`case` 表示可复用的优质内容资产。

一个 case 可以来自：

```text
历史生成结果
人工整理的优质样例
外部导入的内容结构
垂类专家沉淀的模板
```

每个 case 必须归属于某个 `vertical`，可选归属于某个 `scenario`。

例如：

```json
{
  "case_id": "case_nail_summer_cat_eye_001",
  "vertical": "nail",
  "scenario": "summer_cat_eye"
}
```

案例库必须按 vertical 隔离。`nail` 的 case 不能直接用于 `outfit` 的生成任务；`outfit` 的 case 也不能直接用于 `pet` 的生成任务。

如果用户在创建任务时传入 `case_id`，后端必须校验：

```text
case.vertical == request.vertical
```

如果不匹配，应返回 4xx 错误，而不是静默使用或自动 fallback。

---

## **0.8 笔记 note**

`note` 表示一次生成得到的完整小红书图文笔记结果。

一个 note 至少应该包含：

```text
note_id
content_platform
content_type
vertical
scenario
brief
selected_title
caption/body
tags
pages
image_urls
diagnostics
created_at
status
```

MVP v1.0 中，note 的主要落地形式是：

```text
note_package.json
```

历史记录、预览回放、案例复用都应围绕 note_package 展开。

为了支持多垂类，note_package 中必须写入：

```json
{
  "content_platform": "xhs",
  "content_type": "image_text_note",
  "vertical": "nail"
}
```

如果是旧数据，package 中暂时没有这些字段，历史扫描服务可以进行 fallback 推断，但必须在返回结果中标记为：

```text
inferred
```

或：

```text
unknown
```

不能因为旧数据字段缺失导致历史接口整体失败。

---

## **0.9 参考来源 reference_source**

`reference_source` 表示生成任务使用的参考资料来源。

该字段是通用平台字段，不属于 nail 特有字段。

MVP v1.0 支持三种取值：

```text
none
local_path
case_id
```

含义如下：

```text
none：不使用参考资料。
local_path：使用用户上传的本地参考图片。
case_id：使用当前 vertical 下的案例作为参考。
```

未来可扩展到：

```text
history_note
url
brand_asset
knowledge_base
manual_brief
```

但这些不纳入 MVP v1.0 的实现范围。

MVP v1.0 中，三种 reference_source 必须在 UI 和 API 中显式表达，并且互斥：

```text
reference_source=none 时，不得传 reference_image_path 和 case_id。
reference_source=local_path 时，必须传 reference_image_path，不得传 case_id。
reference_source=case_id 时，必须传 case_id，不得传 reference_image_path。
```

---

## **0.10 Vertical Registry**

`Vertical Registry` 是系统用于管理可用垂类的配置或服务。

MVP v1.0 至少要注册：

```json
{
  "vertical": "nail",
  "display_name": "美甲",
  "enabled": true,
  "content_platforms": ["xhs"],
  "content_types": ["image_text_note"],
  "supported_reference_sources": ["none", "local_path", "case_id"],
  "default_page_count": 6,
  "workflow_id": "nail_note_workflow_v1",
  "case_enabled": true,
  "reference_image_enabled": true
}
```

未来新增垂类时，应通过新增 registry 配置和 adapter 实现，而不是复制整套 API 和前端页面。

---

# **1. 项目背景与目标**

## **1.1 项目背景**

当前系统已经在 nail 美甲场景中验证了小红书图文笔记生成的基础能力，包括内容生成、图片生成、参考图输入、case_id 参数、任务轮询、结果 package 保存等能力。

但是，现有 Web MVP 实现仍主要围绕单一 nail 场景展开，产品形态更接近一个内部调试型单页工作台，而不是一个可扩展的多垂类内容生产平台。

从产品层面看，当前实现存在以下问题：

```text
页面结构偏单一，历史记录、案例库、任务详情没有产品化展开；
历史回放依赖 localStorage，不是真正的服务端历史；
case_id 只是参数入口，不是案例库产品能力；
任务进度缺少 stage、耗时、错误阶段等可观察信息；
内容预览还没有完全变成可直接生产使用的内容面板；
验收方式偏代码测试，缺少产品级验收矩阵。
```

从架构层面看，当前实现还存在更深层的问题：

```text
产品命名绑定 nail；
API 路径绑定 nail；
数据模型缺少 vertical 字段；
历史记录没有按 vertical 过滤；
案例库没有按 vertical 隔离；
前端文案和状态容易写死为美甲；
新增其他行业时可能需要复制整套页面和接口。
```

因此，MVP v1.0 的目标不是继续在当前 nail 页面上做零散修补，而是重新定义一个可验收、可扩展、可持续迭代的多垂类内容生成工作台。

---

## **1.2 产品目标**

Vertical Content Studio MVP v1.0 的目标是建立一个面向小红书图文笔记生产的多垂类内容生成工作台。

它不是一个单纯的接口调用页面，也不是一个只服务美甲的垂类工具，而是一个可扩展的平台型工作台。

MVP v1.0 的核心策略是：

```text
通用平台底座先成型；
nail 美甲作为首个垂类端到端落地；
后续垂类通过 registry + adapter + cases + workflow 扩展。
```

该工作台需要支持以下核心目标：

1. 用户可以选择或查看当前目标垂类 `vertical`，并基于该垂类创建小红书图文笔记生成任务。

2. 用户可以在指定垂类下输入内容需求 `brief`，并选择生成模式。

3. 用户可以选择无参考、上传参考图、复用案例三种生成模式。

4. 用户可以观察长任务生成进度，理解任务当前阶段、执行状态、耗时和失败原因。

5. 用户可以查看完整生成结果，包括标题、正文、标签、多页图文结构、图片和诊断信息。

6. 用户可以从历史记录中找回过去生成的内容，并且历史记录必须支持按 vertical 过滤，不依赖浏览器本地缓存。

7. 用户可以浏览当前 vertical 下的案例库，并选择案例用于下一次生成。

8. 系统必须支持以 nail 作为首个 vertical 完成端到端验收。

9. 系统的核心模型、API、前端模块、测试方案和验收标准必须保留 vertical 维度，确保未来可以增加新的行业细分赛道。

10. 所有核心链路必须具备可测试、可恢复、可验收的明确标准。

---

## **1.3 v1.0 的产品边界**

MVP v1.0 不追求一次性完成所有行业，不追求复杂账号系统，也不追求完整 CMS 能力。

v1.0 的边界是：

```text
做通用底座；
做 nail 首个垂类；
做历史回放；
做案例复用；
做任务进度；
做内容预览；
做垂类扩展点；
做测试和验收闭环。
```

v1.0 不做：

```text
多用户账号体系；
云端权限管理；
自动发布到小红书；
复杂内容 CMS；
复杂图片编辑器；
多个真实垂类的全面内容质量验证；
大规模数据库化改造，除非 output 扫描无法满足历史回放需求。
```

这意味着，v1.0 的成功标准不是“所有行业都能生成高质量内容”，而是：

```text
平台抽象正确；
nail 链路完整；
未来新增 vertical 不需要重写系统。
```

---

## **1.4 产品定位**

Vertical Content Studio 是一个内容生产工作台，而不是接口调试台。

它面向的主要用户是：

```text
内容生产者
内容运营者
垂类内容策划者
项目开发者本人
后续行业垂类扩展者
```

用户不是只运行一次脚本的人，而是需要反复生产、查看、复用、管理和迭代内容的人。

因此，系统必须围绕真实内容生产流程组织：

```text
选择垂类
创建任务
选择参考来源
观察进度
查看结果
复制内容
查看图片
回放历史
复用案例
沉淀资产
扩展新垂类
```

而不是只围绕后端接口组织。

---

## **1.5 关键产品原则**

MVP v1.0 必须遵守以下产品原则。

第一，平台能力与垂类能力分离。

生成工作台、任务进度、历史记录、案例库、内容预览、静态资源访问、测试验收属于平台能力。nail prompt、nail workflow、nail case、nail 风格标签属于垂类能力。平台能力不得写死 nail。

第二，v1.0 只真实验收一个垂类，但架构不能只支持一个垂类。

nail 是首个 vertical，不是唯一 vertical。所有数据模型、API、历史记录、案例库和 package 都必须包含或支持 vertical。

第三，API 存在不等于功能完成。

如果后端有 `/api/verticals/nail/cases`，但前端没有案例库入口，不算案例库完成。如果后端有历史 package 接口，但前端无法浏览历史，不算历史记录完成。

第四，localStorage 恢复不等于服务端历史。

localStorage 可以作为最近任务快捷入口，但不能作为 v1.0 历史记录的唯一来源。历史记录必须来自服务端 output 扫描或持久化存储。

第五，case_id 参数存在不等于案例库完成。

v1.0 必须有前端案例库入口，用户可以浏览当前 vertical 下的案例，并选择案例用于生成任务。

第六，JSON 可读不等于内容预览完成。

内容预览必须以用户可使用的方式展示标题、正文、标签、多页内容、图片和诊断信息，而不是只显示原始 JSON。

第七，测试通过不等于产品验收通过。

自动化测试是必要条件，但最终验收必须结合功能验收矩阵、页面验收、手动用户流程和范围偏差检查。

---

## **1.6 v1.0 成功标准**

MVP v1.0 只有同时满足以下条件，才算成功：

1. 通用平台层具备 vertical 概念。

2. `GET /api/verticals` 或等价能力可以返回可用垂类列表，至少包含 nail。

3. 创建任务、历史记录、案例库、package 回放都绑定 vertical。

4. note_package.json 中写入 `content_platform`、`content_type`、`vertical`。

5. nail 垂类可以完成基础生成、参考图生成、案例复用、任务进度、结果预览、历史回放的端到端链路。

6. 历史记录不依赖 localStorage，清空浏览器缓存后仍可从服务端恢复。

7. 案例库不是隐藏参数输入，而是有前端可见入口和选择动作。

8. 后端不允许未知 vertical 静默 fallback 到 nail。

9. 前端页面不应把所有产品文案、状态和数据结构写死为美甲。

10. 所有 Must Have 功能都有对应测试和验收项。

11. 每个 Milestone 完成后都有验收报告，记录 commit、测试结果、手动验收结果和范围偏差检查。

---
# **2. 当前实现状态与差距**

## **2.1 当前版本判断**

当前版本可以定义为：

```text
Web MVP v0 内部验证版
```

它已经证明了部分底层工程链路可行，包括：

```text
前端可以提交生成任务；
后端可以创建 job；
前端可以轮询任务状态；
任务成功后可以展示生成结果；
可以上传参考图；
可以传入 case_id；
可以通过静态路径访问 output/input 资源；
可以通过 note_id fallback 恢复部分历史结果；
可以使用 localStorage 保存最近任务。
```

这些能力说明，系统已经具备从脚本/接口走向 Web 工作台的基础。

但是，当前版本尚未达到 MVP v1.0 的产品标准，也尚未达到多垂类平台的架构标准。

从产品层面看，当前实现更接近：

```text
单垂类内部调试型生成页面
```

而不是：

```text
多垂类小红书图文内容生产工作台
```

从架构层面看，当前实现仍然明显绑定 nail 美甲场景，缺少 `vertical` 抽象。这会导致未来新增其他行业赛道时，开发容易走向复制接口、复制页面、复制数据模型的不可维护路径。

因此，MVP v1.0 的目标不是简单继续修补当前页面，而是以当前 v0 为工程基础，补齐产品闭环，并将系统抽象升级为：

```text
通用平台底座 + 垂类适配器 + nail 首个垂类落地
```

---

## **2.2 当前实现的已完成能力**

当前 v0 已完成的能力应被保留，并作为 v1.0 的工程基础继续演进。

| 能力 | 当前状态 | v1.0 处理方式 |
|---|---|---|
| Web 页面入口 | 已有本地 Web 页面 | 保留，但升级为通用 Studio 页面 |
| 生成任务提交 | 已支持提交任务 | 保留，并加入 vertical/reference_source 显式建模 |
| 任务轮询 | 已支持根据 job_id 查询状态 | 保留，并增强 stage、耗时、错误信息 |
| 结果预览 | 已支持展示部分生成结果 | 保留，并升级为完整内容预览模块 |
| 参考图上传 | 已有参考图上传链路 | 保留，并改为当前 vertical 下的 reference asset |
| case_id 参数 | 已支持传入 case_id | 保留，但必须升级为案例库选择能力 |
| 静态资源访问 | 已支持 output/input 静态映射 | 保留，并支持按 vertical 组织或识别 |
| 最近任务 | 已支持 localStorage 最近任务 | 保留为快捷入口，但不能作为历史记录主来源 |
| job 404 fallback | 已支持部分 package fallback | 保留，并纳入历史回放策略 |
| API 测试 | 已有基础 API 测试 | 保留，并扩展为平台级 + nail 垂类级测试 |

这些能力不应被推倒重来。v1.0 的重点是：

```text
把已有工程能力产品化；
把单垂类能力通用化；
把隐藏参数能力前端可视化；
把临时恢复能力升级为服务端历史；
把代码测试升级为产品验收。
```

---

## **2.3 当前产品形态差距**

当前 v0 与 MVP v1.0 的产品形态存在明显差距。

| 模块 | v1.0 目标 | 当前状态 | 差距判断 |
|---|---|---|---|
| 生成工作台 | 支持 vertical、brief、生成模式、参考来源、参数提交 | 已有单页输入区 | 部分完成，但缺少 vertical 与模式产品化 |
| 任务进度 | 展示 status、stage、current step、耗时、错误阶段 | 只有简化 Progress 面板 | 明显简化 |
| 内容预览 | 展示标题、正文、标签、多页结构、图片、复制、诊断 | 有基础预览 | 部分完成，生产可用性不足 |
| 历史记录 | 服务端历史列表与 package 回放 | localStorage 最近任务 + fallback | 明显不足 |
| 案例库 | 可浏览、搜索、选择案例并回填生成任务 | 无前端案例库 UI | 缺失 |
| 参考来源 | none/local_path/case_id 三模式明确互斥 | 参数层面部分支持 | 产品表达不足 |
| 错误处理 | 结构化错误、错误阶段、可恢复提示 | 部分错误展示 | 不完整 |
| 复制/复用 | 复制标题、正文、标签、单页内容，复用历史 | 部分或缺失 | 不完整 |
| 验收体系 | 功能、接口、页面、测试、手动流程逐项验收 | 以代码测试为主 | 不足 |

当前页面可以用于内部快速验证，但还不适合作为长期内容生产工作台。

尤其是历史记录和案例库这两项，当前更接近“后端/参数能力”，而不是“用户可见的产品能力”。

---

## **2.4 当前架构抽象差距**

除了产品功能缺口，当前版本还存在更重要的架构抽象问题：系统过度绑定 nail 垂类。

| 模块 | 当前状态 | 通用化问题 | v1.0 要求 |
|---|---|---|---|
| 产品命名 | Nail Web Studio / 美甲工作台 | 产品名绑定单一垂类 | 改为 Vertical Content Studio |
| 页面文案 | 小红书美甲图文 | UI 写死美甲场景 | 页面显示 content_platform、content_type、vertical |
| API 路径 | `/api/nail/...` | 路径绑定 nail | 推荐 `/api/verticals/{vertical}/...` |
| 数据模型 | 默认 nail note/case | 缺少 vertical 字段 | job、note、case、history、package 必须包含 vertical |
| 工作流入口 | NailNoteWorkflow | workflow 绑定 nail | 通过 vertical registry/adapter 查找 |
| 历史记录 | 面向 nail output | 无法跨垂类管理 | 历史记录必须按 vertical 过滤 |
| 案例库 | nail case 语义 | 无 vertical 隔离 | case 必须归属 vertical |
| 静态资源 | output 路径未必区分 vertical | 多垂类资产可能混杂 | 推荐 output/{vertical}/{note_id} |
| 测试文件 | test_nail_api | 测试只覆盖 nail | 增加平台级 vertical 测试 |
| 扩展方式 | 可能复制一套 nail 逻辑 | 后续不可维护 | 新垂类通过 registry + adapter 扩展 |

这类差距比单个功能缺失更重要。因为如果不在 v1.0 阶段修正抽象层，后续新增第二个、第三个垂类时，系统很容易变成多套重复实现：

```text
/api/nail/...
/api/outfit/...
/api/pet/...
/api/home/...
```

每个垂类都复制一套页面、路由、历史、案例、测试，最终难以维护。

MVP v1.0 必须避免这种方向。

---

## **2.5 历史记录差距**

历史记录是当前 v0 与 v1.0 差距最大的模块之一。

当前实现的历史能力主要是：

```text
localStorage 保存最近任务；
部分任务保存 job_id、note_id；
点击最近任务后尝试查询 job；
如果 job 不存在，尝试通过 note_id 读取 package；
```

这只能算“本机最近任务恢复”，不能算完整历史记录。

MVP v1.0 要求的历史记录必须是服务端能力，至少满足：

```text
不依赖浏览器 localStorage；
可以从服务端 output 或持久化存储读取历史 note；
可以按 vertical 过滤；
可以展示 note_id、created_at、brief、selected_title、status、reference_source、page_count、image_count、qa_score；
可以点击历史项打开 note_package；
可以处理损坏 package；
可以兼容旧 package；
不返回本地绝对路径；
不允许路径穿越。
```

对比来看：

| 历史能力 | 当前 v0 | v1.0 要求 |
|---|---|---|
| 历史来源 | localStorage 为主 | 服务端 output 或持久化存储 |
| 跨浏览器恢复 | 不支持 | 支持 |
| 清空缓存后恢复 | 不支持 | 支持 |
| 按 vertical 过滤 | 不支持 | 必须支持 |
| 历史列表 UI | 无完整 UI | 必须有 |
| 点击打开 package | 部分支持 | 必须稳定支持 |
| 损坏 package 处理 | 不完整 | 跳过或 diagnostics，不得 500 |
| 旧数据兼容 | 不完整 | 允许 fallback/inferred |
| 路径安全 | 需继续验证 | 必须验收 |

因此，v1.0 中“历史记录”不能被 localStorage 最近任务替代。localStorage 可以保留，但只能作为快捷入口。

必须明确：

```text
localStorage 恢复不等于服务端历史。
```

---

## **2.6 案例库差距**

当前系统已有 `case_id` 参数能力，但这不等于案例库完成。

当前状态更接近：

```text
开发者知道 case_id，然后手动输入或通过参数传入。
```

MVP v1.0 要求的是：

```text
用户可以在前端看到当前 vertical 下的案例；
用户可以浏览、搜索或筛选案例；
用户可以点击“使用此案例”；
系统自动将 case_id 回填到生成工作台；
生成模式切换为 case_id；
提交任务时后端校验 case.vertical 与 request.vertical 一致。
```

对比来看：

| 案例能力 | 当前 v0 | v1.0 要求 |
|---|---|---|
| case_id 参数 | 已有 | 保留 |
| 案例列表接口 | 不完整或缺失 | 必须有 |
| 案例库 UI | 缺失 | 必须有 |
| 选择案例回填 | 缺失 | 必须有 |
| vertical 隔离 | 缺失 | 必须有 |
| 跨垂类 case 校验 | 缺失 | 必须有 |
| 案例预览图 | 不完整 | Should Have |
| 案例搜索 | 缺失 | Should Have |

因此，v1.0 不能把“支持 case_id 参数”当作“案例库完成”。

必须明确：

```text
case_id 参数存在不等于案例库完成。
```

---

## **2.7 任务进度差距**

当前 v0 已经有任务状态轮询，但进度表达仍然偏弱。

MVP v1.0 的任务进度不应只是显示：

```text
queued
running
succeeded
failed
```

还应尽可能展示：

```text
当前 stage；
当前进度说明；
已耗时；
错误代码；
错误信息；
错误阶段；
note_id；
是否可 fallback；
是否 partial_failed。
```

v1.0 推荐的 stage 包括：

```text
queued
planning
copywriting
image_generation
qa
saving
succeeded
failed
partial_failed
timeout
restored
```

如果后端暂时不能做到页面级实时进度，至少要在 job status 中提供阶段级信息，并在任务完成后从 package diagnostics 中展示 page_timings。

对比来看：

| 进度能力 | 当前 v0 | v1.0 要求 |
|---|---|---|
| job_id 展示 | 部分支持 | 必须支持 |
| status 展示 | 已支持 | 必须保留 |
| stage 展示 | 不完整 | 必须支持 |
| elapsed_seconds | 不完整 | 必须支持 |
| error_code | 不完整 | Should Have |
| error_stage | 不完整 | Should Have |
| page_timings | 不完整 | Should Have |
| failed/partial_failed UI | 部分支持 | 必须清晰表达 |
| job 404 fallback | 已有部分能力 | 必须纳入验收 |

任务进度的目标不是做复杂监控系统，而是让用户知道：

```text
任务有没有在跑？
现在跑到哪一步？
是不是失败了？
失败在哪里？
是否还能从 package 恢复？
```

---

## **2.8 内容预览差距**

当前 v0 已有内容预览，但还需要从“结果展示”升级为“内容生产面板”。

MVP v1.0 的内容预览至少应展示：

```text
note_id
content_platform
content_type
vertical
scenario
selected_title
caption/body
tags
pages
image_urls
qa_score
diagnostics.reference
diagnostics.timing
page_timings
```

并支持：

```text
复制标题；
复制正文；
复制标签；
复制单页内容；
打开图片；
图片缺失时显示缺失状态；
从历史 package 恢复预览；
partial_failed 时展示成功部分并标记失败部分。
```

必须明确：

```text
JSON 可读不等于内容预览完成。
```

用户需要的是可直接复制、查看、复用和发布前整理的内容，而不是只看到原始结构化数据。

---

## **2.9 多垂类扩展差距**

当前 v0 没有明确“新增一个垂类需要做什么”。

MVP v1.0 必须定义新增 vertical 的最小扩展步骤。未来新增一个垂类时，理想流程应该是：

```text
新增 vertical registry 配置；
新增 vertical adapter；
新增或绑定 workflow；
新增 case seed 数据；
新增垂类测试；
前端自动显示该 vertical；
历史记录按 vertical 生效；
案例库按 vertical 生效。
```

而不是：

```text
复制 nail API；
复制 nail 页面；
复制 nail history；
复制 nail cases；
复制 nail tests；
手动改一堆写死文案。
```

因此，v1.0 不要求完成多个真实行业，但必须提供清晰的扩展点。

---

## **2.10 当前差距结论**

当前版本不应被判定为完全失败，也不应被判定为完整 MVP v1.0。

更准确的判断是：

```text
Web MVP v0 内部验证版：基本成立。
Vertical Content Studio MVP v1.0：尚未完成。
```

当前 v0 已经完成了底层工程链路的可行性验证，但在以下方面仍需补齐：

```text
产品形态从单页调试台升级为内容生产工作台；
历史记录从 localStorage 升级为服务端历史；
case_id 从隐藏参数升级为案例库选择；
任务进度从状态灯升级为可观察进度；
内容预览从原始展示升级为可生产使用；
系统抽象从 nail 专用升级为 vertical 通用；
验收方式从代码测试升级为产品、接口、测试、手动流程全链路验收。
```

MVP v1.0 的核心任务是：

```text
保留 v0 已打通的工程能力；
修正 v0 的产品缺口；
修正 v0 的单垂类强绑定；
以 nail 为首个垂类完成通用平台闭环。
```

---

# **3. 产品定位与用户场景**

## **3.1 产品定位**

Vertical Content Studio 是一个面向小红书图文笔记生产的多垂类内容生成工作台。

它的长期目标不是成为单一美甲工具，而是成为一个可以支持多个行业细分赛道的内容生产平台。

MVP v1.0 的定位是：

```text
小红书图文笔记生产工作台
+ 多垂类扩展底座
+ nail 美甲首个落地垂类
```

它服务于需要持续生产、查看、复用和管理内容资产的用户，而不是只服务于一次性运行脚本或调试接口的开发场景。

系统应该围绕真实内容生产过程组织：

```text
选择垂类
输入内容需求
选择参考来源
创建生成任务
观察任务进度
查看生成结果
复制内容
打开图片
回放历史
复用案例
沉淀资产
扩展垂类
```

而不是只围绕接口调用组织。

---

## **3.2 目标用户**

MVP v1.0 的目标用户包括以下几类。

### **3.2.1 内容生产者**

内容生产者需要快速生成小红书图文笔记，包括标题、正文、标签、多页图文结构和图片素材。

他们关心的是：

```text
内容能不能直接用；
标题是否吸引人；
正文是否适合小红书语气；
标签是否合适；
图片是否能打开；
生成过的内容能不能找回；
好用的案例能不能复用。
```

对这类用户来说，API 是否存在并不重要，重要的是页面上是否能完成真实生产动作。

---

### **3.2.2 内容运营者**

内容运营者可能需要围绕不同垂类持续产出内容，例如：

```text
美甲
穿搭
家居
宠物
美食
探店
健身
母婴
```

他们关心的是：

```text
不同垂类能否分开管理；
历史内容能否按垂类查看；
优质案例能否沉淀；
不同垂类的生成风格是否可控；
内容资产是否能持续复用。
```

对这类用户来说，多垂类不是技术概念，而是日常内容运营的组织方式。

---

### **3.2.3 垂类内容策划者**

垂类内容策划者负责定义某个 vertical 的内容策略、风格、案例和模板。

例如，nail 垂类策划者可能关心：

```text
短甲、猫眼、法式、通勤、婚礼、美拉德等场景；
不同风格的标题模板；
不同图片风格的提示词；
不同季节和节日主题；
优质案例沉淀。
```

未来 outfit 垂类策划者可能关心：

```text
通勤穿搭、约会穿搭、旅行穿搭；
身材适配；
季节适配；
单品组合；
风格标签。
```

系统需要允许这些垂类策略通过 registry、adapter、case、workflow 等方式接入，而不是硬编码在平台层。

---

### **3.2.4 项目开发者**

项目开发者需要持续迭代系统，新增功能、修复问题、扩展垂类、验证链路。

他们关心的是：

```text
需求范围是否明确；
每个功能是否有 FR 编号；
每个接口是否有合约；
每个垂类如何接入；
测试怎么跑；
验收怎么做；
哪些是平台能力；
哪些是垂类能力。
```

对开发者来说，本文档必须成为唯一输入，否则后续容易再次出现“代码完成但产品偏离”的问题。

---

### **3.2.5 新垂类扩展者**

未来新增 vertical 的人可能不是原始开发者。系统必须让他们知道新增一个垂类需要做什么。

他们关心的是：

```text
在哪里注册 vertical；
如何定义 display_name；
如何绑定 workflow；
如何准备 case；
如何测试新垂类；
如何让前端显示新垂类；
如何让历史记录和案例库自动按 vertical 工作。
```

因此，MVP v1.0 必须把新增 vertical 的扩展路径写清楚。

---

## **3.3 核心使用场景**

MVP v1.0 至少要覆盖以下核心使用场景。

---

### **场景一：选择垂类并基础生成**

用户进入 Vertical Content Studio。

系统显示当前内容平台：

```text
小红书 xhs
```

系统显示当前内容形态：

```text
图文笔记 image_text_note
```

系统显示当前垂类：

```text
美甲 nail
```

在 MVP v1.0 中，nail 可以是默认且唯一启用的垂类，但页面和状态中必须体现 vertical 概念。

用户选择或确认当前垂类后，输入内容需求，例如：

```text
夏日短甲猫眼美甲，适合通勤，显白，低调但有细节
```

用户选择生成模式：

```text
基础生成
```

即：

```text
reference_source=none
```

用户点击生成。系统创建任务，并返回 job_id。前端进入任务进度模块，展示当前任务状态、阶段和耗时。

任务成功后，系统展示生成结果，包括：

```text
标题
正文
标签
多页图文结构
图片
诊断信息
```

生成结果写入服务端历史。用户之后可以从当前 vertical 的历史记录中再次打开。

---

### **场景二：当前垂类下的参考图生成**

用户进入生成工作台，当前 vertical 为：

```text
nail
```

用户选择生成模式：

```text
参考图生成
```

即：

```text
reference_source=local_path
```

用户上传一张美甲参考图。系统保存上传文件，并返回 `reference_image_path`。

用户输入 brief，例如：

```text
参考这张图片的颜色和质感，生成一篇适合小红书的短甲美甲图文
```

用户点击生成。前端提交任务时，payload 或 path 必须明确当前 vertical：

```text
vertical=nail
```

并包含：

```text
reference_source=local_path
reference_image_path=...
```

后端根据 nail 垂类的 workflow 或 adapter 处理该任务。任务成功后，预览中展示生成结果，并在 diagnostics 中展示 reference 相关信息。

历史记录中该任务应标记为：

```text
vertical=nail
reference_source=local_path
```

---

### **场景三：当前垂类下的案例复用生成**

用户进入案例库模块。系统根据当前 selectedVertical 加载案例：

```text
GET /api/verticals/nail/cases
```

用户浏览 nail 垂类下的案例，例如：

```text
夏日短甲猫眼案例
法式通勤美甲案例
新娘美甲案例
```

用户点击某个案例的“使用此案例”。

系统回到生成工作台，并自动完成以下动作：

```text
保持 vertical=nail；
生成模式切换为 case_id；
填入 selectedCase；
显示 case_id；
允许用户补充 brief。
```

用户点击生成。前端提交任务时包含：

```text
reference_source=case_id
case_id=case_nail_summer_cat_eye_001
```

后端必须校验：

```text
case.vertical == request.vertical
```

如果 case 属于其他 vertical，例如 outfit，则必须拒绝，不得静默使用。

任务成功后，系统展示结果，并写入 nail 历史记录。

---

### **场景四：服务端历史回放**

用户进入历史记录模块。

系统根据当前 selectedVertical 加载历史：

```text
GET /api/verticals/nail/notes
```

历史列表展示当前 nail 垂类下过去生成过的 note，包括：

```text
note_id
created_at
brief
selected_title
status
reference_source
page_count
generated_image_count
qa_score
```

用户点击某条历史记录。前端调用：

```text
GET /api/verticals/nail/notes/{note_id}/package
```

系统读取对应 note_package.json，并使用与实时任务成功后相同的渲染逻辑展示结果。

该过程必须满足：

```text
不依赖 localStorage；
清空浏览器缓存后仍可恢复；
package 字段缺失时不崩溃；
图片缺失时展示缺失状态；
旧 package 可以 fallback 推断 vertical；
损坏 package 不导致历史接口整体失败。
```

页面状态应显示：

```text
已从历史记录恢复
```

或等价表达。

---

### **场景五：任务失败与恢复**

用户提交任务后，任务可能失败、部分失败或超时。

系统必须在任务进度模块中展示：

```text
status
stage
elapsed_seconds
error_code
error_message
error_stage
```

如果任务失败但已经产生部分 note_package，系统应允许展示成功部分，并标记失败部分。

如果 job_store 中已经没有 job，但前端或历史中有 note_id，系统应尝试通过 package 回放恢复。

该场景的目标是：

```text
任务失败时用户知道失败在哪里；
已有结果尽量不丢；
能恢复的 package 必须可以恢复；
不能恢复时给出明确提示。
```

---

### **场景六：新增垂类扩展**

未来需要新增一个垂类，例如：

```text
outfit
```

开发者不应该复制一整套 nail 页面和 API，而应该按以下路径扩展：

```text
新增 vertical registry 配置；
新增 outfit adapter；
绑定 outfit workflow；
准备 outfit cases；
补充 outfit 测试；
前端通过 GET /api/verticals 自动看到 outfit；
历史记录通过 vertical=outfit 自动隔离；
案例库通过 vertical=outfit 自动加载。
```

MVP v1.0 不要求 outfit 真实上线，但必须保证系统设计不会阻止这种扩展。

为了验证这一点，v1.0 可以增加一个 mock 或 sample vertical，用于测试：

```text
未知 vertical 不会 fallback 到 nail；
vertical registry 可以返回多个条目；
历史记录可以按 vertical 过滤；
案例库可以按 vertical 过滤；
前端状态不是写死 nail。
```

这个 mock/sample vertical 不要求具备真实高质量生成能力，只用于验证平台抽象没有写死。

---

## **3.4 关键用户流程总览**

MVP v1.0 的关键用户流程包括：

```text
流程一：选择 vertical → 基础生成 → 任务进度 → 内容预览 → 写入历史
流程二：选择 vertical → 上传参考图 → 参考图生成 → 预览 → 历史回放
流程三：选择 vertical → 案例库 → 选择 case → 案例复用生成 → 预览
流程四：选择 vertical → 历史记录 → 打开 package → 恢复预览
流程五：任务失败 → 展示错误 → 尝试 package fallback → 展示可恢复内容
流程六：新增 vertical → registry/adapter/case/test → 平台自动识别
```

这些流程后续会在第 6 章中进一步细化为可验收的操作路径。

---

## **3.5 v1.0 的用户体验原则**

MVP v1.0 的用户体验不追求复杂和华丽，但必须清晰、稳定、可恢复。

### **3.5.1 垂类清晰**

用户必须知道当前正在使用哪个 vertical。

即使 v1.0 只有 nail 一个启用垂类，页面也应该显示：

```text
当前垂类：美甲 nail
```

而不是把所有文案都写死为“美甲工具”。

这样做的目的不是增加复杂度，而是避免后续扩展时推翻页面结构。

---

### **3.5.2 模式清晰**

用户必须知道当前使用哪种生成模式：

```text
基础生成
参考图生成
案例复用
```

三种模式应在 UI 中明确区分，对应到后端：

```text
reference_source=none
reference_source=local_path
reference_source=case_id
```

用户不应通过猜测某个输入框是否为空来决定生成模式。

---

### **3.5.3 状态清晰**

任务执行中，用户必须知道：

```text
任务是否已创建；
job_id 是什么；
当前 status 是什么；
当前 stage 是什么；
运行多久了；
是否失败；
失败在哪里；
是否可以恢复。
```

长任务不能只显示“运行中”，否则用户无法判断系统是否卡住。

---

### **3.5.4 结果可用**

内容预览必须支持用户真实使用结果。

至少要支持：

```text
看标题；
看正文；
看标签；
看每页结构；
看图片；
复制核心内容；
打开历史结果；
处理图片缺失；
处理 partial_failed。
```

如果只是显示一段 JSON，不算完成内容预览。

---

### **3.5.5 历史可靠**

用户生成过的内容不能只存在浏览器 localStorage 中。

MVP v1.0 必须确保：

```text
清空 localStorage 后历史仍可恢复；
换浏览器访问同一服务端仍可看到历史；
历史项可以打开 package；
历史按 vertical 隔离。
```

---

### **3.5.6 案例可见**

案例库必须是用户可见的内容资产模块，而不是隐藏参数。

用户应该能看到：

```text
有哪些案例；
案例属于哪个 vertical；
案例标题是什么；
案例有哪些标签；
案例评分或质量如何；
点击后如何使用。
```

---

### **3.5.7 扩展可控**

新增垂类时，用户和开发者都不应感知到系统架构混乱。

新增 vertical 的流程应该是：

```text
注册 vertical；
配置 adapter；
准备 case；
补测试；
验收；
上线。
```

而不是复制整套系统。

---

## **3.6 本阶段不覆盖的用户场景**

为了控制 MVP v1.0 范围，以下用户场景不纳入 v1.0 必须验收。

```text
多用户登录；
团队协作；
云端权限管理；
自动发布到小红书；
跨平台内容一键改写；
复杂图片编辑；
批量任务队列管理；
大规模 CMS 管理；
多垂类同时达到生产级内容质量；
完整商业化后台；
复杂数据看板。
```

这些可以进入 v1.1、v1.2 或后续 backlog，但不得阻塞 v1.0。

v1.0 的重点仍然是：

```text
平台抽象正确；
nail 链路完整；
历史可靠；
案例可见；
任务可观察；
结果可使用；
验收可执行。
```

---

# **4. MVP v1.0 范围定义**

## **4.1 v1.0 范围原则**

MVP v1.0 采用以下范围策略：

```text
通用平台底座 + nail 美甲首个垂类落地
```

这句话是 v1.0 最重要的范围边界。

它意味着：

```text
v1.0 不是只做 nail 美甲工具；
v1.0 也不是一次性做完所有行业垂类；
v1.0 要做的是一个可扩展的多垂类内容工作台底座，并用 nail 作为首个真实垂类完成端到端验证。
```

因此，v1.0 的验收必须分成两层：

```text
平台级能力验收
垂类级能力验收
```

平台级能力关注：

```text
系统是否有 vertical 概念；
API 是否支持 vertical；
历史记录是否按 vertical 过滤；
案例库是否按 vertical 隔离；
note_package 是否写入 vertical；
前端页面是否不再写死 nail；
新增 vertical 是否有清晰扩展路径。
```

垂类级能力关注：

```text
nail 是否可以完成真实生成；
nail 是否可以上传参考图；
nail 是否可以使用案例复用；
nail 是否可以展示任务进度；
nail 是否可以展示内容预览；
nail 是否可以从历史记录回放；
nail 是否可以通过测试和手动验收。
```

v1.0 的成功标准不是“做出所有行业”，而是：

```text
平台抽象正确；
nail 链路完整；
未来扩展其他 vertical 不需要重写系统。
```

---

## **4.2 v1.0 必须完成的范围：Must Have**

以下内容属于 MVP v1.0 必须完成范围。任何一项未完成，都不能判定 v1.0 完整通过。

---

### **4.2.1 垂类注册与选择**

系统必须支持 `vertical` 概念，并将其作为平台级核心字段。

MVP v1.0 至少内置并启用一个真实垂类：

```text
nail
```

即美甲。

系统必须提供 vertical registry 或等价机制，用于定义当前可用垂类。registry 中至少包含：

```text
vertical
display_name
enabled
content_platforms
content_types
supported_reference_sources
default_page_count
workflow_id
case_enabled
reference_image_enabled
```

前端必须能够显示当前 vertical。即使 v1.0 只有 nail 一个垂类，也不能把页面文案完全写死为“美甲工具”。页面应表达为：

```text
当前平台：小红书 xhs
内容形态：图文笔记 image_text_note
当前垂类：美甲 nail
```

API 创建任务时必须明确 vertical。可以通过以下两种方式之一实现：

```text
路径中包含 vertical，例如 POST /api/verticals/{vertical}/notes；
或 request body 中包含 vertical 字段。
```

推荐方式是路径中包含 vertical。

所有 job、note、case、history item、note_package 都必须包含或能够推导出 vertical。

未知 vertical 不允许自动 fallback 到 nail。请求不存在或未启用的 vertical 时，后端必须返回 4xx 错误。

---

### **4.2.2 生成工作台**

生成工作台必须支持用户创建当前 vertical 下的小红书图文笔记生成任务。

生成工作台必须包含以下字段：

```text
content_platform，默认 xhs；
content_type，默认 image_text_note；
vertical，v1.0 默认 nail；
scenario，可选；
brief，必填；
generate_images，布尔值；
reference_source，必填；
reference_image_path，local_path 模式使用；
case_id，case_id 模式使用；
options，可选扩展参数。
```

生成工作台必须支持三种生成模式：

```text
基础生成：reference_source=none
参考图生成：reference_source=local_path
案例复用生成：reference_source=case_id
```

三种模式必须在 UI 中明确区分，而不是依赖用户是否填写某个隐藏字段来推断。

提交任务时，前端必须根据当前模式构造合法 payload。后端也必须进行同样的互斥校验，不能只依赖前端校验。

生成工作台必须支持以下动作：

```text
输入 brief；
选择或显示当前 vertical；
选择生成模式；
上传参考图；
从案例库带入 case_id；
提交任务；
清空表单；
查看提交错误。
```

v1.0 中，nail 必须完整支持三种模式。

---

### **4.2.3 参考来源 reference_source**

`reference_source` 是通用平台字段，不属于 nail 特有字段。

MVP v1.0 必须支持以下三种取值：

```text
none
local_path
case_id
```

规则如下：

```text
reference_source=none 时，不得传 reference_image_path，不得传 case_id。
reference_source=local_path 时，必须传 reference_image_path，不得传 case_id。
reference_source=case_id 时，必须传 case_id，不得传 reference_image_path。
```

前端必须在提交前校验这些规则。

后端必须在接口层或 schema 层再次校验这些规则。

非法组合必须返回 4xx 错误，不能静默修正，也不能自动忽略字段。

当 `reference_source=case_id` 时，后端还必须校验：

```text
case.vertical == request.vertical
```

不允许跨 vertical 使用 case。

---

### **4.2.4 任务创建与任务状态**

系统必须支持创建长任务，并返回 `job_id`。

任务状态必须至少支持：

```text
queued
running
succeeded
failed
partial_failed
timeout
restored
```

任务状态对象必须尽可能包含以下字段：

```text
job_id
vertical
content_platform
content_type
status
stage
note_id
progress_text
started_at
updated_at
elapsed_seconds
error_code
error_message
error_stage
```

其中 `stage` 推荐支持：

```text
queued
planning
copywriting
image_generation
qa
saving
succeeded
failed
partial_failed
timeout
restored
```

如果某些 stage 暂时无法精确提供，也必须在文档和验收报告中说明限制。

前端 Progress 模块必须展示：

```text
job_id；
status；
stage；
elapsed_seconds；
note_id，如果已产生；
error_message，如果失败；
是否可以 fallback 恢复。
```

任务成功后，前端必须自动加载并渲染 note package 或 job result。

任务失败时，前端必须展示错误信息。不能只显示“失败”，而不显示失败原因。

---

### **4.2.5 内容预览**

内容预览必须以内容生产者可用的方式展示生成结果，而不是只展示原始 JSON。

Preview 模块必须展示：

```text
note_id
content_platform
content_type
vertical
scenario
selected_title
caption/body
tags
pages
image_urls
qa_score
diagnostics
```

其中 pages 至少应展示：

```text
page_index
page_title 或 title
page_copy 或 copy
visual_prompt
image_url
status
```

内容预览必须支持以下动作：

```text
复制标题；
复制正文；
复制标签；
复制单页文案；
打开图片；
从历史 package 恢复；
展示图片缺失状态；
展示 partial_failed 成功部分。
```

如果 package 字段不完整，前端不能崩溃。必须使用 fallback 文案或空状态展示。

如果图片缺失，前端应显示：

```text
图片缺失
```

或等价状态，而不是导致整个预览失败。

---

### **4.2.6 服务端历史记录**

历史记录必须是服务端能力，不能只依赖 localStorage。

MVP v1.0 必须提供按 vertical 过滤的历史记录接口。

推荐接口为：

```text
GET /api/verticals/{vertical}/notes
```

该接口应扫描服务端 output 目录或持久化存储中的 note_package，返回当前 vertical 下可回放的历史 note 列表。

历史列表中的每个 item 至少包含：

```text
note_id
content_platform
content_type
vertical
scenario
created_at
brief
selected_title
status
reference_source
page_count
generated_image_count
qa_score
package_path 或 package_url
```

历史记录必须满足：

```text
清空 localStorage 后仍可加载；
换浏览器访问同一服务端仍可加载；
可以按 vertical 过滤；
output 为空时返回空数组，不返回 500；
单个损坏 package 不导致接口整体失败；
旧 package 缺少 vertical 时允许 fallback 推断；
不能返回本地绝对路径；
不能允许路径穿越。
```

localStorage 最近任务可以保留，但只能作为快捷入口，不能替代服务端历史记录。

必须明确：

```text
localStorage 恢复不等于服务端历史。
```

---

### **4.2.7 历史 package 回放**

系统必须支持通过 note_id 打开历史 package。

推荐接口为：

```text
GET /api/verticals/{vertical}/notes/{note_id}/package
```

该接口必须读取对应 note_package，并返回可供 Preview 模块渲染的结构化结果。

历史回放必须满足：

```text
点击历史项可以恢复完整预览；
回放结果与实时任务成功后的预览使用同一渲染逻辑；
note_id 不存在时返回 404；
vertical 与 note 不匹配时返回 404 或 4xx；
package 字段缺失时前端不崩溃；
图片缺失时文本内容仍可展示；
旧 package 可以 fallback 补齐 vertical；
损坏 package 不影响其他历史项。
```

页面应显示：

```text
已从历史记录恢复
```

或等价状态。

---

### **4.2.8 案例库**

案例库必须是用户可见的产品模块，不是隐藏参数输入。

MVP v1.0 必须提供当前 vertical 下的案例列表接口。

推荐接口为：

```text
GET /api/verticals/{vertical}/cases
```

每个 case 至少包含：

```text
case_id
content_platform
content_type
vertical
scenario
title
style_tags
source_note_id
qa_score
preview_image_url
```

案例库必须满足：

```text
案例按 vertical 隔离；
当前 selectedVertical 只能展示对应 vertical 的案例；
用户可以点击“使用此案例”；
点击后生成工作台切换为 case_id 模式；
case_id 自动带入生成任务；
提交任务时后端校验 case.vertical 与 request.vertical 一致；
无案例时展示空状态；
案例加载失败时展示错误和重试入口。
```

v1.0 不要求案例库做复杂管理后台，但必须支持浏览和选择案例。

必须明确：

```text
case_id 参数存在不等于案例库完成。
```

---

### **4.2.9 静态资源访问**

系统必须支持访问生成输出资源和上传输入资源。

至少包括：

```text
output 图片；
input 上传参考图；
note_package 中引用的图片；
case preview 图片。
```

静态资源路径必须满足：

```text
前端展示的图片 URL 可打开；
不返回本地绝对路径；
不暴露不必要的服务器文件结构；
不允许路径穿越；
旧 output 路径可以兼容；
推荐未来按 vertical 组织资源。
```

推荐输出目录结构为：

```text
output/
  nail/
    nail_20260430_xxx/
      note_package.json
      page_01.png
      page_02.png
```

如果当前实际目录仍是：

```text
output/{note_id}/note_package.json
```

v1.0 可以兼容，但 note_package 和历史 item 中必须包含或推导出 vertical。

---

### **4.2.10 基础安全**

MVP v1.0 必须满足以下基础安全要求：

```text
前端不得使用 innerHTML 渲染用户可控内容；
历史记录、案例库、预览内容必须使用 textContent/createElement 等安全 DOM API；
上传文件必须校验后缀和类型；
后端不得返回本地绝对路径；
历史接口不得允许路径穿越；
package 接口不得允许通过 note_id 读取 output 之外的文件；
未知 vertical 不得 fallback 到 nail；
跨 vertical case_id 不得使用；
损坏 JSON 不得导致接口整体 500。
```

这些属于 v1.0 的硬性要求，不是优化项。

---

## **4.3 v1.0 建议完成的范围：Should Have**

以下内容建议在 MVP v1.0 完成，但如果因时间原因未完成，可以在验收报告中说明，并进入 v1.1 backlog。

---

### **4.3.1 历史记录增强**

历史记录建议支持：

```text
按时间倒序展示；
limit/offset 分页；
keyword 关键词搜索；
按 reference_source 过滤；
按 status 过滤；
展示 brief、标题、图片数量、qa_score、reference_source；
展示 vertical 与 scenario；
支持“复用为新任务”。
```

其中，按 vertical 过滤是 Must Have，不能降级为 Should Have。

---

### **4.3.2 案例库增强**

案例库建议支持：

```text
关键词搜索；
按 style_tags 筛选；
按 qa_score 排序；
展示 preview_image；
展示 source_note_id；
从历史结果保存为案例；
案例空状态引导；
案例加载失败重试。
```

v1.0 必须有案例列表和选择能力，但复杂搜索和保存为案例可以后续做。

---

### **4.3.3 诊断信息展示**

任务完成后，Preview 模块建议展示：

```text
diagnostics.reference
diagnostics.timing
page_timings
workflow_id
adapter_id
inferred_fields
missing_assets
```

这些信息有助于调试和验收，尤其是多垂类扩展时，可以判断某条结果来自哪个 workflow/adapter。

---

### **4.3.4 新增 sample vertical 验证**

为了验证系统没有写死 nail，建议在 v1.0 中增加一个 mock 或 sample vertical，例如：

```text
sample
```

或：

```text
demo
```

该 vertical 不需要具备真实高质量生成能力，只用于验证：

```text
GET /api/verticals 可以返回多个 vertical；
未知 vertical 不会 fallback 到 nail；
历史记录可以按 vertical 过滤；
案例库可以按 vertical 过滤；
前端状态可以切换或显示非 nail vertical；
平台 API 不依赖 nail 命名。
```

如果时间有限，这项可以作为 Should Have，但平台代码必须至少不阻碍未来实现。

---

### **4.3.5 复制与导出增强**

内容预览建议支持：

```text
复制标题；
复制正文；
复制标签；
复制全部发布文案；
复制单页文案；
导出 Markdown；
下载图片；
打开输出目录静态链接。
```

其中复制标题、正文、标签属于 Must Have；导出 Markdown 和批量下载可以后续做。

---

## **4.4 v1.0 可后续增强的范围：Could Have**

以下功能不作为 MVP v1.0 必须范围，可以进入后续版本。

```text
单页重生成；
多任务并发管理；
任务队列管理；
批量生成；
批量下载图片；
导出完整发布包；
从历史一键保存案例；
案例评分管理；
案例标签管理；
多垂类内容质量评估；
用户登录；
多用户隔离；
权限系统；
数据看板；
SQLite/数据库持久化；
完整 CMS 管理后台；
自动发布到小红书。
```

这些功能中，有些未来很重要，但不应阻塞 v1.0。

v1.0 的重点仍然是：

```text
通用平台抽象；
nail 链路闭环；
历史可靠；
案例可见；
任务可观察；
结果可使用；
验收可执行。
```

---

## **4.5 v1.0 明确不做的范围：Won’t Have**

为了避免范围失控，MVP v1.0 明确不做以下内容：

```text
不做复杂账号系统；
不做团队协作；
不做云端权限管理；
不做自动发布到小红书；
不做复杂图片编辑器；
不做完整 CMS；
不做商业化后台；
不做复杂数据分析看板；
不做所有垂类的生产级质量验证；
不做多平台内容发布；
不强制引入数据库，除非 output 扫描无法满足历史回放；
不重写所有既有 workflow；
不复制多套按垂类命名的 Web 页面和 API。
```

特别需要强调：

```text
v1.0 不做多个真实垂类的全面质量验收；
但 v1.0 必须具备未来新增多个垂类的架构能力。
```

这条是防止范围失控的关键。

---

## **4.6 v1.0 范围边界示例**

为了避免后续理解偏差，下面用几个示例说明什么属于 v1.0，什么不属于 v1.0。

| 需求 | 是否属于 v1.0 | 原因 |
|---|---:|---|
| 页面显示当前 vertical=nail | 是 | 平台级 vertical 概念必须存在 |
| GET /api/verticals 返回 nail | 是 | 垂类 registry 必须存在 |
| nail 基础生成 | 是 | 首个垂类必须端到端跑通 |
| nail 参考图生成 | 是 | 三种 reference_source 之一 |
| nail 案例复用生成 | 是 | 案例库必须产品化 |
| 服务端历史按 nail 过滤 | 是 | 历史记录必须按 vertical 工作 |
| outfit 真实高质量生成 | 否 | v1.0 不要求多个真实垂类质量验证 |
| sample vertical mock 测试 | 建议 | 用于验证平台未写死 nail |
| 用户登录 | 否 | 不属于 MVP v1.0 |
| 自动发布到小红书 | 否 | 不属于 MVP v1.0 |
| SQLite 历史库 | 可选 | output 扫描优先，数据库后续引入 |
| 单页重生成 | 否 | 可进入 v1.1 或 backlog |
| 批量下载图片 | 否 | 可后续增强 |

---

# **5. 信息架构与页面结构**

## **5.1 信息架构原则**

Vertical Content Studio 的信息架构必须服务于两个目标：

```text
让当前 nail 垂类可以真实使用；
让未来新增 vertical 时不需要重写页面结构。
```

因此，页面结构应按平台能力组织，而不是按 nail 专用功能组织。

也就是说，页面不应设计成：

```text
美甲生成页
美甲历史页
美甲案例页
```

而应设计成：

```text
垂类选择
生成工作台
任务进度
内容预览
历史记录
案例库
```

其中，当前 selectedVertical 可以是：

```text
nail
```

未来可以是：

```text
outfit
pet
home
food
```

页面模块本身不应随着 vertical 改变而复制。不同 vertical 只应改变：

```text
垂类名称；
可用 scenario；
可用案例；
workflow；
默认参数；
文案提示；
结果风格；
诊断信息。
```

---

## **5.2 核心页面模块**

MVP v1.0 包含 6 个核心模块：

```text
1. 垂类上下文 Vertical Context
2. 生成工作台 Studio
3. 任务进度 Jobs / Progress
4. 内容预览 Preview
5. 历史记录 History
6. 案例库 Cases
```

这 6 个模块可以实现为单页中的多个区域，也可以实现为多 Tab 或多路由页面。v1.0 不强制要求复杂前端路由，但产品上必须具备这些模块的可见入口或清晰区域。

| 模块 | 主要目的 | 核心内容 | v1.0 是否必须 |
|---|---|---|---|
| Vertical Context | 明确当前平台、内容形态、垂类 | xhs、image_text_note、nail | 是 |
| Studio | 创建生成任务 | brief、模式、参考图、case_id、参数 | 是 |
| Progress | 查看任务状态 | job_id、status、stage、error、timing | 是 |
| Preview | 查看生成结果 | 标题、正文、标签、页面、图片、诊断 | 是 |
| History | 回放过去结果 | note 列表、vertical 过滤、打开 package | 是 |
| Cases | 复用优质案例 | case 列表、选择 case_id、回填任务 | 是 |

当前 v0 页面已有 Studio、Progress、Preview 的雏形，但缺少 Vertical Context、完整 History 和 Cases。

---

## **5.3 垂类上下文模块 Vertical Context**

Vertical Context 是 v1.0 新增的基础模块，用于明确当前用户正在操作哪个内容平台、内容形态和垂类。

该模块必须展示：

```text
当前平台：小红书 xhs
内容形态：图文笔记 image_text_note
当前垂类：美甲 nail
```

如果 v1.0 只有 nail 一个启用垂类，可以先做成只读展示，或做成只有一个选项的下拉选择器。

推荐展示方式：

```text
平台：小红书
内容：图文笔记
垂类：美甲 nail
```

如果系统实现了 `GET /api/verticals`，前端应从接口加载 vertical list，而不是在页面中硬编码。

Vertical Context 需要影响以下模块：

```text
Studio 创建任务；
History 加载历史；
Cases 加载案例；
Preview 展示 package；
Progress 展示 job vertical。
```

当 selectedVertical 变化时，系统应重新加载：

```text
当前 vertical 的历史记录；
当前 vertical 的案例库；
当前 vertical 的默认参数。
```

MVP v1.0 中，如果暂时不允许切换 vertical，也必须在代码状态中保留：

```text
selectedVertical
```

默认值为：

```text
nail
```

---

## **5.4 生成工作台 Studio**

生成工作台是用户创建内容任务的主入口。

Studio 必须包含以下字段：

```text
vertical，当前垂类，默认 nail；
scenario，可选；
brief，内容需求，必填；
generate_images，是否生成图片；
reference_source，生成模式；
reference_image_path，参考图模式使用；
case_id，案例复用模式使用；
options，扩展参数。
```

Studio 必须包含以下操作：

```text
选择生成模式；
上传参考图；
从案例库选择案例；
提交生成任务；
清空表单；
显示校验错误；
显示提交错误。
```

---

### **5.4.1 生成模式 UI**

生成模式必须以明确方式展示，推荐使用 radio、segmented control 或 tab：

```text
基础生成
参考图生成
案例复用
```

对应关系为：

```text
基础生成 → reference_source=none
参考图生成 → reference_source=local_path
案例复用 → reference_source=case_id
```

三种模式切换时，前端必须清理不适用字段。

例如：

```text
切换到基础生成时，清空 reference_image_path 和 case_id；
切换到参考图生成时，清空 case_id；
切换到案例复用时，清空 reference_image_path。
```

这样可以避免非法 payload。

---

### **5.4.2 基础生成模式**

基础生成模式下，用户只需要输入 brief，并选择是否生成图片。

前端提交时应构造：

```json
{
  "content_platform": "xhs",
  "content_type": "image_text_note",
  "scenario": null,
  "brief": "夏日短甲猫眼美甲",
  "generate_images": true,
  "reference_source": "none",
  "reference_image_path": null,
  "case_id": null,
  "options": {}
}
```

如果 API path 已包含 vertical：

```text
POST /api/verticals/nail/notes
```

body 中可以不重复传 vertical，但 job、history、package 中必须包含 vertical。

---

### **5.4.3 参考图生成模式**

参考图生成模式下，用户必须先上传参考图。

上传成功后，系统返回：

```text
reference_image_path
```

前端提交时应构造：

```json
{
  "content_platform": "xhs",
  "content_type": "image_text_note",
  "scenario": null,
  "brief": "参考这张图的颜色和质感，生成小红书图文",
  "generate_images": true,
  "reference_source": "local_path",
  "reference_image_path": "/static/input/xxx.png",
  "case_id": null,
  "options": {}
}
```

如果用户选择参考图生成，但没有上传参考图，前端必须阻止提交并提示。

后端也必须校验：

```text
reference_source=local_path 时 reference_image_path 必填
```

---

### **5.4.4 案例复用模式**

案例复用模式下，用户应通过案例库选择案例，而不是手动输入隐藏 case_id。

选择案例后，Studio 应显示：

```text
已选择案例：xxx
case_id：case_nail_xxx
```

前端提交时应构造：

```json
{
  "content_platform": "xhs",
  "content_type": "image_text_note",
  "scenario": null,
  "brief": "沿用这个案例的风格，生成一个新的夏日短甲主题",
  "generate_images": true,
  "reference_source": "case_id",
  "reference_image_path": null,
  "case_id": "case_nail_summer_cat_eye_001",
  "options": {}
}
```

如果用户选择案例复用，但没有选择案例，前端必须阻止提交。

后端必须校验：

```text
case_id 存在；
case.vertical 与 request vertical 一致。
```

---

## **5.5 任务进度模块 Progress**

Progress 模块用于展示当前任务状态。

该模块必须包含：

```text
job_id
vertical
status
stage
progress_text
note_id
started_at
updated_at
elapsed_seconds
error_code
error_message
error_stage
```

用户提交任务后，前端应立即进入 Progress 状态，并开始轮询：

```text
GET /api/jobs/{job_id}
```

轮询结果中如果包含 note_id，前端应记录该 note_id，用于后续 package fallback。

任务成功后，前端应加载结果并渲染 Preview。

任务失败后，前端应展示错误信息，并停止自动轮询。

如果任务状态为 `partial_failed`，前端应展示可用结果，同时标记失败部分。

如果 job 查询返回 404，但前端已有 note_id，前端可以尝试调用 package 接口恢复：

```text
GET /api/verticals/{vertical}/notes/{note_id}/package
```

如果恢复成功，状态显示为：

```text
restored
```

或：

```text
已从 package 恢复
```

---

## **5.6 内容预览模块 Preview**

Preview 模块用于展示实时生成结果或历史 package 回放结果。

Preview 必须展示：

```text
note_id
content_platform
content_type
vertical
scenario
selected_title
caption/body
tags
pages
image_urls
qa_score
diagnostics
```

Preview 应分成几个自然区域：

```text
标题区；
正文区；
标签区；
多页内容区；
图片区；
诊断信息区；
操作区。
```

操作区至少应支持：

```text
复制标题；
复制正文；
复制标签；
复制单页内容；
打开图片；
回到历史项；
复用为新任务。
```

其中“复用为新任务”可以在 v1.0 中作为 Should Have，但复制标题、正文、标签应属于 Must Have。

Preview 渲染必须满足：

```text
不使用 innerHTML 渲染用户可控内容；
字段缺失时不崩溃；
图片缺失时显示缺失状态；
partial_failed 时展示成功部分；
历史回放和实时结果使用同一渲染逻辑。
```

必须明确：

```text
JSON 可读不等于内容预览完成。
```

---

## **5.7 历史记录模块 History**

History 模块用于展示服务端历史记录，不应依赖 localStorage。

History 必须根据当前 selectedVertical 加载：

```text
GET /api/verticals/{vertical}/notes
```

历史列表至少展示：

```text
note_id
created_at
brief
selected_title
status
reference_source
page_count
generated_image_count
qa_score
```

也应展示或隐含：

```text
content_platform
content_type
vertical
scenario
```

历史项必须支持：

```text
打开历史；
加载 package；
恢复预览；
显示恢复状态。
```

点击历史项后，前端调用：

```text
GET /api/verticals/{vertical}/notes/{note_id}/package
```

并将结果传给 Preview 模块。

History 空状态必须清晰表达：

```text
当前垂类还没有历史记录
```

而不是让用户以为页面损坏。

History 加载失败时，应展示错误信息和重试入口。

localStorage 最近任务可以作为 History 旁边的“最近查看”快捷入口，但不能替代 History。

---

## **5.8 案例库模块 Cases**

Cases 模块用于展示当前 selectedVertical 下的案例，并允许用户选择案例用于生成任务。

Cases 必须根据当前 selectedVertical 加载：

```text
GET /api/verticals/{vertical}/cases
```

案例列表至少展示：

```text
case_id
title
style_tags
scenario
qa_score
preview_image_url
source_note_id
```

案例项必须支持：

```text
查看案例摘要；
使用此案例；
回填到 Studio；
切换 Studio 到 case_id 模式。
```

选择案例后，Studio 中必须显示：

```text
当前已选择案例；
case_id；
案例标题；
案例 vertical。
```

如果案例加载为空，页面显示：

```text
当前垂类暂无案例
```

如果案例加载失败，页面显示错误并提供重试。

Cases 模块必须按 vertical 隔离，不允许在 nail 下展示 outfit 的案例。

---

## **5.9 页面布局建议**

MVP v1.0 可以继续采用轻量单页结构，但建议从当前三栏结构升级为“上下文 + 主工作区 + 资产区”的结构。

一种可行布局是：

```text
顶部：Vertical Context
左侧：Studio
中间：Progress + Preview
右侧：History + Cases
```

也可以采用 Tab 结构：

```text
顶部：Vertical Context
Tab 1：生成工作台
Tab 2：历史记录
Tab 3：案例库
Tab 4：当前任务/预览
```

v1.0 不强制使用哪种布局，但必须保证：

```text
用户能看到当前 vertical；
用户能创建任务；
用户能查看进度；
用户能查看结果；
用户能打开历史；
用户能选择案例。
```

如果采用单页结构，建议避免页面过度拥挤。History 和 Cases 可以做成折叠面板或 Tab。

---

## **5.10 前端状态模型**

前端至少应维护以下状态：

```text
verticalList
selectedVertical
selectedScenario
selectedReferenceSource
selectedCase
currentJob
currentNotePackage
historyList
caseList
uploadState
errorState
```

这些状态之间的关系如下：

```text
selectedVertical 决定 historyList 和 caseList；
selectedReferenceSource 决定 Studio 显示哪些输入；
selectedCase 只在 reference_source=case_id 时有效；
uploadState 只在 reference_source=local_path 时有效；
currentJob 决定 Progress；
currentNotePackage 决定 Preview。
```

当 selectedVertical 改变时，应清理或重置：

```text
selectedCase；
historyList；
caseList；
currentNotePackage，如果不属于新 vertical；
reference_source=case_id 的非法选择。
```

MVP v1.0 如果只启用 nail，也应保留这些状态结构，避免后续扩展时重写。

---

## **5.11 页面文案原则**

页面文案不应全部写死为美甲。

可以显示：

```text
当前垂类：美甲 nail
```

但不应把通用模块命名为：

```text
美甲历史
美甲案例
美甲任务
```

更推荐：

```text
历史记录
案例库
生成工作台
内容预览
任务进度
```

具体内容中可以显示：

```text
美甲
```

但模块名称应保持通用。

例如：

```text
正确：当前垂类暂无案例
正确：美甲 nail 暂无案例
不推荐：美甲案例库加载失败，请检查美甲接口
```

这是为了避免未来新增 vertical 时页面大面积修改。

---

## **5.12 页面验收要求**

MVP v1.0 页面必须满足以下要求：

```text
页面打开无报错；
页面展示当前平台、内容形态、垂类；
用户可以在 Studio 创建任务；
用户可以选择基础生成、参考图生成、案例复用；
用户可以看到任务进度；
任务成功后可以看到内容预览；
用户可以复制标题、正文、标签；
用户可以看到服务端历史记录；
用户可以点击历史记录恢复 package；
用户可以看到案例库；
用户可以选择案例并回填生成任务；
localStorage 清空后历史记录仍可加载；
页面不通过 innerHTML 渲染用户可控内容；
页面不把平台能力全部写死为 nail。
```

这些页面验收要求后续会进入第 12 章的验收矩阵。

---

# **6. 核心用户流程**

## **6.1 流程设计原则**

MVP v1.0 的核心用户流程必须围绕真实内容生产过程设计，而不是围绕接口调用过程设计。

用户实际关心的是：

```text
我现在在哪个垂类下工作？
我要生成什么内容？
我要不要用参考图？
我要不要复用案例？
任务现在跑到哪一步？
生成结果能不能直接用？
历史结果能不能找回？
案例能不能继续复用？
```

因此，MVP v1.0 的用户流程必须覆盖以下关键路径：

```text
选择或确认 vertical；
创建生成任务；
选择 reference_source；
观察任务进度；
查看内容预览；
从历史恢复；
从案例复用；
处理失败和 fallback；
验证新增 vertical 的扩展路径。
```

v1.0 中，真实落地 vertical 是：

```text
nail
```

但流程设计不得写死 nail。所有流程都应以 `selectedVertical` 为上下文，只是在 v1.0 验收时默认 `selectedVertical=nail`。

---

## **6.2 流程一：选择垂类并进行基础生成**

### **流程目标**

用户可以在当前 vertical 下，不使用参考图、不使用案例，仅通过 brief 创建一篇小红书图文笔记。

v1.0 中，该流程必须在 nail 垂类下完整跑通。

### **前置条件**

```text
服务正常启动；
GET /api/verticals 返回 nail；
前端已加载 selectedVertical=nail；
生成工作台可用；
reference_source 支持 none；
```

### **用户操作路径**

用户打开 Vertical Content Studio。

页面展示当前上下文：

```text
平台：小红书 xhs
内容形态：图文笔记 image_text_note
当前垂类：美甲 nail
```

用户在生成工作台中选择：

```text
基础生成
```

此时系统设置：

```text
reference_source=none
```

用户输入 brief，例如：

```text
夏日短甲猫眼美甲，适合通勤，显白，低调但有细节
```

用户选择是否生成图片，例如：

```text
generate_images=true
```

用户点击：

```text
生成内容
```

前端向后端提交创建任务请求。

推荐请求路径：

```text
POST /api/verticals/nail/notes
```

请求中包含：

```json
{
  "content_platform": "xhs",
  "content_type": "image_text_note",
  "scenario": null,
  "brief": "夏日短甲猫眼美甲，适合通勤，显白，低调但有细节",
  "generate_images": true,
  "reference_source": "none",
  "reference_image_path": null,
  "case_id": null,
  "options": {}
}
```

后端返回：

```json
{
  "job_id": "job_xxx",
  "status": "queued"
}
```

前端进入任务进度模块，开始轮询：

```text
GET /api/jobs/{job_id}
```

任务成功后，前端加载结果并渲染 Preview。

生成结果写入服务端 output，并可通过历史记录回放。

### **成功标准**

```text
用户可以看到 job_id；
用户可以看到任务状态；
任务成功后可以看到标题、正文、标签、多页结构和图片；
note_package 中包含 content_platform、content_type、vertical；
历史记录中可以看到该 note；
清空 localStorage 后仍可从历史记录打开该 note；
```

### **失败处理**

如果 brief 为空，前端必须阻止提交。

如果后端返回 4xx 或 5xx，前端必须展示错误信息。

如果任务失败，Progress 必须展示：

```text
status=failed
error_message
error_stage，如有
```

如果任务已经产生 note_id 或 package，系统应尝试支持 fallback 恢复。

---

## **6.3 流程二：当前垂类下的参考图生成**

### **流程目标**

用户可以在当前 vertical 下上传参考图，并基于该参考图生成小红书图文笔记。

v1.0 中，该流程必须在 nail 垂类下完整跑通。

### **前置条件**

```text
selectedVertical=nail；
reference_source 支持 local_path；
参考图上传接口可用；
上传目录可通过静态路径访问；
```

### **用户操作路径**

用户打开生成工作台，确认当前垂类为：

```text
美甲 nail
```

用户选择生成模式：

```text
参考图生成
```

系统设置：

```text
reference_source=local_path
```

页面显示参考图上传区域。

用户上传一张参考图。前端调用：

```text
POST /api/verticals/nail/reference-images
```

或兼容接口：

```text
POST /api/nail/reference-images
```

后端保存图片并返回：

```json
{
  "reference_image_path": "/static/input/xxx.png"
}
```

前端展示上传成功状态，并记录 `reference_image_path`。

用户输入 brief，例如：

```text
参考这张图的颜色和质感，生成一篇适合小红书发布的短甲美甲图文
```

用户点击生成。

前端提交：

```text
POST /api/verticals/nail/notes
```

请求中包含：

```json
{
  "content_platform": "xhs",
  "content_type": "image_text_note",
  "scenario": null,
  "brief": "参考这张图的颜色和质感，生成一篇适合小红书发布的短甲美甲图文",
  "generate_images": true,
  "reference_source": "local_path",
  "reference_image_path": "/static/input/xxx.png",
  "case_id": null,
  "options": {}
}
```

后端创建 job，并在 nail adapter/workflow 中使用该参考图。

任务成功后，Preview 展示生成结果，并在 diagnostics 中尽可能展示 reference 相关信息。

历史记录中该任务应包含：

```text
vertical=nail
reference_source=local_path
```

### **成功标准**

```text
参考图可以成功上传；
上传后可以得到 reference_image_path；
local_path 模式下不允许缺少 reference_image_path；
任务成功后可以展示结果；
历史记录中可以看到 reference_source=local_path；
package 中包含 vertical=nail；
图片静态 URL 可以打开；
```

### **失败处理**

如果用户选择参考图模式但未上传图片，前端必须阻止提交。

如果上传文件后缀或类型不合法，后端必须拒绝。

如果 `reference_source=local_path` 但没有 `reference_image_path`，后端必须返回 4xx。

如果图片后续缺失，Preview 仍应展示文本结果，并标记图片缺失或参考图不可用。

---

## **6.4 流程三：当前垂类下的案例复用生成**

### **流程目标**

用户可以从当前 vertical 的案例库选择一个案例，并基于该案例发起新的生成任务。

v1.0 中，该流程必须在 nail 垂类下完整跑通。

### **前置条件**

```text
selectedVertical=nail；
案例库接口可用；
至少存在一个 nail case；
reference_source 支持 case_id；
后端可以校验 case.vertical；
```

### **用户操作路径**

用户打开案例库模块。

前端调用：

```text
GET /api/verticals/nail/cases
```

系统返回 nail 垂类下的案例列表。

案例项展示：

```text
案例标题；
case_id；
style_tags；
scenario；
qa_score；
preview_image，如有；
```

用户点击某个案例的：

```text
使用此案例
```

系统回填生成工作台：

```text
selectedVertical=nail；
selectedReferenceSource=case_id；
selectedCase=该案例；
case_id=case_nail_xxx；
```

Studio 显示：

```text
已选择案例：夏日短甲猫眼案例
case_id：case_nail_summer_cat_eye_001
```

用户补充 brief，例如：

```text
沿用这个案例的风格，生成一个更适合夏天通勤的短甲主题
```

用户点击生成。

前端提交：

```text
POST /api/verticals/nail/notes
```

请求中包含：

```json
{
  "content_platform": "xhs",
  "content_type": "image_text_note",
  "scenario": null,
  "brief": "沿用这个案例的风格，生成一个更适合夏天通勤的短甲主题",
  "generate_images": true,
  "reference_source": "case_id",
  "reference_image_path": null,
  "case_id": "case_nail_summer_cat_eye_001",
  "options": {}
}
```

后端校验：

```text
case_id 存在；
case.vertical == request.vertical；
case 可用于当前 content_type；
```

校验通过后创建 job。

任务成功后，Preview 展示生成结果，History 记录该任务。

### **成功标准**

```text
案例库可以加载 nail 案例；
案例项包含 case_id 和 vertical；
点击案例后 Studio 切换到 case_id 模式；
case_id 自动带入；
提交任务时 payload 包含 reference_source=case_id；
后端校验 case.vertical 与 request.vertical 一致；
任务成功后可以展示结果；
历史记录中可以看到 reference_source=case_id；
```

### **失败处理**

如果案例库为空，页面显示：

```text
当前垂类暂无案例
```

如果案例加载失败，页面显示错误和重试按钮。

如果用户选择案例复用但未选择案例，前端必须阻止提交。

如果 case_id 不存在，后端返回 4xx。

如果 case_id 属于其他 vertical，后端必须返回 4xx，不得静默使用。

---

## **6.5 流程四：服务端历史记录回放**

### **流程目标**

用户可以从服务端历史记录中找回过去生成的 note，并完整恢复预览。

该流程不能依赖 localStorage。

### **前置条件**

```text
服务端 output 或持久化存储中存在 note_package；
历史记录接口可用；
package 回放接口可用；
selectedVertical 已确定；
```

### **用户操作路径**

用户进入 History 模块。

前端根据当前 selectedVertical 调用：

```text
GET /api/verticals/nail/notes
```

后端扫描 output 或持久化存储，返回历史 note 列表。

每条历史记录展示：

```text
note_id；
created_at；
brief；
selected_title；
status；
reference_source；
page_count；
generated_image_count；
qa_score；
```

用户点击某条历史记录。

前端调用：

```text
GET /api/verticals/nail/notes/{note_id}/package
```

后端返回 note_package。

前端使用与实时任务成功后相同的 Preview 渲染逻辑展示结果。

页面显示：

```text
已从历史记录恢复
```

或等价状态。

### **成功标准**

```text
清空 localStorage 后仍能看到历史记录；
点击历史项可以打开 package；
Preview 展示标题、正文、标签、页面和图片；
历史项包含 vertical；
历史列表按 selectedVertical 过滤；
旧 package 缺少 vertical 时可以 fallback 推断；
损坏 package 不导致整个历史接口 500；
返回路径不包含本机绝对路径；
```

### **失败处理**

如果 output 为空，返回空数组，页面显示：

```text
当前垂类暂无历史记录
```

如果某个 package 损坏，历史扫描跳过该项或记录 diagnostics，但不能导致接口整体失败。

如果 note_id 不存在，package 接口返回 404。

如果 note_id 存在但 vertical 不匹配，接口返回 404 或 4xx。

如果图片缺失，Preview 展示文本内容，并标记图片缺失。

---

## **6.6 流程五：任务失败、部分失败与 fallback 恢复**

### **流程目标**

用户在任务失败、部分失败或 job_store 丢失时，仍能理解失败原因，并尽可能恢复已有结果。

### **前置条件**

```text
任务状态接口可用；
package 回放接口可用；
job result 或 note_id 可记录；
前端支持 failed/partial_failed/restored 状态；
```

### **用户操作路径**

用户提交任务后，前端开始轮询：

```text
GET /api/jobs/{job_id}
```

如果任务运行中，Progress 展示：

```text
status=running
stage=...
elapsed_seconds=...
```

如果任务失败，接口返回：

```json
{
  "job_id": "job_xxx",
  "status": "failed",
  "stage": "image_generation",
  "error_code": "IMAGE_GENERATION_FAILED",
  "error_message": "图片生成失败",
  "error_stage": "image_generation"
}
```

前端停止轮询，并展示错误信息。

如果任务为 `partial_failed`，但已有部分 pages 或 package，前端展示成功部分，并标记失败部分。

如果 job 查询返回 404，但前端已有 note_id，则尝试：

```text
GET /api/verticals/{vertical}/notes/{note_id}/package
```

如果 package 存在，前端恢复 Preview，并显示：

```text
已从 package 恢复
```

### **成功标准**

```text
failed 状态展示错误原因；
partial_failed 状态展示成功部分；
timeout 状态有明确提示；
job 404 且有 note_id 时可以 fallback；
fallback 成功后 Preview 可用；
fallback 失败时有明确提示；
```

### **失败处理**

如果没有 note_id，无法 fallback 时，页面提示：

```text
任务记录不存在，且未找到可恢复的 note package
```

如果 package 损坏，页面提示 package 无法读取，但不导致页面崩溃。

---

## **6.7 流程六：新增 vertical 的扩展验证**

### **流程目标**

验证平台没有写死 nail，未来可以通过 registry 和 adapter 扩展新 vertical。

MVP v1.0 不要求新增 vertical 达到真实生产质量，但必须确保架构不阻碍扩展。

### **前置条件**

```text
存在 vertical registry；
平台 API 支持 /api/verticals；
任务、历史、案例接口支持 vertical path 或 vertical 字段；
```

### **扩展路径**

开发者新增一个 vertical，例如：

```text
sample
```

或未来的：

```text
outfit
```

需要执行以下步骤：

```text
新增 vertical registry 配置；
新增或绑定 vertical adapter；
准备 sample cases；
准备 sample output/package；
补充测试；
前端能显示或识别该 vertical；
历史记录能按该 vertical 过滤；
案例库能按该 vertical 过滤；
未知 vertical 不会 fallback 到 nail。
```

### **成功标准**

```text
GET /api/verticals 可以返回 nail 和 sample；
GET /api/verticals/sample/cases 不会返回 nail cases；
GET /api/verticals/sample/notes 不会返回 nail notes；
POST /api/verticals/unknown/notes 返回 4xx；
跨 vertical case_id 被拒绝；
前端状态中存在 selectedVertical，而不是硬编码 nail；
```

### **范围说明**

如果 v1.0 时间有限，sample vertical 可以只作为测试数据或 mock adapter 存在，不要求真实生成高质量内容。

但系统必须明确：

```text
新增 vertical 不应该复制整套 Web 页面和 API。
```

---

## **6.8 核心流程验收总览**

| 流程 | 验收重点 | v1.0 要求 |
|---|---|---|
| 基础生成 | selectedVertical + reference_source=none | nail 必须通过 |
| 参考图生成 | local_path 上传和生成 | nail 必须通过 |
| 案例复用 | case_id 选择与 vertical 校验 | nail 必须通过 |
| 历史回放 | 服务端历史，不依赖 localStorage | 必须通过 |
| 失败恢复 | failed/partial_failed/fallback | 必须通过 |
| 新垂类扩展 | registry/adapter/vertical 隔离 | 平台必须支持 |

这些流程后续必须进入手动验收 checklist。每次阶段验收时，不能只看测试命令通过，还必须手动验证这些用户路径。

---

# **7. 功能需求明细**

## **7.1 功能需求编写原则**

本章将 MVP v1.0 的能力拆解为可开发、可测试、可验收的功能需求。

每个功能需求使用 `FR-xxx` 编号。后续开发任务、测试用例、验收报告都必须引用这些编号。

这样做的目的是避免再次出现以下问题：

```text
有代码但没有需求编号；
有接口但没有前端入口；
有参数但没有产品能力；
有测试但没有用户流程；
有功能但不知道如何验收。
```

每个 FR 应至少包含：

```text
功能名称；
用户故事；
功能描述；
输入；
输出；
异常处理；
验收标准。
```

MVP v1.0 的开发任务必须能映射到一个或多个 FR。未映射 FR 的开发内容，不计入 v1.0 完成范围。

---

## **7.2 FR-000 垂类注册与选择**

### **功能名称**

垂类注册与选择。

### **用户故事**

作为内容生产者，我希望知道当前正在使用哪个内容垂类，以便系统根据不同垂类生成对应的小红书图文笔记。

作为开发者，我希望系统通过 registry 管理垂类，以便未来新增 vertical 时不需要复制整套 API 和页面。

### **功能描述**

系统提供 vertical registry 或等价机制，返回当前可用垂类列表。前端展示当前 selectedVertical。MVP v1.0 至少支持 nail 垂类。

所有生成、历史、案例和 package 回放能力都必须绑定 vertical。

### **输入**

```text
无必填输入。
可选 selectedVertical。
```

### **输出**

`GET /api/verticals` 或等价能力返回：

```json
{
  "verticals": [
    {
      "vertical": "nail",
      "display_name": "美甲",
      "enabled": true,
      "content_platforms": ["xhs"],
      "content_types": ["image_text_note"],
      "supported_reference_sources": ["none", "local_path", "case_id"],
      "default_page_count": 6,
      "workflow_id": "nail_note_workflow_v1",
      "case_enabled": true,
      "reference_image_enabled": true
    }
  ]
}
```

### **异常处理**

```text
无可用 vertical 时，前端展示不可创建任务状态；
请求不存在的 vertical 时，后端返回 404 或 400；
disabled vertical 不允许创建任务；
未知 vertical 不得 fallback 到 nail。
```

### **验收标准**

```text
GET /api/verticals 返回 200；
返回结果至少包含 nail；
前端显示当前 vertical；
创建任务、历史记录、案例库均使用当前 vertical；
请求未知 vertical 时返回 4xx；
未知 vertical 不会落入 nail 默认逻辑。
```

---

## **7.3 FR-001 创建生成任务**

### **功能名称**

创建小红书图文笔记生成任务。

### **用户故事**

作为内容生产者，我希望在当前 vertical 下输入内容需求并创建生成任务，以便系统为我生成对应垂类的小红书图文笔记。

### **功能描述**

用户在 Studio 中填写 brief，选择生成模式和参数后，点击生成。前端调用创建任务接口，后端返回 job_id。前端进入 Progress 状态并开始轮询。

推荐接口：

```text
POST /api/verticals/{vertical}/notes
```

现有 `/api/nail/notes` 可以作为兼容层保留，但新开发和文档应以通用接口为准。

### **输入**

```text
vertical，通过 path 或 body 指定，必填；
content_platform，默认 xhs；
content_type，默认 image_text_note；
scenario，可选；
brief，必填；
generate_images，布尔值；
reference_source，必填，枚举 none/local_path/case_id；
reference_image_path，local_path 模式必填；
case_id，case_id 模式必填；
options，可选。
```

### **输出**

```json
{
  "job_id": "job_xxx",
  "status": "queued"
}
```

### **异常处理**

```text
brief 为空时前端阻止提交；
unknown vertical 返回 4xx；
disabled vertical 返回 4xx；
reference_source 非法返回 4xx；
reference_source 与 reference_image_path/case_id 组合非法返回 4xx；
case_id 不存在返回 4xx；
case.vertical 与 request.vertical 不一致返回 4xx；
后端创建任务失败时返回结构化错误。
```

### **验收标准**

```text
nail 基础生成可以创建 job；
nail 参考图生成可以创建 job；
nail 案例复用生成可以创建 job；
三种模式 payload 正确且互斥；
创建任务时能识别 vertical；
未知 vertical 创建任务失败；
跨 vertical case_id 创建任务失败；
返回 job_id 后前端进入轮询状态。
```

---

## **7.4 FR-002 参考来源模式管理**

### **功能名称**

reference_source 三模式管理。

### **用户故事**

作为内容生产者，我希望明确选择基础生成、参考图生成或案例复用，而不是通过隐藏参数判断系统会如何生成。

### **功能描述**

前端提供三种生成模式，并映射到通用字段 `reference_source`：

```text
基础生成 → none
参考图生成 → local_path
案例复用 → case_id
```

三种模式在 UI 和 API 中都必须互斥。

### **输入**

```text
selectedReferenceSource；
reference_image_path；
case_id。
```

### **输出**

合法 payload：

```json
{
  "reference_source": "none",
  "reference_image_path": null,
  "case_id": null
}
```

或：

```json
{
  "reference_source": "local_path",
  "reference_image_path": "/static/input/xxx.png",
  "case_id": null
}
```

或：

```json
{
  "reference_source": "case_id",
  "reference_image_path": null,
  "case_id": "case_nail_xxx"
}
```

### **异常处理**

```text
none 模式下传 reference_image_path 或 case_id，应拒绝；
local_path 模式下缺少 reference_image_path，应拒绝；
local_path 模式下同时传 case_id，应拒绝；
case_id 模式下缺少 case_id，应拒绝；
case_id 模式下同时传 reference_image_path，应拒绝。
```

### **验收标准**

```text
UI 中可以明确选择三种模式；
切换模式时清理不适用字段；
前端阻止非法组合；
后端拒绝非法组合；
非法组合不能静默修正；
三种模式均能在 nail 下创建任务。
```

---

## **7.5 FR-003 参考图上传**

### **功能名称**

当前垂类下的参考图上传。

### **用户故事**

作为内容生产者，我希望在当前 vertical 下上传参考图，以便系统参考图片风格生成图文笔记。

### **功能描述**

用户选择参考图生成模式后，上传图片。后端保存图片，并返回可用于生成任务的 `reference_image_path`。

推荐接口：

```text
POST /api/verticals/{vertical}/reference-images
```

### **输入**

```text
vertical；
图片文件。
```

### **输出**

```json
{
  "reference_image_path": "/static/input/xxx.png",
  "filename": "xxx.png"
}
```

### **异常处理**

```text
未知 vertical 返回 4xx；
文件为空返回 4xx；
非法文件类型返回 4xx；
非法后缀返回 4xx；
保存失败返回结构化错误；
返回路径不得包含本地绝对路径。
```

### **验收标准**

```text
nail 下可以上传参考图；
上传成功后前端显示成功状态；
返回 reference_image_path 可用于 local_path 模式；
非法文件被拒绝；
返回路径不是本地绝对路径；
上传图片静态 URL 可访问。
```

---

## **7.6 FR-004 任务进度观察**

### **功能名称**

任务进度观察。

### **用户故事**

作为内容生产者，我希望知道长任务当前执行到哪一步，以判断任务是否正常运行。

### **功能描述**

前端根据 job_id 轮询任务状态接口，展示 status、stage、elapsed_seconds、error 等信息。

接口：

```text
GET /api/jobs/{job_id}
```

### **输入**

```text
job_id
```

### **输出**

```json
{
  "job_id": "job_xxx",
  "vertical": "nail",
  "content_platform": "xhs",
  "content_type": "image_text_note",
  "status": "running",
  "stage": "image_generation",
  "note_id": null,
  "progress_text": "正在生成图片",
  "elapsed_seconds": 128,
  "error_code": null,
  "error_message": null,
  "error_stage": null
}
```

### **异常处理**

```text
job_id 不存在时返回 404；
如果前端已有 note_id，则尝试 package fallback；
任务失败时停止轮询并展示错误；
任务超时时停止轮询并提示；
网络错误时允许用户手动重试。
```

### **验收标准**

```text
queued/running/succeeded/failed/partial_failed/timeout 状态均可正确展示；
Progress 展示 job_id、status、stage、elapsed_seconds；
failed 展示错误原因；
succeeded 后自动进入 Preview；
partial_failed 展示可用结果和失败标记；
job 404 且有 note_id 时可以尝试 fallback。
```

---

## **7.7 FR-005 内容预览**

### **功能名称**

生成结果内容预览。

### **用户故事**

作为内容生产者，我希望以可直接使用的方式查看标题、正文、标签、多页结构和图片，而不是只看到原始 JSON。

### **功能描述**

Preview 模块展示实时任务成功后的结果，或历史 package 回放结果。实时结果和历史结果必须使用同一套渲染逻辑。

### **输入**

```text
note_package；
或 job result 中的 package/result。
```

### **输出展示**

```text
note_id；
content_platform；
content_type；
vertical；
scenario；
selected_title；
caption/body；
tags；
pages；
image_urls；
qa_score；
diagnostics。
```

### **异常处理**

```text
字段缺失时使用 fallback；
pages 为空时展示空状态；
图片缺失时显示图片缺失；
partial_failed 时展示成功部分；
package 损坏时展示无法读取提示；
不得因单个字段缺失导致页面崩溃。
```

### **验收标准**

```text
标题可见；
正文可见；
标签可见；
多页内容可见；
图片可见或显示缺失状态；
支持复制标题、正文、标签；
历史回放和实时生成使用同一渲染逻辑；
不使用 innerHTML 渲染用户可控内容。
```

---

## **7.8 FR-006 服务端历史列表**

### **功能名称**

按 vertical 过滤的服务端历史列表。

### **用户故事**

作为内容生产者，我希望即使清空浏览器缓存，也能从历史记录中找回过去生成的内容。

### **功能描述**

后端提供历史列表接口，扫描服务端 output 目录或持久化存储中的 note_package，返回当前 vertical 下可回放的历史 note 列表。

推荐接口：

```text
GET /api/verticals/{vertical}/notes
```

### **输入**

```text
vertical，必填；
limit，可选；
offset，可选；
keyword，可选；
```

### **输出**

```json
{
  "notes": [
    {
      "note_id": "nail_20260430_xxx",
      "content_platform": "xhs",
      "content_type": "image_text_note",
      "vertical": "nail",
      "scenario": "summer_cat_eye",
      "created_at": "2026-04-30T09:09:13",
      "brief": "夏日短甲猫眼美甲",
      "selected_title": "短甲猫眼真的太适合夏天了",
      "status": "succeeded",
      "reference_source": "local_path",
      "page_count": 6,
      "generated_image_count": 6,
      "qa_score": 0.86
    }
  ]
}
```

### **异常处理**

```text
output 为空时返回空数组；
某个 note_package 损坏时跳过该项或记录 diagnostics；
旧 package 缺少 vertical 时允许 fallback 推断；
无法识别 vertical 时标记 unknown 或跳过，具体策略需统一；
不得返回本地绝对路径；
不得允许路径穿越；
未知 vertical 返回 4xx 或空列表，需在 API 合约中明确。
```

### **验收标准**

```text
localStorage 为空时仍能看到服务端历史；
GET /api/verticals/nail/notes 返回 nail 历史；
history item 包含 vertical；
点击历史记录可以打开 package；
损坏 JSON 不导致接口整体 500；
返回路径不包含本机绝对路径；
历史记录按时间倒序展示，若已实现。
```

---

## **7.9 FR-007 历史 package 回放**

### **功能名称**

历史 note package 回放。

### **用户故事**

作为内容生产者，我希望点击历史记录后可以完整恢复过去生成的标题、正文、标签、页面结构和图片。

### **功能描述**

前端点击历史项后，调用 package 接口，使用与实时任务成功后相同的渲染逻辑展示结果。

推荐接口：

```text
GET /api/verticals/{vertical}/notes/{note_id}/package
```

### **输入**

```text
vertical；
note_id。
```

### **输出**

```text
note_package
```

### **异常处理**

```text
note_id 不存在时返回 404；
vertical 与 note 不匹配时返回 404 或 4xx；
package 存在但图片缺失时仍展示文本，并标记图片缺失；
package 字段不完整时使用 fallback；
package 损坏时返回结构化错误。
```

### **验收标准**

```text
可以从历史列表打开任意有效 note；
展示内容与生成完成后的预览一致；
页面状态显示“已从历史记录恢复”或等价状态；
清空 localStorage 后仍可回放；
note_package 中包含或补齐 vertical；
图片缺失不导致整个预览失败。
```

---

## **7.10 FR-008 案例库列表与选择**

### **功能名称**

当前 vertical 下的案例库列表与选择。

### **用户故事**

作为内容生产者，我希望从当前垂类的案例库中选择一个优质案例作为参考，而不是手动输入 case_id。

### **功能描述**

前端展示当前 vertical 下的案例列表。用户点击“使用此案例”后，生成工作台进入 case_id 模式，并自动填入对应 case_id。

推荐接口：

```text
GET /api/verticals/{vertical}/cases
```

### **输入**

```text
vertical，必填；
keyword，可选；
style_tag，可选；
```

### **输出**

```json
{
  "cases": [
    {
      "case_id": "case_nail_summer_cat_eye_001",
      "content_platform": "xhs",
      "content_type": "image_text_note",
      "vertical": "nail",
      "scenario": "summer_cat_eye",
      "title": "夏日短甲猫眼案例",
      "style_tags": ["短甲", "猫眼", "夏日"],
      "source_note_id": "nail_20260430_xxx",
      "qa_score": 0.91,
      "preview_image_url": "/static/output/nail/xxx/page_01.png"
    }
  ]
}
```

### **异常处理**

```text
无案例时展示空状态；
案例加载失败时展示错误信息和重试按钮；
未知 vertical 返回 4xx 或空列表；
case preview 图片缺失时展示缺失状态；
返回路径不得包含本地绝对路径。
```

### **验收标准**

```text
GET /api/verticals/nail/cases 返回 nail 案例；
case item 包含 case_id 和 vertical；
前端可以展示案例列表；
点击案例后 Studio 切换到 case_id 模式；
case_id 正确带入任务 payload；
不允许跨 vertical 使用 case_id；
无案例时有空状态。
```

---

## **7.11 FR-009 静态资源访问**

### **功能名称**

生成资源与上传资源访问。

### **用户故事**

作为内容生产者，我希望能在页面中看到生成图片和上传参考图，并能打开这些资源。

### **功能描述**

系统提供 output 和 input 静态资源访问能力，用于展示生成图片、参考图、case preview 图片等。

### **输入**

```text
静态资源相对路径或 URL。
```

### **输出**

```text
可访问的图片或文件资源。
```

### **异常处理**

```text
资源不存在时返回 404；
路径穿越被拒绝；
不返回本地绝对路径；
不暴露不必要服务器目录；
图片缺失时前端显示缺失状态。
```

### **验收标准**

```text
生成图片 URL 可打开；
上传参考图 URL 可打开；
case preview 图片 URL 可打开，如存在；
note_package 中的图片路径可被前端展示；
返回路径不包含 /Users 等本地绝对路径；
路径中不允许 .. 穿越。
```

---

## **7.12 FR-010 错误处理与恢复**

### **功能名称**

任务错误处理与结果恢复。

### **用户故事**

作为内容生产者，我希望任务失败时知道失败原因，并尽可能恢复已有结果。

### **功能描述**

系统在任务失败、部分失败、超时、job 丢失、package 缺失等情况下，提供明确错误提示和可恢复路径。

### **输入**

```text
job status；
note_id；
package path；
error payload。
```

### **输出**

```text
错误提示；
恢复状态；
可用预览内容；
fallback 结果。
```

### **异常处理**

```text
failed 展示 error_message；
partial_failed 展示成功部分；
timeout 展示超时提示；
job 404 时尝试 note_id fallback；
package 不存在时展示不可恢复提示；
package 损坏时展示无法读取提示；
网络错误允许重试。
```

### **验收标准**

```text
失败任务不会让页面崩溃；
错误信息对用户可见；
partial_failed 可以展示成功部分；
job 404 fallback 可以恢复已有 note；
fallback 失败时有明确提示；
所有错误状态均可手动验收。
```

---

## **7.13 FR-011 安全渲染与输入校验**

### **功能名称**

前端安全渲染与后端输入校验。

### **用户故事**

作为系统维护者，我希望页面渲染和接口输入具备基础安全保护，避免用户可控内容造成页面注入、路径穿越、非法文件访问或跨垂类数据污染。

作为内容生产者，我希望即使历史记录、案例、标题、正文、标签中包含特殊字符，页面也能稳定展示，而不会崩溃或执行异常内容。

### **功能描述**

前端渲染历史记录、案例库、内容预览、错误信息、标题、正文、标签、brief、diagnostics 等用户可控或模型生成内容时，必须使用安全 DOM API。

后端必须校验上传文件、路径参数、vertical、case_id、note_id、reference_image_path 等输入，避免读取 output/input 目录之外的文件，避免未知 vertical 自动进入默认 nail 流程，避免跨 vertical 使用 case。

该功能属于 MVP v1.0 的基础安全要求，不是后续优化项。

### **输入**

```text
用户 brief；
模型生成 title；
模型生成 caption/body；
模型生成 tags；
模型生成 pages；
历史 note_id；
case_id；
vertical；
scenario；
reference_image_path；
上传文件；
错误信息；
diagnostics；
package 内容。
```

### **输出**

```text
安全渲染后的页面内容；
经过校验的 API 请求；
合法的静态资源路径；
结构化错误响应。
```

### **前端要求**

前端必须满足：

```text
历史记录渲染不得使用 innerHTML 拼接用户可控内容；
案例库渲染不得使用 innerHTML 拼接用户可控内容；
内容预览渲染不得使用 innerHTML 拼接用户可控内容；
错误信息渲染不得使用 innerHTML 拼接用户可控内容；
标题、正文、标签、brief、diagnostics 均应使用 textContent 或 createTextNode；
需要构建复杂 DOM 时，应使用 createElement、appendChild、textContent；
图片 URL 必须做基础校验；
缺失图片必须显示缺失状态；
字段缺失不得导致 JS 报错中断整个页面。
```

如果确实需要渲染受控 HTML，必须满足：

```text
HTML 内容不是用户输入或模型输出；
来源为固定模板；
经过明确 sanitize；
并在代码注释中说明原因。
```

但 MVP v1.0 建议完全避免动态 HTML 注入。

### **后端要求**

后端必须满足：

```text
未知 vertical 返回 4xx，不得 fallback 到 nail；
disabled vertical 不允许创建任务；
note_id 不得允许路径穿越；
case_id 不得允许路径穿越；
reference_image_path 不得指向 input/output 之外；
history 扫描只能扫描允许的 output 目录；
package 读取只能读取允许的 note_package.json；
返回路径不得包含本地绝对路径；
上传文件必须校验后缀；
上传文件必须校验 MIME 或实际文件类型，至少做基础校验；
非法 reference_source 组合必须返回 4xx；
case.vertical 与 request.vertical 不一致必须返回 4xx；
损坏 JSON 不得导致历史列表接口整体 500。
```

### **异常处理**

```text
非法 vertical：返回 400 或 404；
非法 note_id：返回 400 或 404；
非法 case_id：返回 400 或 404；
跨 vertical case：返回 400 或 409；
非法 reference_source 组合：返回 422 或 400；
非法上传文件：返回 400；
路径穿越尝试：返回 400 或 403；
package 损坏：package 接口返回结构化错误，历史列表跳过或记录 diagnostics；
资源缺失：返回 404，前端显示缺失状态。
```

错误响应至少应包含：

```json
{
  "error_code": "INVALID_REFERENCE_SOURCE",
  "message": "reference_source=local_path requires reference_image_path"
}
```

如果暂时无法统一 error_code，也必须至少返回清晰的 `message`。

### **验收标准**

```text
前端历史记录渲染不使用 innerHTML 拼接用户可控内容；
前端案例库渲染不使用 innerHTML 拼接用户可控内容；
前端预览渲染不使用 innerHTML 拼接用户可控内容；
brief/title/caption/tags 中包含特殊字符时页面正常展示；
上传非法文件被拒绝；
note_id 中包含 .. 时被拒绝；
case_id 中包含 .. 时被拒绝；
未知 vertical 不会进入 nail 流程；
跨 vertical case_id 被拒绝；
历史接口遇到损坏 package 不返回 500；
API 返回路径不包含本地绝对路径；
静态资源接口不允许访问 input/output 之外的文件。
```

---

## **7.14 FR-012 note_package 标准化**

### **功能名称**

多垂类 note_package 标准化。

### **用户故事**

作为内容生产者，我希望每次生成结果都能被稳定保存和回放。

作为开发者，我希望不同 vertical 的生成结果都遵循统一 package 结构，以便历史记录、内容预览、案例复用和后续扩展可以复用同一套逻辑。

### **功能描述**

MVP v1.0 必须定义统一的 `note_package.json` 基础结构。不同 vertical 可以在 diagnostics 或 vertical_specific 字段中扩展特有信息，但通用字段必须保持稳定。

`note_package.json` 是历史回放、内容预览、案例沉淀和测试验收的关键资产。

### **输入**

```text
生成任务结果；
workflow 输出；
adapter 输出；
图片生成结果；
诊断信息；
任务元数据。
```

### **输出**

标准化后的：

```text
note_package.json
```

### **推荐结构**

```json
{
  "note_id": "nail_20260430_xxx",
  "content_platform": "xhs",
  "content_type": "image_text_note",
  "vertical": "nail",
  "scenario": "summer_cat_eye",
  "created_at": "2026-04-30T09:09:13",
  "status": "succeeded",
  "request": {
    "brief": "夏日短甲猫眼美甲",
    "generate_images": true,
    "reference_source": "local_path",
    "reference_image_path": "/static/input/xxx.png",
    "case_id": null,
    "options": {}
  },
  "result": {
    "selected_title": "短甲猫眼真的太适合夏天了",
    "caption": "正文内容",
    "tags": ["短甲", "猫眼", "夏日美甲"],
    "pages": [
      {
        "page_index": 1,
        "title": "第一页标题",
        "copy": "第一页文案",
        "visual_prompt": "图片提示词",
        "image_url": "/static/output/nail/nail_20260430_xxx/page_01.png",
        "status": "succeeded"
      }
    ]
  },
  "diagnostics": {
    "reference": {},
    "timing": {},
    "page_timings": {},
    "inferred_fields": []
  }
}
```

### **必填字段**

MVP v1.0 中，package 至少应包含：

```text
note_id；
content_platform；
content_type；
vertical；
created_at；
status；
request.brief；
request.reference_source；
result.selected_title；
result.caption 或 result.body；
result.tags；
result.pages；
diagnostics，可为空对象。
```

如果旧 package 缺少部分字段，历史扫描和 package 回放服务可以 fallback 补齐，但必须记录：

```text
diagnostics.inferred_fields
```

或等价信息。

### **异常处理**

```text
package 字段缺失时，前端使用 fallback 展示；
package 缺少 vertical 时，后端尝试从路径或 note_id 推断；
无法推断 vertical 时标记 unknown；
pages 缺失时展示空状态；
image_url 缺失时展示图片缺失；
diagnostics 缺失时当作空对象处理；
package JSON 损坏时，package 接口返回结构化错误，历史列表跳过该项。
```

### **验收标准**

```text
新生成的 nail package 包含 content_platform、content_type、vertical；
package 可以被历史列表识别；
package 可以被 Preview 渲染；
package 字段缺失不会导致页面崩溃；
旧 package 可以 fallback；
损坏 package 不影响其他历史项；
diagnostics 缺失时页面仍可展示正文和标题。
```

---

## **7.15 FR-013 垂类适配器与工作流分发**

### **功能名称**

Vertical Adapter 与 workflow 分发。

### **用户故事**

作为开发者，我希望平台可以根据 vertical 分发到不同垂类的 workflow，以便未来新增行业时不需要复制整套 API、历史、案例和页面。

### **功能描述**

平台层接收统一的生成请求后，应通过 vertical registry 查找对应垂类配置，再调用对应的 adapter/workflow。

MVP v1.0 中，真实 adapter 可以只有 nail，但代码结构和接口语义不应写死为 nail。

### **输入**

```text
vertical；
content_platform；
content_type；
scenario；
CreateNoteRequest；
reference_source；
case_id；
reference_image_path。
```

### **输出**

```text
job_id；
job status；
note_package；
生成资源。
```

### **处理流程**

推荐流程：

```text
API 接收 /api/verticals/{vertical}/notes
        ↓
校验 vertical 是否存在且 enabled
        ↓
读取 vertical registry
        ↓
校验 reference_source
        ↓
如果 case_id 模式，校验 case.vertical
        ↓
选择 vertical adapter
        ↓
adapter 调用对应 workflow
        ↓
workflow 生成 note_package
        ↓
统一写入 output/history
        ↓
返回 job_id
```

### **异常处理**

```text
vertical 不存在：返回 404 或 400；
vertical disabled：返回 403 或 400；
adapter 不存在：返回 501 或 500，并记录错误；
workflow 不存在：返回结构化错误；
adapter 执行失败：job status=failed；
workflow 部分失败：job status=partial_failed；
```

### **验收标准**

```text
nail vertical 可以找到对应 adapter/workflow；
未知 vertical 不会调用 nail workflow；
adapter 执行失败时 job 进入 failed；
note_package 中记录 workflow_id 或 adapter_id，至少 Should Have；
新增 sample/mock vertical 时无需复制整套 API；
```

---

## **7.16 FR-014 前端垂类状态管理**

### **功能名称**

前端 selectedVertical 状态管理。

### **用户故事**

作为内容生产者，我希望页面明确显示当前垂类，并且历史记录、案例库、生成任务都围绕当前垂类工作。

作为开发者，我希望前端不把 nail 写死在所有逻辑里，以便后续新增 vertical 时只需要增加配置，而不是重写页面。

### **功能描述**

前端必须维护 `selectedVertical` 状态。MVP v1.0 中默认值可以是：

```text
nail
```

但生成、历史、案例、预览等模块都应读取该状态，而不是散落硬编码。

### **输入**

```text
verticalList；
selectedVertical；
用户选择的 vertical，如果支持切换。
```

### **输出**

```text
当前垂类上下文；
按 selectedVertical 创建任务；
按 selectedVertical 加载历史；
按 selectedVertical 加载案例；
按 selectedVertical 打开 package。
```

### **状态联动**

当 selectedVertical 初始化或变化时：

```text
刷新 History；
刷新 Cases；
重置 selectedCase；
校验 currentNotePackage 是否属于当前 vertical；
清空不匹配的 case_id；
更新页面上下文展示；
更新创建任务 API path。
```

MVP v1.0 如果只有 nail 一个垂类，也应保留这套状态结构。

### **异常处理**

```text
GET /api/verticals 失败时，页面显示垂类加载失败；
没有 enabled vertical 时，禁用生成按钮；
selectedVertical 不存在时，回到默认可用 vertical 或显示错误；
当前 package.vertical 与 selectedVertical 不匹配时，提示不能在当前垂类下打开。
```

### **验收标准**

```text
页面显示当前 vertical；
app.js 或前端逻辑中存在 selectedVertical 或等价状态；
创建任务使用 selectedVertical；
历史记录加载使用 selectedVertical；
案例库加载使用 selectedVertical；
选择案例后不改变 selectedVertical；
前端不应在所有请求中散落硬编码 nail；
```

---

## **7.17 FR-015 兼容旧接口与旧数据**

### **功能名称**

旧接口和旧 package 兼容。

### **用户故事**

作为系统维护者，我希望在升级到多垂类架构时，不破坏已有 nail 链路和历史结果。

### **功能描述**

MVP v1.0 推荐使用通用接口：

```text
/api/verticals/{vertical}/...
```

但现有 `/api/nail/...` 可以作为兼容层保留一段时间。

旧的 note_package 可能没有 `vertical`、`content_platform`、`content_type` 等字段，历史扫描和回放服务需要尽可能兼容。

### **输入**

```text
旧 /api/nail/... 请求；
旧 output 目录；
旧 note_package.json；
旧 note_id；
旧 case_id。
```

### **输出**

```text
兼容后的响应；
补齐或推断的 vertical；
可回放 package；
diagnostics.inferred_fields。
```

### **兼容策略**

推荐兼容策略：

```text
/api/nail/notes 转发或映射到 /api/verticals/nail/notes；
/api/nail/cases 转发或映射到 /api/verticals/nail/cases；
/api/nail/notes/{note_id}/package 转发或映射到 /api/verticals/nail/notes/{note_id}/package；
旧 package 缺少 vertical 时，从 note_id 前缀或目录推断 nail；
无法推断时标记 unknown；
旧 output 路径仍可扫描；
新 package 必须写入 vertical。
```

### **异常处理**

```text
旧 package 损坏时跳过或返回结构化错误；
旧 note_id 无法识别 vertical 时标记 unknown；
unknown vertical 的历史项是否展示，需要在 API 合约中明确；
兼容接口不得绕过新校验；
兼容接口不得允许非法 reference_source 组合。
```

### **验收标准**

```text
现有 nail 链路不被破坏；
旧 package 可以在历史记录中显示或被合理跳过；
旧 package 回放不会导致页面崩溃；
新生成 package 必须包含 vertical；
兼容接口仍执行安全校验；
文档明确旧接口只是兼容层，不是新开发主接口。
```

---

## **7.18 FR-016 基础复制与内容使用能力**

### **功能名称**

内容复制与基础使用能力。

### **用户故事**

作为内容生产者，我希望生成结果能直接用于内容整理和发布准备，而不是只能看不能用。

### **功能描述**

Preview 模块提供复制标题、正文、标签等基础操作。

MVP v1.0 不要求完整导出发布包，但必须提供最基本的内容复制能力。

### **输入**

```text
selected_title；
caption/body；
tags；
pages。
```

### **输出**

```text
复制到剪贴板的文本；
复制成功或失败提示。
```

### **必须支持**

```text
复制标题；
复制正文；
复制标签；
复制全部标题+正文+标签，Should Have；
复制单页文案，Should Have。
```

### **异常处理**

```text
剪贴板 API 不可用时显示失败提示；
字段为空时禁用对应复制按钮；
复制失败时不影响页面其他功能。
```

### **验收标准**

```text
标题复制可用；
正文复制可用；
标签复制可用；
复制后有成功提示；
字段为空时不会复制 undefined/null；
历史回放结果同样可以复制。
```

---

## **7.19 FR-017 空状态与加载状态**

### **功能名称**

页面空状态、加载状态与错误状态。

### **用户故事**

作为内容生产者，我希望页面在没有历史、没有案例、任务未开始、接口加载失败时，都能给出清晰状态，而不是看起来像坏了。

### **功能描述**

MVP v1.0 页面必须对关键模块提供清晰状态表达。

### **涉及模块**

```text
Vertical Context；
Studio；
Progress；
Preview；
History；
Cases；
Upload；
```

### **必须支持的状态**

```text
垂类加载中；
垂类加载失败；
任务待开始；
任务运行中；
任务成功；
任务失败；
任务部分失败；
任务超时；
预览为空；
历史为空；
历史加载失败；
案例为空；
案例加载失败；
参考图上传中；
参考图上传失败；
图片缺失；
package 恢复中；
package 恢复失败。
```

### **异常处理**

```text
接口失败时显示错误与重试；
空数组显示空状态；
null 字段显示占位文案；
加载中禁用重复提交；
任务运行中防止重复点击生成，或明确允许新任务。
```

### **验收标准**

```text
初始页面不显示误导性错误；
没有历史时显示空状态；
没有案例时显示空状态；
接口失败时有错误提示；
任务运行中显示加载状态；
任务失败时显示失败状态；
图片缺失时显示缺失状态；
```

---

## **7.20 FR-018 基础文档与验收报告**

### **功能名称**

项目文档与阶段验收报告。

### **用户故事**

作为项目负责人，我希望每个阶段都有明确文档、测试结果和验收结论，以避免开发过程中再次跑偏。

### **功能描述**

MVP v1.0 的每个 Milestone 完成后，必须输出阶段验收报告。报告记录实现内容、测试结果、手动验收、范围偏差和已知问题。

### **输入**

```text
当前需求文档；
commit hash；
测试命令输出；
手动验收结果；
浏览器验证结果；
已知问题。
```

### **输出**

```text
阶段验收报告；
功能验收矩阵状态；
测试结果摘要；
范围偏差检查结果。
```

### **验收标准**

```text
每个 Milestone 有验收报告；
报告包含 HEAD commit；
报告包含测试命令和结果；
报告包含手动验收 checklist；
报告包含范围偏差检查；
报告明确通过、有条件通过或不通过；
未通过项有后续修复计划。
```

---

## **7.21 功能需求优先级**

MVP v1.0 的 FR 优先级建议如下。

| 优先级 | FR | 功能 | 说明 |
|---|---|---|---|
| P0 | FR-000 | 垂类注册与选择 | 多垂类平台基础 |
| P0 | FR-001 | 创建生成任务 | 核心生成入口 |
| P0 | FR-002 | reference_source 模式管理 | 三链路基础 |
| P0 | FR-004 | 任务进度观察 | 长任务必须可观察 |
| P0 | FR-005 | 内容预览 | 结果必须可用 |
| P0 | FR-006 | 服务端历史列表 | 解决历史不可回放 |
| P0 | FR-007 | 历史 package 回放 | 历史恢复闭环 |
| P0 | FR-008 | 案例库列表与选择 | case_id 产品化 |
| P0 | FR-011 | 安全渲染与输入校验 | 基础安全硬要求 |
| P0 | FR-012 | note_package 标准化 | 历史/预览/案例基础 |
| P1 | FR-003 | 参考图上传 | nail 真实链路必需，已有基础 |
| P1 | FR-009 | 静态资源访问 | 图片展示基础 |
| P1 | FR-010 | 错误处理与恢复 | 提升可靠性 |
| P1 | FR-013 | 垂类适配器与工作流分发 | 多垂类扩展关键 |
| P1 | FR-014 | 前端垂类状态管理 | 避免前端写死 nail |
| P1 | FR-015 | 兼容旧接口与旧数据 | 平滑迁移 |
| P2 | FR-016 | 基础复制与内容使用能力 | 提升生产可用性 |
| P2 | FR-017 | 空状态与加载状态 | 提升体验稳定性 |
| P2 | FR-018 | 基础文档与验收报告 | 管理闭环 |

说明：

```text
P0 表示 v1.0 必须完成，否则不能判定完整通过；
P1 表示强烈建议在 v1.0 完成，若未完成必须说明原因；
P2 表示可以视时间完成，但应进入验收或 backlog。
```

其中，FR-003 虽然标为 P1，是因为当前已有参考图上传基础；但从 nail 端到端真实链路看，参考图生成仍应被纳入 v1.0 手动验收。

---

## **7.22 功能需求与核心模块映射**

| 模块 | 对应 FR | 说明 |
|---|---|---|
| Vertical Context | FR-000、FR-014 | 垂类注册、选择、前端状态 |
| Studio | FR-001、FR-002、FR-003、FR-008 | 创建任务、模式、参考图、案例回填 |
| Progress | FR-004、FR-010、FR-017 | 任务状态、错误、加载状态 |
| Preview | FR-005、FR-012、FR-016、FR-017 | 内容预览、package、复制、空状态 |
| History | FR-006、FR-007、FR-010、FR-015 | 历史列表、回放、fallback、旧数据兼容 |
| Cases | FR-008、FR-011、FR-017 | 案例展示、选择、安全、空状态 |
| Static Assets | FR-009、FR-011 | 图片、上传资源、路径安全 |
| Platform Core | FR-000、FR-013、FR-015 | registry、adapter、兼容层 |
| Documentation | FR-018 | 验收报告与文档闭环 |

这个映射用于后续检查：

```text
是否每个页面模块都有 FR；
是否每个 FR 都有页面入口；
是否存在后端能力没有前端入口；
是否存在开发任务没有需求编号。
```

---

## **7.23 功能需求与用户流程映射**

| 用户流程 | 对应 FR |
|---|---|
| 选择垂类并基础生成 | FR-000、FR-001、FR-002、FR-004、FR-005、FR-006 |
| 当前垂类下参考图生成 | FR-000、FR-001、FR-002、FR-003、FR-004、FR-005 |
| 当前垂类下案例复用生成 | FR-000、FR-001、FR-002、FR-008、FR-004、FR-005 |
| 服务端历史记录回放 | FR-000、FR-006、FR-007、FR-005、FR-012 |
| 任务失败与 fallback 恢复 | FR-004、FR-010、FR-007、FR-017 |
| 新增 vertical 扩展验证 | FR-000、FR-013、FR-014、FR-015 |
| 内容复制与生产使用 | FR-005、FR-016 |
| 基础安全与路径保护 | FR-011、FR-009 |

后续验收时，不能只按 FR 单独验收，也要按这些用户流程端到端验收。

---

## **7.24 第 7 章验收要求**

第 7 章本身也应该被验收。也就是说，在进入开发前，应确认：

```text
所有 Must Have 范围都有 FR 编号；
所有核心页面模块都有 FR 覆盖；
所有核心用户流程都有 FR 覆盖；
所有 P0 FR 都有明确验收标准；
每个 FR 都能映射到测试方案；
每个开发任务都能引用至少一个 FR；
不存在“只写了想法但无法测试”的需求；
不存在“只写了接口但没有页面入口”的需求。
```

如果某项开发任务无法映射到任何 FR，则需要先判断：

```text
是否应该新增 FR；
是否应该放入 backlog；
是否属于范围外功能。
```

不得在没有需求编号的情况下直接开发。

---

# **8. 数据模型与 API 合约**

## **8.1 API 与数据模型设计原则**

MVP v1.0 的 API 和数据模型必须支持多垂类扩展，同时保证 nail 作为首个 vertical 可以端到端落地。

设计原则如下：

```text
平台能力通用化；
垂类能力 adapter 化；
API 路径显式表达 vertical；
数据模型必须包含或可推导 vertical；
note_package 必须标准化；
历史记录和案例库必须按 vertical 隔离；
旧 nail 接口可以兼容，但不能作为新主接口；
未知 vertical 不得 fallback 到 nail；
跨 vertical case_id 不得使用。
```

API 和数据模型的目标不是追求复杂，而是解决当前项目最关键的几个问题：

```text
避免系统写死 nail；
避免历史记录无法回放；
避免案例库只是隐藏 case_id；
避免前后端字段不一致；
避免 package 结构不稳定；
避免未来新增 vertical 时复制整套系统。
```

---

## **8.2 推荐 API 路径风格**

MVP v1.0 推荐采用以下通用路径：

```text
GET  /api/verticals
POST /api/verticals/{vertical}/notes
GET  /api/verticals/{vertical}/notes
GET  /api/verticals/{vertical}/notes/{note_id}/package
POST /api/verticals/{vertical}/reference-images
GET  /api/verticals/{vertical}/cases
GET  /api/jobs/{job_id}
```

其中：

```text
vertical = nail、outfit、pet、home 等垂类标识
```

v1.0 真实启用的 vertical 至少包含：

```text
nail
```

现有接口可以作为兼容层保留，例如：

```text
POST /api/nail/notes
GET  /api/nail/notes
GET  /api/nail/notes/{note_id}/package
POST /api/nail/reference-images
GET  /api/nail/cases
```

但文档和新开发应以通用接口为准。

兼容层建议行为：

```text
/api/nail/notes 等价映射到 /api/verticals/nail/notes；
/api/nail/cases 等价映射到 /api/verticals/nail/cases；
兼容层仍必须执行 v1.0 的 reference_source、case.vertical、路径安全等校验；
兼容层不得绕过新的安全规则。
```

---

## **8.3 API 清单**

| 方法 | 路径 | 目的 | v1.0 必须 |
|---|---|---|---|
| GET | `/api/verticals` | 获取可用垂类列表 | 是 |
| POST | `/api/verticals/{vertical}/notes` | 创建当前垂类生成任务 | 是 |
| GET | `/api/jobs/{job_id}` | 查询任务状态 | 是 |
| GET | `/api/verticals/{vertical}/notes` | 获取当前垂类历史记录 | 是 |
| GET | `/api/verticals/{vertical}/notes/{note_id}/package` | 获取历史 package | 是 |
| POST | `/api/verticals/{vertical}/reference-images` | 上传当前垂类参考图 | 是 |
| GET | `/api/verticals/{vertical}/cases` | 获取当前垂类案例列表 | 是 |
| POST | `/api/nail/notes` | 旧接口兼容 | 可保留 |
| GET | `/api/nail/notes` | 旧接口兼容 | 可保留 |
| GET | `/api/nail/cases` | 旧接口兼容 | 可保留 |

说明：

```text
/api/verticals/{vertical}/... 是 v1.0 主接口；
/api/nail/... 是兼容接口；
新测试应优先覆盖通用接口，同时保留 nail 兼容接口回归测试。
```

---

## **8.4 通用响应格式建议**

MVP v1.0 不强制重构所有响应格式，但建议逐步统一成功和错误响应。

### **8.4.1 成功响应**

简单接口可以直接返回业务对象，例如：

```json
{
  "verticals": []
}
```

或：

```json
{
  "job_id": "job_xxx",
  "status": "queued"
}
```

如果后续需要统一包装，可以采用：

```json
{
  "ok": true,
  "data": {},
  "message": null
}
```

v1.0 不强制采用统一 wrapper，避免不必要的大改。

### **8.4.2 错误响应**

错误响应至少应包含：

```json
{
  "error_code": "INVALID_REFERENCE_SOURCE",
  "message": "reference_source=local_path requires reference_image_path"
}
```

如果当前框架暂时只能返回：

```json
{
  "detail": "error message"
}
```

也可以接受，但必须保证错误信息清晰可读。后续 v1.1 再统一 error_code。

v1.0 中建议优先定义以下 error_code：

```text
UNKNOWN_VERTICAL
DISABLED_VERTICAL
INVALID_REFERENCE_SOURCE
MISSING_REFERENCE_IMAGE
MISSING_CASE_ID
CASE_NOT_FOUND
CASE_VERTICAL_MISMATCH
NOTE_NOT_FOUND
PACKAGE_NOT_FOUND
PACKAGE_INVALID
INVALID_UPLOAD_FILE
PATH_NOT_ALLOWED
JOB_NOT_FOUND
WORKFLOW_FAILED
```

---

## **8.5 VerticalDefinition**

`VerticalDefinition` 表示一个可用垂类的注册信息。

### **字段定义**

```json
{
  "vertical": "nail",
  "display_name": "美甲",
  "enabled": true,
  "content_platforms": ["xhs"],
  "content_types": ["image_text_note"],
  "supported_reference_sources": ["none", "local_path", "case_id"],
  "default_page_count": 6,
  "workflow_id": "nail_note_workflow_v1",
  "case_enabled": true,
  "reference_image_enabled": true
}
```

### **字段说明**

| 字段 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| vertical | string | 是 | 垂类标识，如 nail |
| display_name | string | 是 | 展示名称，如 美甲 |
| enabled | boolean | 是 | 是否启用 |
| content_platforms | string[] | 是 | 支持的平台，v1.0 至少 xhs |
| content_types | string[] | 是 | 支持的内容形态，v1.0 至少 image_text_note |
| supported_reference_sources | string[] | 是 | 支持的参考来源 |
| default_page_count | number | 否 | 默认页数 |
| workflow_id | string | 是 | 对应 workflow |
| case_enabled | boolean | 是 | 是否启用案例库 |
| reference_image_enabled | boolean | 是 | 是否启用参考图 |

### **约束**

```text
vertical 必须全局唯一；
disabled vertical 不允许创建任务；
unknown vertical 不允许 fallback 到 nail；
supported_reference_sources 决定前端模式可用性；
workflow_id 用于 adapter 分发。
```

---

## **8.6 CreateNoteRequest**

`CreateNoteRequest` 表示创建生成任务的请求体。

当 API path 已包含 `{vertical}` 时，body 可以不重复传 vertical；但后端内部 job、note、history、package 中必须写入 vertical。

### **推荐请求体**

```json
{
  "content_platform": "xhs",
  "content_type": "image_text_note",
  "scenario": "summer_cat_eye",
  "brief": "夏日短甲猫眼美甲，适合通勤，显白，低调但有细节",
  "generate_images": true,
  "reference_source": "none",
  "reference_image_path": null,
  "case_id": null,
  "options": {}
}
```

### **字段说明**

| 字段 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| content_platform | string | 否 | 默认 xhs |
| content_type | string | 否 | 默认 image_text_note |
| scenario | string/null | 否 | 垂类内细分场景 |
| brief | string | 是 | 用户内容需求 |
| generate_images | boolean | 否 | 是否生成图片 |
| reference_source | string | 是 | none/local_path/case_id |
| reference_image_path | string/null | 条件必填 | local_path 模式必填 |
| case_id | string/null | 条件必填 | case_id 模式必填 |
| options | object | 否 | 扩展参数 |

### **reference_source 约束**

```text
reference_source=none：
  reference_image_path 必须为空；
  case_id 必须为空。

reference_source=local_path：
  reference_image_path 必填；
  case_id 必须为空。

reference_source=case_id：
  case_id 必填；
  reference_image_path 必须为空。
```

### **vertical 约束**

```text
path 中的 vertical 必须存在；
vertical 必须 enabled；
case_id 模式下，case.vertical 必须等于 path vertical；
未知 vertical 不允许 fallback 到 nail。
```

---

## **8.7 CreateNoteResponse**

`CreateNoteResponse` 表示创建任务后的返回结果。

```json
{
  "job_id": "job_a137f28f33bf",
  "status": "queued"
}
```

建议后续扩展为：

```json
{
  "job_id": "job_a137f28f33bf",
  "vertical": "nail",
  "content_platform": "xhs",
  "content_type": "image_text_note",
  "status": "queued",
  "created_at": "2026-04-30T10:08:23"
}
```

MVP v1.0 至少必须返回：

```text
job_id
status
```

建议返回：

```text
vertical
created_at
```

---

## **8.8 JobStatus**

`JobStatus` 表示任务状态。

### **推荐结构**

```json
{
  "job_id": "job_xxx",
  "vertical": "nail",
  "content_platform": "xhs",
  "content_type": "image_text_note",
  "status": "running",
  "stage": "image_generation",
  "note_id": null,
  "progress_text": "正在生成图片",
  "started_at": "2026-04-30T10:08:23",
  "updated_at": "2026-04-30T10:09:12",
  "elapsed_seconds": 49,
  "error_code": null,
  "error_message": null,
  "error_stage": null
}
```

### **status 取值**

```text
queued
running
succeeded
failed
partial_failed
timeout
restored
```

### **stage 推荐取值**

```text
queued
planning
copywriting
image_generation
qa
saving
succeeded
failed
partial_failed
timeout
restored
```

### **最低要求**

MVP v1.0 至少要支持：

```text
job_id
status
note_id，如已产生
error_message，如失败
```

但建议尽可能补齐：

```text
vertical
stage
elapsed_seconds
error_code
error_stage
```

---

## **8.9 NoteHistoryItem**

`NoteHistoryItem` 表示历史列表中的单条 note 摘要。

### **推荐结构**

```json
{
  "note_id": "nail_20260430_xxx",
  "content_platform": "xhs",
  "content_type": "image_text_note",
  "vertical": "nail",
  "scenario": "summer_cat_eye",
  "created_at": "2026-04-30T09:09:13",
  "brief": "夏日短甲猫眼美甲",
  "selected_title": "短甲猫眼真的太适合夏天了",
  "status": "succeeded",
  "reference_source": "local_path",
  "page_count": 6,
  "generated_image_count": 6,
  "qa_score": 0.86,
  "package_url": "/api/verticals/nail/notes/nail_20260430_xxx/package"
}
```

### **字段说明**

| 字段 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| note_id | string | 是 | note 唯一标识 |
| content_platform | string | 是 | 默认 xhs |
| content_type | string | 是 | 默认 image_text_note |
| vertical | string | 是 | 所属垂类 |
| scenario | string/null | 否 | 所属场景 |
| created_at | string | 是 | 创建时间，缺失时 fallback mtime |
| brief | string | 否 | 用户需求 |
| selected_title | string | 否 | 生成标题 |
| status | string | 是 | succeeded/failed/partial_failed/restored |
| reference_source | string | 否 | none/local_path/case_id |
| page_count | number | 否 | 页面数量 |
| generated_image_count | number | 否 | 图片数量 |
| qa_score | number/null | 否 | 质量评分 |
| package_url | string | 否 | package 接口路径 |

### **约束**

```text
不得返回本地绝对路径；
不得返回 output 之外的文件路径；
vertical 必须存在或被标记为 unknown/inferred；
历史列表必须按请求 vertical 过滤；
损坏 package 不得导致整个列表失败。
```

---

## **8.10 NotePackage**

`NotePackage` 是生成结果和历史回放的核心数据结构。

### **推荐结构**

```json
{
  "note_id": "nail_20260430_xxx",
  "content_platform": "xhs",
  "content_type": "image_text_note",
  "vertical": "nail",
  "scenario": "summer_cat_eye",
  "created_at": "2026-04-30T09:09:13",
  "status": "succeeded",
  "request": {
    "brief": "夏日短甲猫眼美甲",
    "generate_images": true,
    "reference_source": "local_path",
    "reference_image_path": "/static/input/xxx.png",
    "case_id": null,
    "options": {}
  },
  "result": {
    "selected_title": "短甲猫眼真的太适合夏天了",
    "caption": "正文内容",
    "tags": ["短甲", "猫眼", "夏日美甲"],
    "pages": [
      {
        "page_index": 1,
        "title": "第一页标题",
        "copy": "第一页文案",
        "visual_prompt": "图片提示词",
        "image_url": "/static/output/nail/nail_20260430_xxx/page_01.png",
        "status": "succeeded"
      }
    ]
  },
  "diagnostics": {
    "reference": {},
    "timing": {},
    "page_timings": {},
    "inferred_fields": []
  }
}
```

### **通用必填字段**

```text
note_id
content_platform
content_type
vertical
created_at
status
request
result
```

### **result 最低要求**

```text
selected_title
caption 或 body
tags
pages
```

### **diagnostics 说明**

`diagnostics` 可为空对象，但建议包含：

```text
reference
timing
page_timings
inferred_fields
missing_assets
workflow_id
adapter_id
```

---

## **8.11 CaseItem**

`CaseItem` 表示案例库中的案例。

### **推荐结构**

```json
{
  "case_id": "case_nail_summer_cat_eye_001",
  "content_platform": "xhs",
  "content_type": "image_text_note",
  "vertical": "nail",
  "scenario": "summer_cat_eye",
  "title": "夏日短甲猫眼案例",
  "style_tags": ["短甲", "猫眼", "夏日"],
  "source_note_id": "nail_20260430_xxx",
  "qa_score": 0.91,
  "preview_image_url": "/static/output/nail/nail_20260430_xxx/page_01.png"
}
```

### **字段说明**

| 字段 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| case_id | string | 是 | 案例 ID |
| content_platform | string | 是 | 默认 xhs |
| content_type | string | 是 | 默认 image_text_note |
| vertical | string | 是 | 所属垂类 |
| scenario | string/null | 否 | 所属场景 |
| title | string | 是 | 案例标题 |
| style_tags | string[] | 否 | 风格标签 |
| source_note_id | string/null | 否 | 来源 note |
| qa_score | number/null | 否 | 质量分 |
| preview_image_url | string/null | 否 | 预览图 |

### **约束**

```text
case_id 必须唯一，或在 vertical 内唯一且由后端统一解析；
case 必须归属 vertical；
创建任务时 case.vertical 必须等于 request vertical；
不得跨 vertical 使用 case；
preview_image_url 不得返回本地绝对路径。
```

---

## **8.12 UploadReferenceImageResponse**

`UploadReferenceImageResponse` 表示参考图上传结果。

```json
{
  "reference_image_path": "/static/input/xxx.png",
  "filename": "xxx.png"
}
```

建议扩展为：

```json
{
  "reference_image_path": "/static/input/nail/xxx.png",
  "filename": "xxx.png",
  "vertical": "nail",
  "content_type": "image_text_note",
  "mime_type": "image/png",
  "size_bytes": 123456
}
```

MVP v1.0 至少必须返回：

```text
reference_image_path
```

并保证该路径可用于 `reference_source=local_path` 的创建任务请求。

---

## **8.13 API：GET /api/verticals**

### **目的**

获取可用垂类列表。

### **请求**

```text
GET /api/verticals
```

### **响应**

```json
{
  "verticals": [
    {
      "vertical": "nail",
      "display_name": "美甲",
      "enabled": true,
      "content_platforms": ["xhs"],
      "content_types": ["image_text_note"],
      "supported_reference_sources": ["none", "local_path", "case_id"],
      "default_page_count": 6,
      "workflow_id": "nail_note_workflow_v1",
      "case_enabled": true,
      "reference_image_enabled": true
    }
  ]
}
```

### **验收**

```text
返回 200；
至少包含 nail；
nail.enabled=true；
nail.supported_reference_sources 包含 none/local_path/case_id；
前端可以用该接口初始化 selectedVertical。
```

---

## **8.14 API：POST /api/verticals/{vertical}/notes**

### **目的**

在指定 vertical 下创建生成任务。

### **请求**

```text
POST /api/verticals/nail/notes
```

请求体：

```json
{
  "content_platform": "xhs",
  "content_type": "image_text_note",
  "scenario": null,
  "brief": "夏日短甲猫眼美甲",
  "generate_images": true,
  "reference_source": "none",
  "reference_image_path": null,
  "case_id": null,
  "options": {}
}
```

### **响应**

```json
{
  "job_id": "job_xxx",
  "status": "queued"
}
```

### **错误**

```text
UNKNOWN_VERTICAL
DISABLED_VERTICAL
INVALID_REFERENCE_SOURCE
MISSING_REFERENCE_IMAGE
MISSING_CASE_ID
CASE_NOT_FOUND
CASE_VERTICAL_MISMATCH
WORKFLOW_FAILED
```

### **验收**

```text
nail 基础生成返回 job_id；
nail local_path 生成返回 job_id；
nail case_id 生成返回 job_id；
非法 reference_source 组合返回 4xx；
未知 vertical 返回 4xx；
跨 vertical case 返回 4xx。
```

---

## **8.15 API：GET /api/jobs/{job_id}**

### **目的**

查询任务状态。

### **请求**

```text
GET /api/jobs/job_xxx
```

### **响应**

```json
{
  "job_id": "job_xxx",
  "vertical": "nail",
  "content_platform": "xhs",
  "content_type": "image_text_note",
  "status": "running",
  "stage": "image_generation",
  "note_id": null,
  "progress_text": "正在生成图片",
  "elapsed_seconds": 128,
  "error_code": null,
  "error_message": null,
  "error_stage": null
}
```

### **验收**

```text
queued/running/succeeded/failed/partial_failed/timeout 可展示；
succeeded 时可获得 note_id 或 result；
failed 时可获得 error_message；
job 不存在时返回 404；
job 404 且前端有 note_id 时可走 package fallback。
```

---

## **8.16 API：GET /api/verticals/{vertical}/notes**

### **目的**

获取指定 vertical 下的服务端历史记录。

### **请求**

```text
GET /api/verticals/nail/notes
```

可选参数：

```text
limit
offset
keyword
status
reference_source
```

### **响应**

```json
{
  "notes": [
    {
      "note_id": "nail_20260430_xxx",
      "content_platform": "xhs",
      "content_type": "image_text_note",
      "vertical": "nail",
      "scenario": "summer_cat_eye",
      "created_at": "2026-04-30T09:09:13",
      "brief": "夏日短甲猫眼美甲",
      "selected_title": "短甲猫眼真的太适合夏天了",
      "status": "succeeded",
      "reference_source": "local_path",
      "page_count": 6,
      "generated_image_count": 6,
      "qa_score": 0.86
    }
  ]
}
```

### **验收**

```text
localStorage 为空时仍返回历史；
只返回请求 vertical 的历史；
损坏 package 不导致 500；
output 为空时返回空数组；
返回路径不含本机绝对路径；
旧 package 可以 fallback 推断 vertical。
```

---

## **8.17 API：GET /api/verticals/{vertical}/notes/{note_id}/package**

### **目的**

读取历史 note package，用于回放预览。

### **请求**

```text
GET /api/verticals/nail/notes/nail_20260430_xxx/package
```

### **响应**

返回 `NotePackage`。

### **错误**

```text
NOTE_NOT_FOUND
PACKAGE_NOT_FOUND
PACKAGE_INVALID
PATH_NOT_ALLOWED
VERTICAL_MISMATCH
```

### **验收**

```text
有效 note_id 返回 package；
note_id 不存在返回 404；
vertical 不匹配返回 404 或 4xx；
package 损坏返回结构化错误；
图片缺失不影响文本回放；
返回 package 中包含或补齐 vertical。
```

---

## **8.18 API：POST /api/verticals/{vertical}/reference-images**

### **目的**

上传当前 vertical 下的参考图。

### **请求**

```text
POST /api/verticals/nail/reference-images
```

表单文件：

```text
file
```

### **响应**

```json
{
  "reference_image_path": "/static/input/xxx.png",
  "filename": "xxx.png"
}
```

### **验收**

```text
合法图片上传成功；
非法后缀被拒绝；
非法 MIME 或明显非图片文件被拒绝；
返回路径不是本地绝对路径；
返回 reference_image_path 可用于 local_path 任务；
静态 URL 可打开。
```

---

## **8.19 API：GET /api/verticals/{vertical}/cases**

### **目的**

获取当前 vertical 下的案例列表。

### **请求**

```text
GET /api/verticals/nail/cases
```

可选参数：

```text
keyword
style_tag
scenario
```

### **响应**

```json
{
  "cases": [
    {
      "case_id": "case_nail_summer_cat_eye_001",
      "content_platform": "xhs",
      "content_type": "image_text_note",
      "vertical": "nail",
      "scenario": "summer_cat_eye",
      "title": "夏日短甲猫眼案例",
      "style_tags": ["短甲", "猫眼", "夏日"],
      "source_note_id": "nail_20260430_xxx",
      "qa_score": 0.91,
      "preview_image_url": "/static/output/nail/nail_20260430_xxx/page_01.png"
    }
  ]
}
```

### **验收**

```text
返回当前 vertical 的 cases；
case item 包含 case_id 和 vertical；
不返回其他 vertical 的 case；
无案例时返回空数组；
preview_image_url 不含本地绝对路径；
前端可以点击 case 回填 Studio。
```

---

## **8.20 兼容接口策略**

MVP v1.0 允许保留旧 nail 接口，但必须明确其定位：

```text
旧接口是兼容层；
通用接口是主接口；
新功能优先在通用接口实现；
旧接口不得绕过新校验；
旧接口最终可在后续版本废弃。
```

建议兼容映射：

| 旧接口 | 新接口 |
|---|---|
| `POST /api/nail/notes` | `POST /api/verticals/nail/notes` |
| `GET /api/nail/notes` | `GET /api/verticals/nail/notes` |
| `GET /api/nail/notes/{note_id}/package` | `GET /api/verticals/nail/notes/{note_id}/package` |
| `POST /api/nail/reference-images` | `POST /api/verticals/nail/reference-images` |
| `GET /api/nail/cases` | `GET /api/verticals/nail/cases` |

兼容接口测试必须覆盖：

```text
旧接口仍可用；
旧接口结果与新接口一致；
旧接口同样拒绝非法 reference_source；
旧接口同样拒绝跨 vertical case；
旧接口同样不返回本地绝对路径。
```

---

## **8.21 输出目录与资源路径约定**

推荐新输出目录结构：

```text
output/
  nail/
    nail_20260430_xxx/
      note_package.json
      page_01.png
      page_02.png
```

推荐上传目录结构：

```text
input/
  nail/
    upload_xxx.png
```

如果当前项目暂时仍使用旧结构：

```text
output/{note_id}/note_package.json
input/{filename}
```

v1.0 可以兼容，但必须满足：

```text
note_package 中写入 vertical；
history item 中返回 vertical；
资源 URL 不返回本地绝对路径；
history 扫描可以识别旧结构；
新结构作为后续推荐方向。
```

静态资源 URL 推荐为：

```text
/static/output/nail/nail_20260430_xxx/page_01.png
/static/input/nail/upload_xxx.png
```

---

## **8.22 API 合约验收要求**

MVP v1.0 的 API 合约必须通过以下验收：

```text
GET /api/verticals 返回 nail；
POST /api/verticals/nail/notes 可创建基础任务；
POST /api/verticals/nail/notes 可创建 local_path 任务；
POST /api/verticals/nail/notes 可创建 case_id 任务；
非法 reference_source 组合返回 4xx；
未知 vertical 返回 4xx；
GET /api/jobs/{job_id} 返回任务状态；
GET /api/verticals/nail/notes 返回服务端历史；
GET /api/verticals/nail/notes/{note_id}/package 可回放 package；
POST /api/verticals/nail/reference-images 可上传参考图；
GET /api/verticals/nail/cases 返回案例列表；
所有路径响应不返回本地绝对路径；
损坏 package 不导致历史列表 500；
旧 /api/nail/... 兼容接口仍可用，如决定保留。
```

---

# **9. 技术路线与实现方案**

## **9.1 技术路线总览**

MVP v1.0 延续当前轻量架构，不在 v1.0 阶段引入复杂前端框架、账号系统、权限系统或完整数据库化改造。

推荐技术路线是：

```text
FastAPI 后端
+ 静态前端 Web
+ 通用 vertical API
+ vertical registry
+ vertical adapter
+ output 扫描历史
+ case service
+ note_package 标准化
+ nail 首个垂类落地
```

核心策略是：

```text
不推倒重来；
保留 v0 已打通链路；
把平台能力从 nail 中抽象出来；
优先补齐历史、案例、进度、预览和验收闭环；
为未来新增 vertical 留出 registry/adapter 扩展点。
```

MVP v1.0 不应过早引入复杂架构，但必须避免继续写死 nail。

---

## **9.2 架构原则**

MVP v1.0 的架构原则如下。

### **9.2.1 平台能力与垂类能力分离**

平台能力包括：

```text
Web 页面结构；
任务创建与轮询；
历史记录扫描与回放；
案例库列表与选择；
参考来源模式管理；
note_package 读取与预览；
静态资源访问；
通用 API 合约；
安全校验；
测试与验收。
```

垂类能力包括：

```text
vertical 元数据；
垂类默认参数；
垂类 prompt；
垂类 workflow；
垂类 case seed；
垂类输出字段补齐；
垂类 diagnostics；
垂类质量评估策略。
```

平台层不能写死 nail。nail 应作为一个 vertical adapter 接入平台。

---

### **9.2.2 通用 API 优先，旧接口兼容**

新接口以：

```text
/api/verticals/{vertical}/...
```

为主。

旧接口：

```text
/api/nail/...
```

可以保留为兼容层，但不作为新开发主入口。

这样既避免一次性大重构破坏当前链路，又能保证未来扩展方向正确。

---

### **9.2.3 output 扫描优先，数据库后置**

v1.0 的历史记录优先通过扫描 output 目录下的 note_package.json 实现。

暂不强制引入 SQLite 或其他数据库，除非出现以下情况：

```text
output 扫描性能不可接受；
需要复杂搜索和分页；
需要记录未产生 package 的失败任务；
需要多用户隔离；
需要长期稳定归档；
需要强一致状态管理。
```

这可以降低 v1.0 实施复杂度，优先解决“历史记录无法可靠回放”的核心痛点。

---

### **9.2.4 note_package 作为核心资产**

`note_package.json` 是 v1.0 的核心资产。

它支撑：

```text
内容预览；
历史回放；
案例沉淀；
测试验证；
跨浏览器恢复；
后续内容管理。
```

因此，v1.0 必须标准化 package 结构，并保证新生成 package 写入：

```text
content_platform
content_type
vertical
request
result
diagnostics
```

---

### **9.2.5 安全渲染和路径安全作为硬要求**

v1.0 中所有用户可控内容和模型生成内容都不得通过不安全 `innerHTML` 拼接渲染。

后端必须限制：

```text
vertical；
note_id；
case_id；
reference_image_path；
上传文件；
package 路径；
静态资源路径。
```

安全要求不能因为 MVP 阶段而省略。

---

## **9.3 推荐后端模块结构**

当前项目可以不立即大规模移动目录，但目标结构建议如下。

```text
api/
  app.py
  schemas.py
  routes/
    verticals.py
    jobs.py
    static.py
  services/
    vertical_registry.py
    job_service.py
    history_service.py
    case_service.py
    package_service.py
    reference_image_service.py

verticals/
  base/
    adapter.py
    schemas.py
  nail/
    adapter.py
    workflow.py
    cases/
```

如果现有项目结构已经是：

```text
verticals/nail/api/app.py
verticals/nail/api/routes.py
verticals/nail/web/app.js
```

v1.0 可以渐进式调整，不要求一次性迁移到全局 `api/` 目录。

但必须做到：

```text
新增通用 /api/verticals/{vertical}/... 路由；
抽出 vertical registry；
抽出 history/case/package 通用服务；
nail 逻辑通过 adapter 或等价方式接入；
不再把所有新逻辑写死在 nail routes 中。
```

---

## **9.4 Vertical Registry 实现方案**

`vertical_registry` 可以先用 Python 常量、JSON 配置或 YAML 配置实现。

MVP v1.0 推荐先用代码配置，降低复杂度。

示例：

```python
VERTICALS = {
    "nail": {
        "vertical": "nail",
        "display_name": "美甲",
        "enabled": True,
        "content_platforms": ["xhs"],
        "content_types": ["image_text_note"],
        "supported_reference_sources": ["none", "local_path", "case_id"],
        "default_page_count": 6,
        "workflow_id": "nail_note_workflow_v1",
        "case_enabled": True,
        "reference_image_enabled": True,
    }
}
```

需要提供的能力：

```text
list_verticals()
get_vertical(vertical)
validate_vertical(vertical)
is_enabled(vertical)
get_adapter(vertical)
```

验收要求：

```text
GET /api/verticals 能读取 registry；
unknown vertical 返回 4xx；
disabled vertical 不允许创建任务；
前端 selectedVertical 来自 registry 或与 registry 保持一致。
```

---

## **9.5 Vertical Adapter 实现方案**

Vertical Adapter 是平台层和具体垂类 workflow 之间的适配层。

推荐定义基础接口：

```python
class VerticalAdapter:
    vertical: str

    def create_note_job(self, request):
        ...

    def list_cases(self, filters=None):
        ...

    def get_case(self, case_id):
        ...

    def normalize_package(self, package):
        ...
```

nail adapter 负责：

```text
调用现有 NailNoteWorkflow；
处理 nail 相关 prompt/workflow 参数；
读取 nail cases；
校验 nail case；
补齐 nail package 字段；
将结果转换为通用 NotePackage。
```

MVP v1.0 中可以先做轻量 adapter，不要求复杂抽象，但必须避免 API 层直接硬编码所有 nail 逻辑。

---

## **9.6 History Service 实现方案**

History Service 负责服务端历史记录能力，是 MVP v1.0 中必须优先补齐的核心模块。

当前 v0 的历史记录如果主要依赖浏览器 localStorage，就会出现一个严重问题：用户清空缓存、换浏览器、换设备，或前端状态丢失后，过去生成的内容无法稳定找回。MVP v1.0 必须把历史记录升级为服务端能力，通过扫描 output 目录或读取持久化存储中的 `note_package.json` 来恢复历史结果。

v1.0 阶段推荐先采用 output 扫描方案，而不是立即引入数据库。这样可以降低实现成本，同时解决最关键的历史回放问题。

### **9.6.1 核心职责**

History Service 至少承担以下职责：

```text
扫描 output 目录；
查找 note_package.json；
读取 package；
提取 NoteHistoryItem；
按 vertical 过滤；
支持旧 package fallback；
跳过损坏 JSON；
记录 diagnostics；
不返回本地绝对路径；
为前端 History 模块提供稳定数据；
为 package 回放提供 note_id 索引能力。
```

History Service 不应该只服务 nail。它应该接受 `vertical` 参数，并返回对应垂类下的历史内容。

例如：

```text
GET /api/verticals/nail/notes
```

返回 nail 历史。

未来新增 outfit 后：

```text
GET /api/verticals/outfit/notes
```

应该只返回 outfit 历史，不得混入 nail 历史。

---

### **9.6.2 推荐目录兼容策略**

MVP v1.0 推荐支持两种 output 目录结构。

新结构：

```text
output/
  nail/
    nail_20260430_xxx/
      note_package.json
      page_01.png
      page_02.png
```

旧结构：

```text
output/
  nail_20260430_xxx/
    note_package.json
    page_01.png
    page_02.png
```

新结构更适合多垂类扩展，因为 vertical 在路径中显式存在。

旧结构用于兼容 v0 已生成的数据。v1.0 不应因为升级多垂类架构而导致旧结果完全不可回放。

---

### **9.6.3 扫描策略**

History Service 扫描历史记录时，推荐按以下顺序判断 vertical：

```text
优先读取 package.vertical；
如果 package.vertical 缺失，从路径推断；
如果路径无法推断，从 note_id 前缀推断，例如 nail_xxx；
如果仍无法推断，标记为 unknown 或跳过；
损坏 JSON 跳过并记录 diagnostics；
返回路径转换为相对路径或静态 URL，不返回本地绝对路径。
```

对于请求：

```text
GET /api/verticals/nail/notes
```

History Service 应只返回：

```text
vertical=nail
```

的历史记录。

如果旧 package 缺少 `vertical`，但 `note_id` 是：

```text
nail_20260430_xxx
```

则可以 fallback 推断为：

```text
vertical=nail
```

如果无法推断，建议 v1.0 有两种可选策略：

```text
策略 A：跳过 unknown 历史项；
策略 B：返回 unknown 历史项，但不混入具体 vertical 历史列表。
```

为了降低前端复杂度，MVP v1.0 更推荐策略 A：在请求具体 vertical 历史时，只返回可以明确归属该 vertical 的记录。

---

### **9.6.4 推荐实现步骤**

下面是 History Service 的伪代码示例，用于说明实现思路。

```python
def scan_history(vertical: str, limit: int = 50, offset: int = 0):
    notes = []
    output_dir = get_output_directory()

    # 1. 扫描新结构：output/{vertical}/{note_id}/note_package.json
    vertical_dir = os.path.join(output_dir, vertical)

    if os.path.exists(vertical_dir):
        for note_id in os.listdir(vertical_dir):
            package_path = os.path.join(
                vertical_dir,
                note_id,
                "note_package.json"
            )

            if not os.path.exists(package_path):
                continue

            try:
                package = read_package(package_path)
                package_vertical = infer_vertical_from_package_or_path(
                    package=package,
                    note_id=note_id,
                    package_path=package_path,
                    default_vertical=vertical,
                )

                if package_vertical != vertical:
                    continue

                normalized_package = normalize_package_for_history(
                    package=package,
                    vertical=vertical,
                    note_id=note_id,
                    package_path=package_path,
                )

                item = extract_history_item(normalized_package)
                notes.append(item)

            except Exception as e:
                log_diagnostics(
                    message=f"损坏 package，已跳过：{package_path}",
                    error=e,
                )
                continue

    # 2. 扫描旧结构：output/{note_id}/note_package.json
    for note_id in os.listdir(output_dir):
        legacy_note_dir = os.path.join(output_dir, note_id)

        # 避免把 output/{vertical}/ 当作旧 note 目录重复扫描
        if note_id in get_registered_vertical_names():
            continue

        package_path = os.path.join(
            legacy_note_dir,
            "note_package.json"
        )

        if not os.path.exists(package_path):
            continue

        try:
            package = read_package(package_path)

            inferred_vertical = infer_vertical(
                package=package,
                note_id=note_id,
                package_path=package_path,
            )

            if inferred_vertical != vertical:
                continue

            normalized_package = normalize_package_for_history(
                package=package,
                vertical=inferred_vertical,
                note_id=note_id,
                package_path=package_path,
            )

            item = extract_history_item(normalized_package)
            notes.append(item)

        except Exception as e:
            log_diagnostics(
                message=f"损坏旧 package，已跳过：{package_path}",
                error=e,
            )
            continue

    # 3. 去重
    notes = deduplicate_history_items(notes)

    # 4. 按 created_at 倒序排序
    notes.sort(
        key=lambda item: item.get("created_at") or "",
        reverse=True,
    )

    # 5. 分页
    return notes[offset:offset + limit]
```

---

### **9.6.5 History Item 提取规则**

从 `note_package.json` 提取历史列表项时，不应把完整 package 原样返回给列表接口。历史列表只需要摘要字段。

推荐提取为：

```json
{
  "note_id": "nail_20260430_xxx",
  "content_platform": "xhs",
  "content_type": "image_text_note",
  "vertical": "nail",
  "scenario": "summer_cat_eye",
  "created_at": "2026-04-30T09:09:13",
  "brief": "夏日短甲猫眼美甲",
  "selected_title": "短甲猫眼真的太适合夏天了",
  "status": "succeeded",
  "reference_source": "local_path",
  "page_count": 6,
  "generated_image_count": 6,
  "qa_score": 0.86
}
```

提取时的 fallback 规则建议如下：

```text
note_id：
  优先使用 package.note_id；
  缺失时使用目录名。

vertical：
  优先使用 package.vertical；
  缺失时从路径推断；
  再缺失时从 note_id 前缀推断。

created_at：
  优先使用 package.created_at；
  缺失时使用 note_package.json 文件修改时间。

brief：
  优先使用 package.request.brief；
  缺失时使用空字符串。

selected_title：
  优先使用 package.result.selected_title；
  缺失时使用 package.selected_title；
  再缺失时使用空字符串。

reference_source：
  优先使用 package.request.reference_source；
  缺失时默认为 none 或 unknown。

page_count：
  使用 result.pages 长度；
  缺失时为 0。

generated_image_count：
  统计 pages 中存在 image_url 的页面数量；
  图片文件缺失时可仍计入 URL 数，也可单独记录 missing_assets。

qa_score：
  优先使用 package.diagnostics.qa_score；
  或 package.qa_score；
  缺失时为 null。
```

---

### **9.6.6 路径与资源安全**

History Service 必须保证返回给前端的内容不包含本机绝对路径。

不得返回：

```text
/Users/xxx/project/output/...
/home/xxx/project/output/...
C:\Users\xxx\project\output\...
```

应返回：

```text
/static/output/nail/nail_20260430_xxx/page_01.png
```

或 API 路径：

```text
/api/verticals/nail/notes/nail_20260430_xxx/package
```

History Service 在读取文件时必须限制扫描范围，不能允许路径穿越。

必须拒绝：

```text
../
..\
%2e%2e
```

以及其他试图访问 output/input 之外路径的情况。

---

### **9.6.7 损坏 package 处理**

历史扫描不能因为单个损坏 package 导致整个接口返回 500。

例如 output 中存在：

```text
output/nail/nail_bad_001/note_package.json
```

但该 JSON 内容损坏，History Service 应该：

```text
跳过该项；
记录 diagnostics 或日志；
继续扫描其他 package；
最终接口仍返回 200；
notes 中只包含有效记录。
```

如果系统提供 diagnostics，可以在服务端日志中记录：

```text
损坏 package 路径；
错误类型；
错误时间；
是否已跳过。
```

但返回给前端时不应暴露服务器绝对路径。

---

### **9.6.8 API 对接**

History Service 对应 API：

```text
GET /api/verticals/{vertical}/notes
```

请求示例：

```text
GET /api/verticals/nail/notes?limit=50&offset=0
```

响应示例：

```json
{
  "notes": [
    {
      "note_id": "nail_20260430_xxx",
      "content_platform": "xhs",
      "content_type": "image_text_note",
      "vertical": "nail",
      "scenario": "summer_cat_eye",
      "created_at": "2026-04-30T09:09:13",
      "brief": "夏日短甲猫眼美甲",
      "selected_title": "短甲猫眼真的太适合夏天了",
      "status": "succeeded",
      "reference_source": "local_path",
      "page_count": 6,
      "generated_image_count": 6,
      "qa_score": 0.86
    }
  ]
}
```

当没有历史记录时，应返回：

```json
{
  "notes": []
}
```

而不是返回 404 或 500。

---

### **9.6.9 验收要求**

History Service 必须通过以下验收：

```text
output 为空时返回空数组，不返回 500；
单个损坏 package 不导致整个接口失败；
返回历史项包含 vertical 字段；
旧 package 可以 fallback 推断 vertical；
无法推断 vertical 的 package 不混入 nail 历史；
返回路径不含本地绝对路径；
历史列表按请求 vertical 过滤；
localStorage 清空后，前端仍可通过该接口加载历史记录；
点击历史项后可以进入 package 回放流程。
```

---

## **9.7 Case Service 实现方案**

Case Service 负责案例库管理，是把 `case_id` 从隐藏参数升级为产品能力的关键模块。

在 v0 中，如果系统已经支持 `case_id` 参数，但用户只能手动输入或通过开发者方式传入，那么这不能算完整的案例复用功能。MVP v1.0 必须提供案例列表接口和前端案例选择入口。

### **9.7.1 核心职责**

Case Service 至少承担以下职责：

```text
读取当前 vertical 下的案例；
支持按 keyword/style_tag/scenario 过滤；
返回 CaseItem 列表；
支持获取单个案例详情；
校验 case.vertical 与请求 vertical 一致；
创建任务时校验 case_id；
不返回本地绝对路径；
支持从历史 note 保存为案例，Should Have。
```

Case Service 也不应写死 nail。nail 只是 v1.0 必须真实落地的首个 vertical。

---

### **9.7.2 案例来源**

MVP v1.0 案例可以来自以下来源：

```text
预置 case seed 数据，推荐；
从历史优质 note 手动标记，Should Have；
从 output 扫描已有 package 提取，可选；
后续可扩展为数据库存储。
```

v1.0 推荐先用 JSON 配置或 Python 配置实现预置案例，降低复杂度。

示例目录：

```text
verticals/
  nail/
    cases/
      nail_cases.json
```

示例 case：

```json
{
  "case_id": "case_nail_summer_cat_eye_001",
  "content_platform": "xhs",
  "content_type": "image_text_note",
  "vertical": "nail",
  "scenario": "summer_cat_eye",
  "title": "夏日短甲猫眼案例",
  "style_tags": ["短甲", "猫眼", "夏日"],
  "source_note_id": "nail_20260430_xxx",
  "qa_score": 0.91,
  "preview_image_url": "/static/output/nail/nail_20260430_xxx/page_01.png"
}
```

---

### **9.7.3 推荐实现**

```python
def list_cases(vertical: str, filters=None):
    validate_vertical(vertical)

    cases = []

    # 1. 从配置读取预置案例
    preset_cases = load_preset_cases(vertical)
    cases.extend(preset_cases)

    # 2. 可选：从历史优质 note 中提取案例
    if filters and filters.get("include_history"):
        history_cases = scan_history_for_cases(vertical, filters)
        cases.extend(history_cases)

    # 3. 只保留当前 vertical 的案例
    cases = [
        case for case in cases
        if case.get("vertical") == vertical
    ]

    # 4. keyword 过滤
    if filters and filters.get("keyword"):
        keyword = filters["keyword"]
        cases = [
            case for case in cases
            if keyword in case.get("title", "")
            or keyword in " ".join(case.get("style_tags", []))
        ]

    # 5. style_tag 过滤
    if filters and filters.get("style_tag"):
        style_tag = filters["style_tag"]
        cases = [
            case for case in cases
            if style_tag in case.get("style_tags", [])
        ]

    # 6. scenario 过滤
    if filters and filters.get("scenario"):
        scenario = filters["scenario"]
        cases = [
            case for case in cases
            if case.get("scenario") == scenario
        ]

    # 7. 路径清洗
    cases = [
        sanitize_case_item(case)
        for case in cases
    ]

    return cases


def get_case(vertical: str, case_id: str):
    validate_vertical(vertical)
    validate_case_id(case_id)

    case = load_case_by_id(case_id)

    if case is None:
        raise CaseNotFound(f"Case {case_id} not found")

    if case.get("vertical") != vertical:
        raise CaseVerticalMismatch(
            f"Case {case_id} belongs to {case.get('vertical')}, not {vertical}"
        )

    return sanitize_case_item(case)
```

---

### **9.7.4 创建任务时的 case 校验**

当用户使用案例复用模式时，请求中会包含：

```json
{
  "reference_source": "case_id",
  "case_id": "case_nail_summer_cat_eye_001"
}
```

后端必须校验：

```text
case_id 存在；
case_id 格式合法；
case.vertical == request vertical；
case.content_platform 支持当前 content_platform；
case.content_type 支持当前 content_type；
case 未被禁用；
case 不指向非法资源路径。
```

如果 case 属于其他 vertical，必须拒绝，不得静默使用。

例如：

```text
POST /api/verticals/nail/notes
```

传入：

```text
case_id=case_outfit_xxx
```

必须返回 4xx。

---

### **9.7.5 API 对接**

Case Service 对应 API：

```text
GET /api/verticals/{vertical}/cases
```

请求示例：

```text
GET /api/verticals/nail/cases
```

可选参数：

```text
keyword
style_tag
scenario
```

响应示例：

```json
{
  "cases": [
    {
      "case_id": "case_nail_summer_cat_eye_001",
      "content_platform": "xhs",
      "content_type": "image_text_note",
      "vertical": "nail",
      "scenario": "summer_cat_eye",
      "title": "夏日短甲猫眼案例",
      "style_tags": ["短甲", "猫眼", "夏日"],
      "source_note_id": "nail_20260430_xxx",
      "qa_score": 0.91,
      "preview_image_url": "/static/output/nail/nail_20260430_xxx/page_01.png"
    }
  ]
}
```

无案例时返回：

```json
{
  "cases": []
}
```

---

### **9.7.6 验收要求**

Case Service 必须通过以下验收：

```text
GET /api/verticals/nail/cases 返回 nail 案例；
case item 包含 case_id 和 vertical；
不返回其他 vertical 的案例；
无案例时返回空数组；
case.vertical 与请求 vertical 不一致时拒绝使用；
preview_image_url 不含本地绝对路径；
前端可以展示案例列表；
点击案例后可以回填 Studio；
case_id 模式提交任务时 payload 正确。
```

---

## **9.8 Package Service 实现方案**

Package Service 负责读取、校验、补齐和返回 `note_package.json`，是历史回放和内容预览的基础。

如果 History Service 负责“找到有哪些历史记录”，那么 Package Service 负责“打开某一条历史记录并恢复完整内容”。

### **9.8.1 核心职责**

Package Service 至少承担以下职责：

```text
根据 vertical 和 note_id 查找 note_package.json；
读取 package；
验证 package 结构；
补齐缺失字段；
验证 vertical 匹配；
转换本地路径为静态 URL；
处理损坏 JSON；
处理图片缺失；
返回可被 Preview 渲染的 NotePackage；
不返回本地绝对路径。
```

---

### **9.8.2 查找策略**

Package Service 应兼容新旧两种目录结构。

优先查找新结构：

```text
output/{vertical}/{note_id}/note_package.json
```

如果不存在，再查找旧结构：

```text
output/{note_id}/note_package.json
```

查找到后仍必须验证：

```text
路径在 output 目录内；
note_id 不包含路径穿越；
package.vertical 与请求 vertical 一致；
如果 package.vertical 缺失，可以 fallback 推断；
如果推断结果与请求 vertical 不一致，返回 4xx。
```

---

### **9.8.3 推荐实现**

```python
def get_package(vertical: str, note_id: str):
    validate_vertical(vertical)
    validate_note_id(note_id)

    package_path = find_package_path(
        vertical=vertical,
        note_id=note_id,
    )

    if package_path is None:
        raise PackageNotFound(
            f"Package for note_id={note_id} not found"
        )

    if not is_path_allowed(package_path):
        raise PathNotAllowed(
            f"Package path not allowed"
        )

    try:
        package = read_json(package_path)
    except Exception as e:
        raise PackageInvalid(
            f"Package JSON invalid: {e}"
        )

    package = normalize_package(
        package=package,
        vertical=vertical,
        note_id=note_id,
        package_path=package_path,
    )

    if package.get("vertical") != vertical:
        raise VerticalMismatch(
            f"Package vertical {package.get('vertical')} != request {vertical}"
        )

    package = sanitize_package_paths(package)

    return package
```

---

### **9.8.4 normalize_package 规则**

旧 package 可能缺少字段，因此 v1.0 需要提供 fallback。

推荐补齐规则：

```text
note_id：
  缺失时使用请求 note_id。

vertical：
  缺失时使用请求 vertical，并记录 inferred_fields。

content_platform：
  缺失时默认为 xhs。

content_type：
  缺失时默认为 image_text_note。

created_at：
  缺失时使用文件 mtime。

status：
  缺失时默认为 succeeded 或 restored。

request：
  缺失时补为空对象。

request.brief：
  缺失时补为空字符串。

request.reference_source：
  缺失时补为 unknown 或 none。

result：
  缺失时补为空对象。

result.selected_title：
  缺失时从旧字段 selected_title 推断；
  再缺失时为空字符串。

result.caption：
  缺失时从 body 或 caption 旧字段推断；
  再缺失时为空字符串。

result.tags：
  缺失时为空数组。

result.pages：
  缺失时为空数组。

diagnostics：
  缺失时补为空对象。

diagnostics.inferred_fields：
  记录所有 fallback 补齐字段。
```

示例：

```python
def normalize_package(package, vertical, note_id, package_path):
    inferred_fields = []

    if "note_id" not in package:
        package["note_id"] = note_id
        inferred_fields.append("note_id")

    if "vertical" not in package:
        package["vertical"] = vertical
        inferred_fields.append("vertical")

    if "content_platform" not in package:
        package["content_platform"] = "xhs"
        inferred_fields.append("content_platform")

    if "content_type" not in package:
        package["content_type"] = "image_text_note"
        inferred_fields.append("content_type")

    if "created_at" not in package:
        package["created_at"] = get_file_mtime_iso(package_path)
        inferred_fields.append("created_at")

    if "status" not in package:
        package["status"] = "restored"
        inferred_fields.append("status")

    package.setdefault("request", {})
    package.setdefault("result", {})
    package.setdefault("diagnostics", {})

    package["request"].setdefault("brief", "")
    package["request"].setdefault("reference_source", "unknown")
    package["request"].setdefault("generate_images", None)
    package["request"].setdefault("reference_image_path", None)
    package["request"].setdefault("case_id", None)
    package["request"].setdefault("options", {})

    result = package["result"]

    if "selected_title" not in result:
        result["selected_title"] = package.get("selected_title", "")
        inferred_fields.append("result.selected_title")

    if "caption" not in result:
        result["caption"] = package.get("caption") or package.get("body") or ""
        inferred_fields.append("result.caption")

    if "tags" not in result:
        result["tags"] = package.get("tags", [])
        inferred_fields.append("result.tags")

    if "pages" not in result:
        result["pages"] = package.get("pages", [])
        inferred_fields.append("result.pages")

    diagnostics = package["diagnostics"]
    existing = diagnostics.get("inferred_fields", [])
    diagnostics["inferred_fields"] = list(set(existing + inferred_fields))

    return package
```

---

### **9.8.5 图片缺失处理**

Package Service 不应因为图片文件缺失而拒绝返回 package。

例如页面中存在：

```json
{
  "image_url": "/static/output/nail/nail_20260430_xxx/page_01.png"
}
```

但实际文件已经不存在，Package Service 可以：

```text
仍返回 package；
在 diagnostics.missing_assets 中记录缺失图片；
前端 Preview 显示图片缺失状态；
文本内容仍然正常展示。
```

推荐 diagnostics：

```json
{
  "missing_assets": [
    "/static/output/nail/nail_20260430_xxx/page_01.png"
  ]
}
```

---

### **9.8.6 API 对接**

Package Service 对应 API：

```text
GET /api/verticals/{vertical}/notes/{note_id}/package
```

请求示例：

```text
GET /api/verticals/nail/notes/nail_20260430_xxx/package
```

成功时返回 `NotePackage`。

失败时返回结构化错误：

```json
{
  "error_code": "PACKAGE_NOT_FOUND",
  "message": "Package not found"
}
```

或：

```json
{
  "error_code": "PACKAGE_INVALID",
  "message": "Package JSON invalid"
}
```

---

### **9.8.7 验收要求**

Package Service 必须通过以下验收：

```text
有效 note_id 返回 package；
note_id 不存在返回 404；
note_id 包含 .. 时被拒绝；
vertical 不匹配返回 4xx；
package 损坏返回结构化错误；
图片缺失不影响文本回放；
返回 package 中包含或补齐 vertical；
返回 package 中不包含本地绝对路径；
旧 package 可以 fallback 补齐 content_platform、content_type、vertical；
Preview 可以直接使用返回 package 渲染。
```

---

## **9.9 前端实现方案**

MVP v1.0 的前端可以继续使用轻量静态 Web 页面，不强制引入 React、Vue 或复杂状态管理框架。

但前端必须从“nail 单垂类页面”升级为“带 selectedVertical 上下文的 Vertical Content Studio”。

---

### **9.9.1 页面结构**

MVP v1.0 推荐页面包含以下核心区域：

```text
顶部：Vertical Context
左侧：Studio 生成工作台
中间：Progress + Preview
右侧：History + Cases
```

也可以采用 Tab 结构：

```text
顶部：Vertical Context
Tab 1：生成工作台
Tab 2：历史记录
Tab 3：案例库
Tab 4：当前任务与预览
```

v1.0 不强制具体布局，但必须保证以下模块有明确入口：

```text
Vertical Context；
Studio；
Progress；
Preview；
History；
Cases；
Upload。
```

---

### **9.9.2 Vertical Context**

页面顶部应明确展示当前上下文：

```text
平台：小红书 xhs
内容形态：图文笔记 image_text_note
当前垂类：美甲 nail
```

即使 v1.0 只有 nail 一个真实垂类，也应该保留 `selectedVertical` 状态。

推荐状态：

```javascript
const state = {
  verticalList: [],
  selectedVertical: "nail",
  selectedScenario: null,
  selectedReferenceSource: "none",
  selectedCase: null,
  currentJob: null,
  currentNotePackage: null,
  historyList: [],
  caseList: [],
  uploadState: null,
  errorState: null
};
```

---

### **9.9.3 前端状态联动**

状态联动规则：

```text
selectedVertical 初始化后：
  加载 vertical 配置；
  加载当前 vertical 的历史；
  加载当前 vertical 的案例。

selectedVertical 变化后：
  刷新 History；
  刷新 Cases；
  清空 selectedCase；
  重置 selectedReferenceSource 为 none；
  校验 currentNotePackage 是否属于当前 vertical；
  更新 API path；
  更新页面上下文展示。

selectedReferenceSource 变化后：
  none 模式：清空 reference_image_path 和 case_id；
  local_path 模式：清空 case_id，显示上传区域；
  case_id 模式：清空 reference_image_path，显示案例选择状态。

selectedCase 变化后：
  自动设置 selectedReferenceSource=case_id；
  自动带入 case_id；
  在 Studio 中显示已选案例。

currentJob 变化后：
  更新 Progress；
  开始或停止轮询。

currentNotePackage 变化后：
  使用统一 Preview 渲染逻辑展示结果。
```

---

### **9.9.4 API 调用**

前端 API 调用应从硬编码 nail 升级为使用 `selectedVertical`。

旧写法：

```javascript
fetch("/api/nail/notes", {
  method: "POST",
  body: JSON.stringify(payload)
});
```

新写法：

```javascript
const vertical = encodeURIComponent(state.selectedVertical);

fetch("/api/verticals/" + vertical + "/notes", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify(payload)
});

```

历史记录：

```javascript
const vertical = encodeURIComponent(state.selectedVertical);

fetch("/api/verticals/" + vertical + "/notes");
```

案例库：

```javascript
const vertical = encodeURIComponent(state.selectedVertical);

fetch("/api/verticals/" + vertical + "/cases");

```

Package 回放：

```javascript
const vertical = encodeURIComponent(state.selectedVertical);
const encodedNoteId = encodeURIComponent(noteId);

fetch(
  "/api/verticals/"
    + vertical
    + "/notes/"
    + encodedNoteId
    + "/package"
);

```

参考图上传：

```javascript
const vertical = encodeURIComponent(state.selectedVertical);

const formData = new FormData();
formData.append("file", file);

fetch("/api/verticals/" + vertical + "/reference-images", {
  method: "POST",
  body: formData
});

```

任务状态：

```javascript
const encodedJobId = encodeURIComponent(jobId);

fetch("/api/jobs/" + encodedJobId);

```

如果需要兼容旧接口，前端可以短期保留 fallback，但主路径必须使用：

```text
/api/verticals/{vertical}/...
```

---

### **9.9.5 生成任务 payload 构造**

前端应根据 `selectedReferenceSource` 构造互斥 payload。

基础生成：

```javascript
const payload = {
  content_platform: "xhs",
  content_type: "image_text_note",
  scenario: state.selectedScenario,
  brief,
  generate_images: true,
  reference_source: "none",
  reference_image_path: null,
  case_id: null,
  options: {}
};
```

参考图生成：

```javascript
const payload = {
  content_platform: "xhs",
  content_type: "image_text_note",
  scenario: state.selectedScenario,
  brief,
  generate_images: true,
  reference_source: "local_path",
  reference_image_path: state.uploadState.reference_image_path,
  case_id: null,
  options: {}
};
```

案例复用：

```javascript
const payload = {
  content_platform: "xhs",
  content_type: "image_text_note",
  scenario: state.selectedScenario,
  brief,
  generate_images: true,
  reference_source: "case_id",
  reference_image_path: null,
  case_id: state.selectedCase.case_id,
  options: {}
};
```

前端必须在提交前校验：

```text
brief 不能为空；
local_path 模式必须有 reference_image_path；
case_id 模式必须有 selectedCase 或 case_id；
none 模式不得带 reference_image_path；
none 模式不得带 case_id；
local_path 模式不得带 case_id；
case_id 模式不得带 reference_image_path。
```

后端仍必须重复校验，不能只依赖前端。

---

### **9.9.6 安全渲染**

前端必须避免用 `innerHTML` 拼接用户可控内容。

不推荐：

```javascript
item.innerHTML = `<div>${note.selected_title}</div>`;
```

推荐：

```javascript
const title = document.createElement("div");
title.textContent = note.selected_title || "未命名内容";
item.appendChild(title);
```

历史记录、案例库、内容预览、错误提示中都应使用：

```text
createElement；
appendChild；
textContent；
createTextNode；
setAttribute，但仅用于经过校验的属性。
```

图片 URL 设置前应做基础校验：

```javascript
function isSafeStaticUrl(url) {
  if (!url || typeof url !== "string") return false;
  return url.startsWith("/static/output/")
    || url.startsWith("/static/input/");
}
```

设置图片：

```javascript
if (isSafeStaticUrl(page.image_url)) {
  const img = document.createElement("img");
  img.src = page.image_url;
  img.alt = page.title || "生成图片";
  container.appendChild(img);
} else {
  const missing = document.createElement("div");
  missing.textContent = "图片缺失或路径不可用";
  container.appendChild(missing);
}
```

---

### **9.9.7 Preview 统一渲染**

实时任务成功后的结果和历史 package 回放结果必须使用同一套 Preview 渲染逻辑。

推荐函数：

```javascript
function renderPreview(notePackage, options = {}) {
  clearPreview();

  if (!notePackage) {
    renderPreviewEmptyState();
    return;
  }

  renderPreviewMeta(notePackage);
  renderPreviewTitle(notePackage.result);
  renderPreviewCaption(notePackage.result);
  renderPreviewTags(notePackage.result);
  renderPreviewPages(notePackage.result);
  renderPreviewDiagnostics(notePackage.diagnostics);

  if (options.restoredFromHistory) {
    renderRestoreBadge("已从历史记录恢复");
  }
}
```

这样可以避免出现：

```text
实时生成一个样式；
历史回放另一个样式；
字段 fallback 不一致；
复制按钮只在某个路径可用。
```

---

### **9.9.8 Progress 轮询**

创建任务成功后，前端应进入 Progress 状态，并通过 `job_id` 轮询任务状态接口。

推荐流程如下：

```javascript
async function pollJob(jobId) {
  const response = await fetch("/api/jobs/" + encodeURIComponent(jobId));

  if (!response.ok) {
    renderJobError("任务状态查询失败");
    return;
  }

  const job = await response.json();

  state.currentJob = job;
  renderProgress(job);

  if (job.status === "queued" || job.status === "running") {
    setTimeout(function () {
      pollJob(jobId);
    }, 2000);
    return;
  }

  if (job.status === "succeeded") {
    if (job.result || job.package) {
      state.currentNotePackage = job.result || job.package;
      renderPreview(state.currentNotePackage);
      loadHistory();
      return;
    }

    if (job.note_id) {
      await loadPackageFromHistory(job.note_id, {
        restoredFromHistory: false
      });
      loadHistory();
      return;
    }

    renderJobError("任务已成功，但未返回可预览结果");
    return;
  }

  if (job.status === "partial_failed") {
    if (job.result || job.package) {
      state.currentNotePackage = job.result || job.package;
      renderPreview(state.currentNotePackage, {
        partialFailed: true
      });
    }

    renderJobWarning(job.error_message || "任务部分失败，请查看诊断信息");
    loadHistory();
    return;
  }

  if (job.status === "failed") {
    renderJobError(job.error_message || "任务失败");
    return;
  }

  renderJobError("未知任务状态：" + String(job.status || ""));
}
```

这里有几个关键要求。

首先，`queued` 和 `running` 状态应继续轮询；`succeeded` 状态应进入 Preview；`failed` 状态应展示错误；`partial_failed` 状态不能简单当成失败处理，而应尽可能展示已成功生成的文本、页面或图片，并明确告诉用户哪些部分失败。

其次，任务成功后前端不应只依赖轮询接口返回完整 package。更稳妥的方式是：如果 job status 返回了 `note_id`，前端可以继续调用 package 接口获取最终标准化结果。这样可以确保实时预览和历史回放使用同一份 `note_package.json` 数据。

推荐的 package fallback 逻辑如下：

```javascript
async function loadPackageFromHistory(noteId, options) {
  const vertical = state.selectedVertical || "nail";

  const response = await fetch(
    "/api/verticals/"
      + encodeURIComponent(vertical)
      + "/notes/"
      + encodeURIComponent(noteId)
      + "/package"
  );

  if (!response.ok) {
    renderJobError("结果回放失败，无法读取 note package");
    return;
  }

  const notePackage = await response.json();

  state.currentNotePackage = notePackage;

  renderPreview(notePackage, {
    restoredFromHistory: Boolean(options && options.restoredFromHistory)
  });
}
```

Progress 模块至少应展示：

```text
job_id；
status；
stage；
elapsed_seconds；
note_id，如有；
error_code，如有；
error_message，如有；
error_stage，如有。
```

推荐展示文案：

```text
queued：任务已进入队列
running：正在生成，当前阶段：xxx，已耗时 xx 秒
succeeded：生成完成
partial_failed：部分生成成功，部分内容失败
failed：生成失败，失败阶段：xxx
```

前端不应把所有非 succeeded 状态都展示为“失败”。长任务的用户体验重点是可观察性，用户需要知道任务当前在做什么、是否仍在运行、失败发生在哪个阶段。

---

### **9.9.9 History 模块**

History 模块负责展示服务端历史记录。

页面初始化时应调用：

```javascript
async function loadHistory() {
  const vertical = state.selectedVertical || "nail";

  const response = await fetch(
    "/api/verticals/"
      + encodeURIComponent(vertical)
      + "/notes"
  );

  if (!response.ok) {
    renderHistoryError("历史记录加载失败");
    return;
  }

  const data = await response.json();

  state.historyList = Array.isArray(data.notes) ? data.notes : [];

  renderHistory(state.historyList);
}
```

渲染历史记录时必须使用安全 DOM API：

```javascript
function renderHistory(notes) {
  const container = document.getElementById("history-list");
  clearElement(container);

  if (!notes.length) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.textContent = "暂无历史记录";
    container.appendChild(empty);
    return;
  }

  notes.forEach(function (note) {
    const item = document.createElement("button");
    item.type = "button";
    item.className = "history-item";

    const title = document.createElement("div");
    title.className = "history-title";
    title.textContent = note.selected_title || "未命名内容";

    const meta = document.createElement("div");
    meta.className = "history-meta";
    meta.textContent = [
      note.vertical || "unknown",
      note.reference_source || "unknown",
      note.created_at || ""
    ].join(" · ");

    item.appendChild(title);
    item.appendChild(meta);

    item.addEventListener("click", function () {
      loadPackageFromHistory(note.note_id, {
        restoredFromHistory: true
      });
    });

    container.appendChild(item);
  });
}
```

History 模块的核心验收点不是“前端有一份历史数组”，而是：

```text
localStorage 清空后仍可加载历史；
历史来自服务端接口；
历史按 selectedVertical 过滤；
点击历史项可以恢复完整 package；
恢复后的 Preview 与实时生成后的 Preview 一致；
损坏 package 不导致整个历史接口失败；
历史为空时有明确空状态。
```

---

### **9.9.10 Cases 模块**

Cases 模块负责展示当前 vertical 下的案例库，并支持用户选择案例进入案例复用模式。

页面初始化或 `selectedVertical` 变化时应调用：

```javascript
async function loadCases() {
  const vertical = state.selectedVertical || "nail";

  const response = await fetch(
    "/api/verticals/"
      + encodeURIComponent(vertical)
      + "/cases"
  );

  if (!response.ok) {
    renderCasesError("案例库加载失败");
    return;
  }

  const data = await response.json();

  state.caseList = Array.isArray(data.cases) ? data.cases : [];

  renderCases(state.caseList);
}
```

案例渲染也必须避免 `innerHTML`：

```javascript
function renderCases(cases) {
  const container = document.getElementById("case-list");
  clearElement(container);

  if (!cases.length) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.textContent = "暂无可用案例";
    container.appendChild(empty);
    return;
  }

  cases.forEach(function (caseItem) {
    const item = document.createElement("button");
    item.type = "button";
    item.className = "case-item";

    const title = document.createElement("div");
    title.className = "case-title";
    title.textContent = caseItem.title || "未命名案例";

    const tags = document.createElement("div");
    tags.className = "case-tags";
    tags.textContent = Array.isArray(caseItem.style_tags)
      ? caseItem.style_tags.join(" / ")
      : "";

    item.appendChild(title);
    item.appendChild(tags);

    item.addEventListener("click", function () {
      selectCase(caseItem);
    });

    container.appendChild(item);
  });
}
```

选择案例后，应回填 Studio 状态：

```javascript
function selectCase(caseItem) {
  if (!caseItem || !caseItem.case_id) {
    renderCasesError("案例数据无效");
    return;
  }

  state.selectedCase = caseItem;
  state.selectedReferenceSource = "case_id";

  updateReferenceSourceUI();
  renderSelectedCase(caseItem);
}
```

案例复用不能停留在“用户手动输入 case_id”的阶段。MVP v1.0 必须至少提供可点击选择的案例列表，使用户可以从案例库进入生成流程。

---

### **9.9.11 Upload 模块**

参考图生成模式需要 Upload 模块。

上传接口建议为：

```text
POST /api/verticals/{vertical}/reference-images
```

前端上传示例：

```javascript
async function uploadReferenceImage(file) {
  if (!file) {
    renderUploadError("请选择参考图");
    return;
  }

  if (!isAllowedImageFile(file)) {
    renderUploadError("文件格式不支持");
    return;
  }

  const vertical = state.selectedVertical || "nail";
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(
    "/api/verticals/"
      + encodeURIComponent(vertical)
      + "/reference-images",
    {
      method: "POST",
      body: formData
    }
  );

  if (!response.ok) {
    renderUploadError("参考图上传失败");
    return;
  }

  const data = await response.json();

  state.uploadState = {
    reference_image_path: data.reference_image_path,
    preview_url: data.preview_url || data.reference_image_path
  };

  renderUploadSuccess(state.uploadState);
}
```

基础文件校验示例：

```javascript
function isAllowedImageFile(file) {
  const allowedTypes = [
    "image/png",
    "image/jpeg",
    "image/webp"
  ];

  return allowedTypes.indexOf(file.type) >= 0;
}
```

前端校验不能替代后端校验。后端仍必须检查：

```text
文件后缀；
MIME；
文件大小；
保存路径；
是否在允许目录内；
返回路径是否为静态 URL 或安全相对路径。
```

---

### **9.9.12 复制能力**

Preview 模块应支持复制核心内容。

至少包括：

```text
复制标题；
复制正文；
复制标签；
复制全部文案。
```

示例：

```javascript
async function copyText(text, successMessage) {
  try {
    await navigator.clipboard.writeText(text || "");
    renderToast(successMessage || "复制成功");
  } catch (error) {
    renderToast("复制失败，请手动选择文本复制");
  }
}
```

复制全部文案时可以组合：

```javascript
function buildFullCopyText(notePackage) {
  const result = notePackage.result || {};
  const title = result.selected_title || "";
  const caption = result.caption || "";
  const tags = Array.isArray(result.tags)
    ? result.tags.map(function (tag) {
        return String(tag).startsWith("#") ? String(tag) : "#" + String(tag);
      }).join(" ")
    : "";

  return [title, caption, tags].filter(Boolean).join("\n\n");
}
```

复制按钮的目标是让生成结果能直接进入内容生产流程，而不是只作为展示结果存在。

---

### **9.9.13 前端通用工具函数**

为了降低字段缺失导致页面崩溃的风险，前端应提供通用安全函数。

例如清空节点：

```javascript
function clearElement(element) {
  while (element && element.firstChild) {
    element.removeChild(element.firstChild);
  }
}
```

安全读取数组：

```javascript
function asArray(value) {
  return Array.isArray(value) ? value : [];
}
```

安全字符串：

```javascript
function safeText(value, fallback) {
  if (value === null || value === undefined) {
    return fallback || "";
  }

  return String(value);
}
```

安全静态 URL：

```javascript
function isSafeStaticUrl(url) {
  if (!url || typeof url !== "string") {
    return false;
  }

  return url.indexOf("/static/output/") === 0
    || url.indexOf("/static/input/") === 0;
}
```

这些工具函数可以减少分散在各个渲染函数里的重复判断，也能避免某个字段缺失导致整个页面 JS 中断。

---

### **9.9.14 前端验收要求**

前端必须通过以下验收：

```text
页面加载无报错；
页面展示当前平台、内容形态、垂类；
用户可以在 Studio 创建任务；
用户可以选择基础生成、参考图生成、案例复用三种模式；
三种模式切换不会残留非法参数；
用户可以上传参考图；
用户可以看到任务进度；
任务成功后可以看到内容预览；
partial_failed 可以展示成功部分和失败提示；
用户可以复制标题、正文、标签和全部文案；
用户可以看到服务端历史记录；
用户可以点击历史记录恢复 package；
localStorage 清空后历史记录仍可加载；
用户可以看到案例库；
用户可以选择案例并回填生成任务；
案例复用 payload 正确携带 case_id；
页面不通过 innerHTML 渲染用户可控内容；
页面不把平台能力全部写死为 nail；
selectedVertical 变化后 History 和 Cases 会刷新。
```

---

## **9.10 是否引入数据库**

MVP v1.0 默认不强制引入数据库。

原因是 v1.0 的核心目标不是搭建完整数据平台，而是补齐产品闭环：

```text
服务端历史；
package 回放；
三种生成模式；
案例库入口；
任务进度；
内容预览；
vertical 概念贯通；
验收机制闭环。
```

在这个阶段，如果过早引入数据库，可能会增加迁移、建模、运维和一致性成本，反而影响核心功能交付。

### **9.10.1 v1.0 推荐方案**

v1.0 推荐使用以下轻量方案：

```text
历史记录：扫描 output 中的 note_package.json；
案例库：JSON 配置或从 output 扫描；
任务状态：内存或简单文件存储；
垂类注册：代码配置或 JSON 配置；
静态资源：通过受控 static path 暴露。
```

这种方案的优点是：

```text
实现成本低；
便于兼容旧 output；
便于快速验证产品流程；
不影响后续数据库迁移；
适合单机 MVP。
```

---

### **9.10.2 引入数据库的条件**

只有当以下问题真实出现时，才建议引入 SQLite 或其他数据库：

```text
output package 数量达到数千级，扫描性能不可接受；
需要复杂搜索、分页、排序和过滤；
需要记录生成失败但未产生 package 的任务；
需要多用户隔离；
需要长期稳定归档；
需要强一致状态管理；
需要跨服务共享数据；
需要案例库编辑、审核、上下架流程；
需要任务状态在服务重启后可靠恢复。
```

如果只是为了实现 v1.0 的历史列表和案例库，数据库不是必须条件。

---

### **9.10.3 数据库引入策略**

如果后续引入数据库，应保持外部接口稳定。

也就是说：

```text
History Service 接口不变；
Case Service 接口不变；
Vertical Registry 接口不变；
Package Service 接口不变。
```

内部实现可以从：

```text
扫描 output；
读取 JSON；
内存任务状态；
```

逐步替换为：

```text
查询 SQLite；
查询任务表；
查询案例表；
查询资源表。
```

前端和 API 合约不应因为内部存储变化而大幅改动。

推荐迁移方向：

```text
v1.0：output 扫描 + JSON 配置；
v1.1：增加扫描缓存或轻量索引；
v1.2：引入 SQLite 存储历史和案例；
v2.0：多用户、多垂类、多内容形态统一存储。
```

---

## **9.11 技术债务与后续优化**

MVP v1.0 允许部分技术债务存在，但必须明确记录，不能被误认为最终架构。

### **9.11.1 v1.0 允许的技术债务**

v1.0 可以接受以下技术债务：

```text
旧 /api/nail/... 接口保留为兼容层；
output 扫描性能未深度优化；
案例库先用 JSON 配置；
任务状态可以先用内存或轻量文件存储；
错误响应格式可能未完全统一；
部分字段 fallback 逻辑较简单；
前端状态管理采用轻量原生 JS；
未引入完整端到端自动化测试框架；
从历史 note 一键保存为案例可以作为 Should Have 或 v1.1。
```

这些技术债务可以存在，但必须记录在验收报告中。

---

### **9.11.2 v1.1 建议优化**

v1.1 建议优化方向：

```text
统一错误响应格式：error_code + message + details；
引入 SQLite 存储历史、案例和任务；
优化 output 扫描性能：缓存、索引、增量扫描；
支持从历史 note 一键保存为案例；
支持案例编辑、下架、标签管理；
支持单页重生成；
支持批量下载图片；
支持导出 Markdown 发布包；
引入 Playwright 端到端测试；
完善 API 文档和使用说明；
增加更多 vertical seed 配置；
将 nail 进一步抽象为普通 vertical。
```

v1.1 的目标不应是推翻 v1.0，而是在 v1.0 的接口和产品闭环上增强。

---

### **9.11.3 技术债务记录要求**

每个 Milestone 验收报告必须记录：

```text
已知技术债务；
影响范围；
是否影响当前验收；
是否阻塞上线；
后续修复计划；
优先级。
```

不能用“后面再说”代替技术债务记录。只要某项实现与最终目标存在差距，就应该明确写入报告。

---

# **10. 实施步骤与里程碑**

## **10.1 里程碑总览**

MVP v1.0 分为 5 个里程碑。每个里程碑都应能独立验收，并输出阶段验收报告。

| 里程碑 | 名称 | 目标 | 预计周期 |
|---|---|---|---|
| Milestone 0 | 需求冻结与基线确认 | 冻结本文档作为唯一输入 | 1 天 |
| Milestone 1 | 服务端历史与 package 回放 | 解决历史依赖 localStorage 问题 | 3-5 天 |
| Milestone 2 | 生成模式与案例库 | 补齐三种 reference_source 和案例选择 | 3-5 天 |
| Milestone 3 | 任务进度与内容预览增强 | 让长任务可观察、结果可使用 | 3-5 天 |
| Milestone 4 | 整体联调、回归测试与验收冻结 | 端到端验证、文档冻结 | 2-3 天 |

总周期约 12-18 天，可根据实际资源调整。

---

## **10.2 Milestone 0：需求冻结与基线确认**

### **目标**

冻结本文档作为 Web MVP v1.0 唯一需求输入，确认当前 v0 与目标 v1.0 的差距，并完成任务拆解。

### **交付物**

```text
本文档 v1.0 定稿；
当前 v0 差距清单；
v1.0 功能验收矩阵；
开发任务拆解；
FR 编号与任务映射；
测试计划初稿；
Won't Have 范围确认。
```

### **验收**

```text
所有 Must Have 功能都有对应 FR 编号；
所有 FR 都有测试方案；
所有 API 都有输入输出定义；
明确 Won't Have 范围；
明确 v1.0 技术债务边界；
项目团队确认需求理解一致；
本文档提交到仓库 docs/ 或 verticals/nail/docs/。
```

### **输出**

```text
docs/nail_web_mvp_v1_requirements.md；
docs/nail_web_mvp_v1_acceptance_matrix.md；
docs/nail_web_mvp_v1_test_plan.md；
tasks/v1.0_task_breakdown.md。
```

---

## **10.3 Milestone 1：服务端历史与 package 回放**

### **目标**

解决历史记录不依赖 localStorage 的问题，使历史结果可以从服务端恢复。

### **开发内容**

```text
新增 GET /api/verticals/{vertical}/notes；
实现 History Service；
支持 output 新旧结构扫描；
支持损坏 package 跳过；
新增 GET /api/verticals/{vertical}/notes/{note_id}/package；
实现 Package Service；
实现 package normalize；
实现路径安全校验；
前端 History 模块；
历史 package 回放渲染；
历史接口测试；
package 接口测试。
```

### **验收**

```text
清空 localStorage 后仍可看到历史记录；
点击历史记录可以完整恢复预览；
损坏 package 不导致接口 500；
历史按 vertical 过滤；
返回路径不含本地绝对路径；
旧 package 可以 fallback 推断 vertical；
note_id 不存在时 package 接口返回 404；
note_id 路径穿越被拒绝。
```

### **测试命令**

```bash
python3 -m unittest tests.test_nail_history_api -v
python3 -m unittest tests.test_nail_package_api -v
python3 -m unittest tests.test_package_service -v
python3 -m unittest tests.test_history_service -v
```

### **输出**

```text
阶段验收报告；
测试结果；
手动验收 checklist；
已知问题列表；
技术债务记录。
```

---

## **10.4 Milestone 2：生成模式与案例库**

### **目标**

补齐基础生成、参考图生成、案例复用三种模式，并实现案例库选择入口。

### **开发内容**

```text
reference_source 显式字段；
后端互斥校验；
前端三模式 UI；
参考图上传接口接入；
新增 GET /api/verticals/{vertical}/cases；
实现 Case Service；
案例库前端模块；
案例选择回填 Studio；
案例接口测试；
跨 vertical case 校验；
旧 /api/nail/... 兼容层检查。
```

### **验收**

```text
三种模式均可提交任务；
非法参数组合被拒绝；
参考图上传后可用于 local_path 模式；
案例选择后可成功发起 case_id 任务；
案例按 vertical 隔离；
case.vertical 与 request.vertical 不一致时拒绝；
案例库有空状态和错误状态；
不再要求用户手动输入隐藏 case_id 才能复用案例。
```

### **测试命令**

```bash
python3 -m unittest tests.test_nail_cases_api -v
python3 -m unittest tests.test_reference_source_validation -v
python3 -m unittest tests.test_nail_notes_api -v
```

### **输出**

```text
阶段验收报告；
测试结果；
手动验收 checklist；
已知问题列表；
技术债务记录。
```

---

## **10.5 Milestone 3：任务进度与内容预览增强**

### **目标**

让长任务执行过程可观察，让生成结果可直接用于内容生产。

### **开发内容**

```text
job status 增加 stage；
job status 增加 elapsed_seconds；
job status 增加 error_code、error_message、error_stage；
前端 Progress 模块增强；
Preview 模块增强；
复制标题、正文、标签、全部文案；
图片缺失处理；
partial_failed 展示；
diagnostics 展示；
历史回放与实时预览统一渲染逻辑；
字段缺失 fallback。
```

### **验收**

```text
running 任务可以显示当前 stage 和耗时；
succeeded 任务可以展示完整标题、正文、标签、页面和图片；
failed 任务可以展示错误原因和错误阶段；
partial_failed 任务可以展示成功部分，同时标记失败部分；
历史 package 回放与实时任务成功后的预览展示一致；
复制按钮可正常复制对应内容；
package 字段缺失时页面不崩溃；
图片缺失时页面显示缺失状态。
```

### **测试命令**

```bash
python3 -m unittest tests.test_job_status_api -v
node --check verticals/nail/web/app.js
```

### **输出**

```text
阶段验收报告；
测试结果；
手动验收 checklist；
已知问题列表；
技术债务记录。
```

---

## **10.6 Milestone 4：整体联调、回归测试与验收冻结**

### **目标**

完成 Web MVP v1.0 的端到端验证，确认功能、接口、页面、测试和验收标准全部闭环。

### **开发内容**

```text
基础生成端到端联调；
参考图生成端到端联调；
案例复用端到端联调；
历史回放端到端联调；
失败恢复流程联调；
自动化测试补齐；
手动验收脚本；
文档冻结；
API 合约最终确认；
使用说明编写；
已知限制记录；
后续 backlog 整理。
```

### **验收**

```text
所有 Must Have 功能通过验收；
所有自动化测试通过；
所有核心用户流程手动跑通；
当前实现与本文档需求逐项对应；
没有未解释的范围偏差；
HEAD commit、测试结果、浏览器验证结果均记录在验收报告中；
验收结论明确为通过、有条件通过或不通过。
```

### **测试命令**

```bash
python3 -m py_compile project_paths.py verticals/nail/api/app.py verticals/nail/api/routes.py
node --check verticals/nail/web/app.js
python3 -m unittest tests.test_nail_api -v
python3 -m unittest discover -v
RUN_REAL_IMAGE_TESTS=1 python3 scripts/run_real_nail_image_integration.py
RUN_REAL_IMAGE_TESTS=1 python3 scripts/run_real_nail_ref_image_integration.py /path/to/ref.png
RUN_REAL_IMAGE_TESTS=1 python3 scripts/run_real_nail_case_id_integration.py <case_id>
```

### **输出**

```text
最终验收报告；
完整测试结果；
手动验收 checklist；
API 合约文档；
使用说明；
已知限制；
技术债务清单；
v1.1 backlog。
```

---

## **10.7 里程碑验收报告模板**

每个 Milestone 完成后必须输出验收报告。

```markdown
## Web MVP v1.0 阶段验收报告

### 基本信息

- 验收阶段：Milestone X
- 验收日期：YYYY-MM-DD
- 代码分支：xxx
- HEAD commit：xxx
- origin/main commit：xxx
- 验收人：xxx
- 开发执行人：xxx

### 本阶段目标

填写本 Milestone 的目标。

### 完成功能

| FR 编号 | 功能 | 完成情况 | 备注 |
|---|---|---|---|
| FR-xxx | xxx | 已完成/部分完成/未完成 | xxx |

### API 验收

| API | 验收结果 | 备注 |
|---|---|---|
| GET /api/verticals | 通过/失败 | xxx |

### 自动化测试结果

执行命令：

```bash
填写测试命令
```

测试结果：

```text
填写测试输出摘要
```

### 手动验收结果

| 验收项 | 结果 | 备注 |
|---|---|---|
| 基础生成 | 通过/失败 | xxx |
| 历史回放 | 通过/失败 | xxx |
| 案例复用 | 通过/失败 | xxx |

### 发现问题

| 问题 | 严重程度 | 是否阻塞 | 修复计划 |
|---|---|---|---|
| xxx | P0/P1/P2 | 是/否 | xxx |

### 技术债务记录

| 技术债务 | 影响范围 | 优先级 | 后续计划 |
|---|---|---|---|
| xxx | xxx | P0/P1/P2 | xxx |

### 范围偏差检查

- [ ] 是否所有开发内容都对应 FR 编号？
- [ ] 是否存在未定义的新功能？
- [ ] 是否存在后端有能力但前端无入口？
- [ ] 是否存在 API 字段与文档不一致？
- [ ] 是否存在 Must Have 未完成但被标记完成？
- [ ] 是否存在只通过 localStorage 实现的历史能力？
- [ ] 是否存在只能手填 case_id、没有案例库 UI 的情况？
- [ ] 是否存在 vertical 概念未贯通的问题？
- [ ] 是否存在未知 vertical fallback 到 nail 的问题？
- [ ] 是否存在跨 vertical case_id 未被拒绝的问题？

### 验收结论

结论只能选择一项：

- [ ] 通过
- [ ] 有条件通过
- [ ] 不通过

结论说明：

```text
填写说明。
```
```

---

# **11. 测试方案**

## **11.1 测试原则**

Web MVP v1.0 的测试必须覆盖功能正确性、接口合约、历史恢复、页面交互和安全边界。

测试原则如下：

```text
1. 每个 Must Have 功能必须至少有一条自动化测试或手动验收用例。
2. 每个 API 必须测试成功路径、失败路径和边界路径。
3. 历史记录功能不得只测试 localStorage，必须测试服务端历史来源。
4. reference_source 三种模式必须分别测试，并测试非法组合。
5. 前端渲染不得使用 innerHTML 拼接用户可控内容。
6. 所有真实链路测试必须记录 job_id、note_id、输出目录和测试结果。
7. 测试通过不等于产品验收通过，最终必须结合手动验收 checklist。
8. 平台级测试与垂类级测试分离。
9. vertical 校验必须贯穿 API、数据模型和前端状态。
10. 未知 vertical 不得 fallback 到 nail。
```

---

## **11.2 测试分类**

MVP v1.0 测试分为五类：

```text
1. 后端 API 测试
2. 后端 Service 测试
3. 前端静态测试
4. 前端交互测试
5. 端到端真实链路测试
6. 回归测试
7. 安全测试
```

其中后端 API 测试和前端手动验收必须同时存在。不能只因为接口测试通过，就判定产品功能完成。

---

## **11.3 后端 API 测试**

### **测试文件**

建议测试文件组织：

```text
tests/
  test_verticals_api.py
  test_nail_notes_api.py
  test_nail_history_api.py
  test_nail_cases_api.py
  test_reference_source_validation.py
  test_package_service.py
  test_history_service.py
  test_case_service.py
  test_job_status_api.py
  test_security.py
```

### **必须覆盖的测试**

| 测试对象 | 测试内容 | 必须 |
|---|---|---:|
| `GET /api/verticals` | 返回可用垂类列表 | 是 |
| `POST /api/verticals/{vertical}/notes` | 基础生成创建 job | 是 |
| `POST /api/verticals/{vertical}/notes` | local_path 模式创建 job | 是 |
| `POST /api/verticals/{vertical}/notes` | case_id 模式创建 job | 是 |
| `POST /api/verticals/{vertical}/notes` | 非法 reference_source 组合被拒绝 | 是 |
| `POST /api/verticals/{vertical}/notes` | 未知 vertical 返回 4xx | 是 |
| `POST /api/verticals/{vertical}/notes` | 跨 vertical case_id 被拒绝 | 是 |
| `GET /api/jobs/{job_id}` | 查询 job 状态 | 是 |
| `GET /api/verticals/{vertical}/notes` | 获取服务端历史列表 | 是 |
| `GET /api/verticals/{vertical}/notes/{note_id}/package` | 获取历史 package | 是 |
| `POST /api/verticals/{vertical}/reference-images` | 上传参考图 | 是 |
| `GET /api/verticals/{vertical}/cases` | 获取案例列表 | 是 |
| 旧 `/api/nail/...` 接口 | 兼容层仍可用 | 建议 |

---

### **测试用例示例**

```python
def test_get_verticals(client):
    response = client.get("/api/verticals")
    assert response.status_code == 200

    data = response.json()
    assert "verticals" in data
    assert any(v["vertical"] == "nail" for v in data["verticals"])


def test_create_note_nail_basic(client):
    response = client.post("/api/verticals/nail/notes", json={
        "brief": "夏日短甲猫眼美甲",
        "generate_images": True,
        "reference_source": "none"
    })

    assert response.status_code == 200
    assert "job_id" in response.json()


def test_create_note_invalid_reference_source(client):
    response = client.post("/api/verticals/nail/notes", json={
        "brief": "测试",
        "reference_source": "none",
        "reference_image_path": "/static/input/xxx.png"
    })

    assert response.status_code in (400, 422)


def test_create_note_unknown_vertical(client):
    response = client.post("/api/verticals/unknown/notes", json={
        "brief": "测试",
        "reference_source": "none"
    })

    assert response.status_code in (400, 404)


def test_history_list_empty(client):
    response = client.get("/api/verticals/nail/notes")

    assert response.status_code == 200
    assert "notes" in response.json()
    assert isinstance(response.json()["notes"], list)


def test_package_not_found(client):
    response = client.get(
        "/api/verticals/nail/notes/not_exists/package"
    )

    assert response.status_code == 404


def test_note_id_path_traversal_rejected(client):
    response = client.get(
        "/api/verticals/nail/notes/../secret/package"
    )

    assert response.status_code in (400, 404, 422)


def test_cases_list(client):
    response = client.get("/api/verticals/nail/cases")

    assert response.status_code == 200
    assert "cases" in response.json()
    assert isinstance(response.json()["cases"],
    assert isinstance(response.json()["cases"], list)


def test_case_cross_vertical_rejected(client):
    response = client.post("/api/verticals/nail/notes", json={
        "brief": "测试跨垂类案例",
        "reference_source": "case_id",
        "case_id": "case_outfit_demo_001",
        "generate_images": True
    })

    assert response.status_code in (400, 403, 404, 422)


def test_reference_image_upload_invalid_file(client):
    response = client.post(
        "/api/verticals/nail/reference-images",
        files={
            "file": ("bad.txt", b"not image content", "text/plain")
        }
    )

    assert response.status_code in (400, 415, 422)


def test_job_status_not_found(client):
    response = client.get("/api/jobs/not_exists")

    assert response.status_code in (404, 400)
```

这些测试用例只是示例，实际实现时可以根据当前 API 框架选择 `unittest`、`pytest`、Flask test client、FastAPI test client 或其他测试工具。

重点不是测试框架本身，而是必须覆盖：

```text
成功路径；
失败路径；
边界路径；
路径安全；
vertical 隔离；
reference_source 互斥校验；
历史恢复；
package 回放；
案例复用；
上传校验。
```

---

## **11.4 后端 Service 测试**

除了 API 测试，还建议为核心 Service 增加单元测试。API 测试验证接口行为，Service 测试验证内部逻辑，尤其适合覆盖 output 扫描、fallback、路径清洗和异常处理。

### **11.4.1 History Service 测试**

History Service 至少应测试：

```text
output 为空时返回空列表；
新结构 output/{vertical}/{note_id}/note_package.json 可以被扫描；
旧结构 output/{note_id}/note_package.json 可以被扫描；
旧 package 缺少 vertical 时可以从 note_id 推断；
损坏 package 被跳过；
损坏 package 不影响其他 package；
扫描结果按 created_at 倒序；
limit 和 offset 生效；
未知 vertical 不混入 nail 历史；
返回 item 不包含本地绝对路径。
```

示例：

```python
def test_scan_history_empty(tmp_path):
    service = HistoryService(output_dir=str(tmp_path))

    notes = service.scan_history(vertical="nail")

    assert notes == []


def test_scan_history_skip_damaged_package(tmp_path):
    valid_dir = tmp_path / "nail" / "nail_valid_001"
    valid_dir.mkdir(parents=True)
    (valid_dir / "note_package.json").write_text(
        '{"note_id":"nail_valid_001","vertical":"nail","created_at":"2026-04-30T10:00:00"}',
        encoding="utf-8"
    )

    damaged_dir = tmp_path / "nail" / "nail_bad_001"
    damaged_dir.mkdir(parents=True)
    (damaged_dir / "note_package.json").write_text(
        "{bad json",
        encoding="utf-8"
    )

    service = HistoryService(output_dir=str(tmp_path))

    notes = service.scan_history(vertical="nail")

    assert len(notes) == 1
    assert notes[0]["note_id"] == "nail_valid_001"


def test_scan_history_legacy_infer_vertical(tmp_path):
    legacy_dir = tmp_path / "nail_legacy_001"
    legacy_dir.mkdir(parents=True)
    (legacy_dir / "note_package.json").write_text(
        '{"note_id":"nail_legacy_001","created_at":"2026-04-30T10:00:00"}',
        encoding="utf-8"
    )

    service = HistoryService(output_dir=str(tmp_path))

    notes = service.scan_history(vertical="nail")

    assert len(notes) == 1
    assert notes[0]["vertical"] == "nail"
```

---

### **11.4.2 Package Service 测试**

Package Service 至少应测试：

```text
有效 note_id 可以读取 package；
note_id 不存在返回 PackageNotFound；
note_id 包含路径穿越时被拒绝；
package JSON 损坏时返回 PackageInvalid；
package 缺少 vertical 时可以补齐；
package vertical 与请求 vertical 不一致时拒绝；
本地绝对路径会被转换或移除；
图片缺失不会导致 package 读取失败；
diagnostics.inferred_fields 正确记录 fallback 字段。
```

示例：

```python
def test_package_normalize_adds_missing_vertical(tmp_path):
    note_dir = tmp_path / "nail" / "nail_001"
    note_dir.mkdir(parents=True)
    (note_dir / "note_package.json").write_text(
        '{"note_id":"nail_001","result":{"selected_title":"测试标题"}}',
        encoding="utf-8"
    )

    service = PackageService(output_dir=str(tmp_path))

    package = service.get_package(vertical="nail", note_id="nail_001")

    assert package["vertical"] == "nail"
    assert "diagnostics" in package
    assert "vertical" in package["diagnostics"].get("inferred_fields", [])


def test_package_rejects_vertical_mismatch(tmp_path):
    note_dir = tmp_path / "nail" / "nail_001"
    note_dir.mkdir(parents=True)
    (note_dir / "note_package.json").write_text(
        '{"note_id":"nail_001","vertical":"outfit"}',
        encoding="utf-8"
    )

    service = PackageService(output_dir=str(tmp_path))

    with pytest.raises(VerticalMismatch):
        service.get_package(vertical="nail", note_id="nail_001")
```

---

### **11.4.3 Case Service 测试**

Case Service 至少应测试：

```text
可以读取当前 vertical 的案例；
不会返回其他 vertical 的案例；
keyword 过滤生效；
style_tag 过滤生效；
scenario 过滤生效；
case_id 不存在时返回 CaseNotFound；
case.vertical 与请求 vertical 不一致时拒绝；
preview_image_url 不包含本地绝对路径；
case_id 包含路径穿越字符时被拒绝。
```

示例：

```python
def test_list_cases_only_current_vertical():
    service = CaseService(cases=[
        {
            "case_id": "case_nail_001",
            "vertical": "nail",
            "title": "美甲案例"
        },
        {
            "case_id": "case_outfit_001",
            "vertical": "outfit",
            "title": "穿搭案例"
        }
    ])

    cases = service.list_cases(vertical="nail")

    assert len(cases) == 1
    assert cases[0]["vertical"] == "nail"


def test_get_case_rejects_cross_vertical():
    service = CaseService(cases=[
        {
            "case_id": "case_outfit_001",
            "vertical": "outfit",
            "title": "穿搭案例"
        }
    ])

    with pytest.raises(CaseVerticalMismatch):
        service.get_case(vertical="nail", case_id="case_outfit_001")
```

---

## **11.5 前端静态测试**

前端静态测试的目标是提前发现语法错误、安全渲染风险、API 路径写死、状态缺失等问题。

### **11.5.1 必须执行的命令**

```bash
node --check verticals/nail/web/app.js
```

如果前端拆分为多个 JS 文件，应逐个执行：

```bash
node --check verticals/nail/web/app.js
node --check verticals/nail/web/history.js
node --check verticals/nail/web/cases.js
node --check verticals/nail/web/preview.js
```

具体文件名可根据项目实际结构调整。

---

### **11.5.2 必须检查的内容**

前端静态检查至少应覆盖：

```text
app.js 语法正确；
存在 selectedVertical 或等价状态；
API 调用主路径使用 /api/verticals/{vertical}/...；
存在 reference_source 显式字段；
存在基础生成、参考图生成、案例复用三种模式；
存在 loadHistory 或等价函数；
存在 renderHistory 或等价函数；
存在 loadCases 或等价函数；
存在 renderCases 或等价函数；
存在 renderPreview 或等价函数；
存在 pollJob 或等价任务轮询逻辑；
历史、案例、预览、错误提示不使用 innerHTML 拼接用户可控内容；
字段缺失时不会直接抛出 JS 异常；
图片 URL 设置前有基础校验；
localStorage 不作为历史记录唯一来源。
```

---

### **11.5.3 innerHTML 检查**

v1.0 不要求完全禁止 `innerHTML` 在所有地方出现，但必须禁止用它渲染用户可控内容。

高风险区域包括：

```text
History 列表；
Cases 列表；
Preview 标题；
Preview 正文；
Preview 标签；
Preview 页面内容；
错误信息；
diagnostics；
brief；
caption；
tags。
```

静态检查时应重点搜索：

```bash
grep -n "innerHTML" verticals/nail/web/app.js
```

如果存在 `innerHTML`，必须逐项说明用途。只有在以下情况才可接受：

```text
渲染完全固定的静态模板；
不包含任何 API 返回值；
不包含任何用户输入；
不包含任何 package、case、history、error 字段；
已经通过明确封装保证安全。
```

更推荐的默认方式仍然是：

```text
createElement；
textContent；
appendChild；
createTextNode。
```

---

### **11.5.4 API 路径检查**

前端主流程不得继续只写死旧接口：

```text
/api/nail/...
```

可以保留兼容 fallback，但主路径应为：

```text
/api/verticals/{selectedVertical}/notes；
/api/verticals/{selectedVertical}/cases；
/api/verticals/{selectedVertical}/reference-images；
/api/verticals/{selectedVertical}/notes/{note_id}/package。
```

静态检查可以搜索：

```bash
grep -n "/api/nail" verticals/nail/web/app.js
grep -n "selectedVertical" verticals/nail/web/app.js
grep -n "reference_source" verticals/nail/web/app.js
```

如果仍存在 `/api/nail/...`，需要在验收报告中说明：

```text
是否仅作为兼容层；
是否影响主流程；
是否计划在 v1.1 移除；
是否存在新功能仍只调用旧接口。
```

---

## **11.6 前端交互测试**

前端交互测试用于验证用户能否真正完成产品流程。接口存在不等于产品完成，必须通过浏览器手动验证。

### **11.6.1 页面加载**

必须验证：

```text
页面可以正常打开；
控制台无阻塞性 JS 报错；
页面展示当前平台；
页面展示当前内容形态；
页面展示当前垂类；
生成工作台可见；
任务进度区域可见或可进入；
内容预览区域可见或可进入；
历史记录区域可见或可进入；
案例库区域可见或可进入；
页面初始空状态正常。
```

---

### **11.6.2 生成模式切换**

必须验证三种模式：

```text
基础生成；
参考图生成；
案例复用。
```

基础生成模式下：

```text
reference_source=none；
不要求上传参考图；
不要求选择案例；
payload 不包含 reference_image_path；
payload 不包含 case_id。
```

参考图生成模式下：

```text
reference_source=local_path；
显示上传区域；
上传成功后显示上传状态；
payload 包含 reference_image_path；
payload 不包含 case_id。
```

案例复用模式下：

```text
reference_source=case_id；
显示案例选择入口；
选择案例后显示已选案例；
payload 包含 case_id；
payload 不包含 reference_image_path。
```

切换模式时必须验证：

```text
从参考图模式切回基础生成，reference_image_path 不应继续提交；
从案例模式切回基础生成，case_id 不应继续提交；
从参考图模式切到案例模式，旧 reference_image_path 不应继续提交；
从案例模式切到参考图模式，旧 case_id 不应继续提交。
```

---

### **11.6.3 表单校验**

必须验证：

```text
brief 为空不能提交；
参考图模式未上传图片不能提交；
案例复用模式未选择案例不能提交；
未知 reference_source 不能提交；
前端提示清晰；
后端也会拒绝非法组合。
```

前端校验的目标是提升体验，后端校验的目标是保证安全和数据一致性。两者都必须存在。

---

### **11.6.4 历史记录**

必须手动验证：

```text
生成至少一条成功记录；
清空 localStorage；
刷新页面；
历史记录仍能从服务端加载；
历史列表展示 title、时间、模式等摘要信息；
点击历史项后调用 package 接口；
Preview 成功恢复标题、正文、标签、页面和图片；
页面显示“已从历史记录恢复”或等价状态；
历史为空时显示空状态；
历史接口失败时显示错误状态。
```

关键判断标准是：

```text
历史记录不能依赖 localStorage；
历史恢复必须基于服务端 package；
历史回放和实时预览必须使用同一套 Preview 渲染逻辑。
```

---

### **11.6.5 案例库**

必须手动验证：

```text
案例库可以加载；
案例为空时显示空状态；
案例加载失败时显示错误状态；
案例项展示标题、标签、场景等基本信息；
点击案例后工作台进入案例复用模式；
已选案例在 Studio 中清晰展示；
case_id 被正确写入任务 payload；
提交后后端按 case_id 模式创建任务；
跨 vertical case_id 被拒绝。
```

案例库的验收重点是：

```text
用户不需要手动输入隐藏 case_id；
案例库是可见、可选择、可回填的产品能力。
```

---

### **11.6.6 任务进度**

必须手动验证：

```text
创建任务后页面显示 job_id；
页面显示 status；
running 状态下显示 stage；
running 状态下显示 elapsed_seconds；
任务继续运行时前端持续轮询；
succeeded 后停止轮询；
failed 后停止轮询并显示错误；
partial_failed 后展示成功部分并提示失败部分；
job 查询失败时显示合理错误；
刷新页面后如有 job_id，可根据实现决定是否恢复轮询。
```

如果当前 v1.0 任务状态仍是内存存储，需要在技术债务中记录：

```text
服务重启后 job 状态可能丢失；
但已生成 package 的结果仍可通过历史回放恢复。
```

---

### **11.6.7 内容预览**

必须手动验证：

```text
成功任务展示标题；
成功任务展示正文；
成功任务展示标签；
成功任务展示页面内容；
成功任务展示图片；
图片缺失时显示缺失状态；
复制标题可用；
复制正文可用；
复制标签可用；
复制全部文案可用；
package 字段缺失时页面不崩溃；
diagnostics 可展示或至少不影响页面；
partial_failed 状态下仍展示已成功内容。
```

Preview 的验收重点是内容可用性。生成结果不应只停留在 JSON 层面，用户应能直接复制和使用。

---

## **11.7 端到端真实链路测试**

端到端真实链路测试用于验证从 Web/API 发起任务，到真实生成图片、保存 package、历史回放、内容预览的完整闭环。

### **11.7.1 测试命令**

在具备真实图片生成环境时，必须执行：

```bash
RUN_REAL_IMAGE_TESTS=1 python3 scripts/run_real_nail_image_integration.py
RUN_REAL_IMAGE_TESTS=1 python3 scripts/run_real_nail_ref_image_integration.py /path/to/ref.png
RUN_REAL_IMAGE_TESTS=1 python3 scripts/run_real_nail_case_id_integration.py <case_id>
```

如果真实生成依赖外部模型、密钥、网络或付费资源，应在报告中说明：

```text
测试环境；
依赖配置；
是否使用真实生成；
是否使用 mock；
未执行原因，如有；
风险影响。
```

---

### **11.7.2 必须记录的信息**

每条真实链路必须记录：

```text
执行时间；
执行人；
命令；
job_id；
note_id；
vertical；
reference_source；
output_dir；
是否生成 note_package.json；
是否生成图片；
生成图片数量；
是否可以通过 Web 历史记录打开；
是否可以通过 package 接口回放；
是否存在 partial_failed；
错误信息，如有；
测试结论。
```

推荐记录格式：

```markdown
### 真实链路测试记录

- 测试类型：基础生成 / 参考图生成 / 案例复用
- 执行时间：YYYY-MM-DD HH:mm:ss
- 命令：xxx
- job_id：xxx
- note_id：xxx
- vertical：nail
- reference_source：none/local_path/case_id
- output_dir：xxx
- note_package.json：存在/不存在
- 图片生成：成功/失败/部分失败
- 图片数量：x
- Web 历史可见：是/否
- Package 接口可回放：是/否
- Preview 展示正常：是/否
- 错误信息：xxx
- 结论：通过/失败
```

---

### **11.7.3 验收标准**

端到端真实链路通过标准：

```text
基础生成链路通过；
参考图生成链路通过；
案例复用链路通过；
生成结果写入 output；
生成结果包含 note_package.json；
历史接口能扫描到结果；
package 接口能回放结果；
Web Preview 能展示结果；
失败或部分失败有明确状态和错误信息；
测试记录完整。
```

如果因外部依赖导致真实生成无法执行，可以有条件通过，但必须满足：

```text
mock 链路通过；
API 合约通过；
前端流程通过；
真实链路未执行原因明确；
风险记录在验收报告中；
后续补测计划明确。
```

---

## **11.8 回归测试命令**

每次提交前必须执行基础回归测试。

### **11.8.1 基础命令**

```bash
python3 -m py_compile project_paths.py verticals/nail/api/app.py verticals/nail/api/routes.py
node --check verticals/nail/web/app.js
python3 -m unittest tests.test_nail_api -v
python3 -m unittest discover -v
```

如果项目新增了独立 service 文件，也应加入编译检查：

```bash
python3 -m py_compile verticals/nail/api/services/history_service.py
python3 -m py_compile verticals/nail/api/services/package_service.py
python3 -m py_compile verticals/nail/api/services/case_service.py
```

如果前端拆分为多个文件，也应加入对应检查：

```bash
node --check verticals/nail/web/history.js
node --check verticals/nail/web/cases.js
node --check verticals/nail/web/preview.js
```

---

### **11.8.2 涉及真实链路时**

涉及图片生成、参考图生成或案例复用真实链路时，应执行：

```bash
RUN_REAL_IMAGE_TESTS=1 python3 scripts/run_real_nail_image_integration.py
RUN_REAL_IMAGE_TESTS=1 python3 scripts/run_real_nail_ref_image_integration.py /path/to/ref.png
RUN_REAL_IMAGE_TESTS=1 python3 scripts/run_real_nail_case_id_integration.py <case_id>
```

---

### **11.8.3 验收报告记录要求**

验收报告中必须记录：

```text
执行了哪些命令；
每条命令是否通过；
失败命令的错误摘要；
是否重试；
重试后是否通过；
未执行命令及原因；
是否影响当前验收结论。
```

不能只写“测试通过”，必须能追溯到具体命令。

---

## **11.9 安全测试**

安全测试覆盖路径安全、渲染安全、上传安全、vertical 隔离和错误信息暴露。

### **11.9.1 安全渲染测试**

必须验证：

```text
brief 包含 HTML 标签时，页面按文本展示；
title 包含 HTML 标签时，页面按文本展示；
caption 包含 HTML 标签时，页面按文本展示；
tags 包含特殊字符时，页面按文本展示；
错误信息中包含特殊字符时，页面按文本展示；
history/cases/preview 不使用 innerHTML 拼接用户可控内容。
```

测试样例可以包括：

```text
<script>alert(1)</script>
<img src=x onerror=alert(1)>
<div>测试</div>
" ' < > &
```

通过标准：

```text
页面不执行脚本；
页面不插入非预期 HTML；
内容以文本形式展示；
控制台无阻塞性异常。
```

---

### **11.9.2 路径穿越测试**

必须验证：

```text
note_id 包含 .. 时被拒绝；
note_id 包含 ../ 时被拒绝；
note_id 包含 ..\ 时被拒绝；
note_id 包含 URL 编码路径穿越时被拒绝；
case_id 包含路径穿越字符时被拒绝；
reference_image_path 指向 output/input 之外时被拒绝；
package_path 不允许由用户直接指定。
```

示例请求：

```text
GET /api/verticals/nail/notes/../secret/package
GET /api/verticals/nail/notes/%2e%2e%2fsecret/package
POST /api/verticals/nail/notes with reference_image_path=/etc/passwd
POST /api/verticals/nail/notes with reference_image_path=../../secret.png
```

通过标准：

```text
返回 4xx；
不返回服务器文件内容；
不暴露本地绝对路径；
日志可记录内部细节，但响应不暴露敏感路径。
```

---

### **11.9.3 上传文件测试**

必须验证：

```text
非法后缀被拒绝；
非法 MIME 被拒绝；
空文件被拒绝；
超大文件被拒绝；
伪装后缀文件被拒绝或至少不被当作可信图片；
上传文件保存到受控目录；
返回路径不包含本地绝对路径；
上传失败时返回明确错误。
```

允许的格式建议先限制为：

```text
png；
jpg；
jpeg；
webp。
```

---

### **11.9.4 vertical 隔离测试**

必须验证：

```text
未知 vertical 返回 4xx；
未知 vertical 不 fallback 到 nail；
请求 nail 历史时不返回 outfit 历史；
请求 nail cases 时不返回 outfit cases；
请求 nail package 时不能读取 outfit package；
nail 创建任务不能使用 outfit case_id；
vertical 字段缺失的旧 package 只能在可明确推断时归属；
无法推断 vertical 的 package 不应混入具体 vertical。
```

这是 v1.0 的核心防跑偏测试之一。

---

### **11.9.5 错误信息暴露测试**

必须验证错误响应不暴露：

```text
服务器本地绝对路径；
环境变量；
密钥；
完整堆栈；
内部目录结构；
不必要的依赖信息。
```

错误响应可以包含：

```json
{
  "error_code": "PACKAGE_NOT_FOUND",
  "message": "Package not found"
}
```

不应包含：

```text
/Users/xxx/project/output/...
/home/xxx/...
C:\Users\xxx\...
Traceback ...
SECRET_KEY=...
```

---

# **12. 验收标准与防跑偏机制**

## **12.1 总体验收口径**

Web MVP v1.0 只有在同时满足以下条件时，才能判定为验收通过：

```text
1. 本文档 Must Have 范围内的功能全部完成。
2. 每个功能需求 FR 都有对应实现。
3. 每个核心 API 都符合约定输入输出。
4. 每个核心用户流程都能手动跑通。
5. 所有自动化测试通过。
6. 历史记录不依赖 localStorage，能够从服务端恢复。
7. 案例复用不依赖手动输入隐藏 case_id，必须有前端选择入口。
8. reference_source 三种模式在 UI 和 API 中都显式存在。
9. 当前实现没有未解释的范围偏差。
10. 验收报告记录 commit、测试结果、已知限制和后续 backlog。
11. vertical 概念在 API、数据模型、前端状态中贯通。
12. 未知 vertical 不会 fallback 到 nail。
13. 跨 vertical case_id 被拒绝。
14. 前端不通过 innerHTML 渲染用户可控内容。
15. 返回给前端的路径不包含本地绝对路径。
16. 任务进度、内容预览、历史回放和案例库均有页面入口。
```

其中第 6、7、8、11、12、13 条是核心防偏差点，因为它们直接决定产品是否真正从“美甲单点工具”升级为“多垂类内容生产工作台”。

---

## **12.2 功能验收矩阵**

| 编号 | 功能 | 验收方式 | 通过标准 | 状态 |
|---|---|---|---|---|
| FR-000 | 垂类注册与选择 | API + 手动 | GET /api/verticals 返回 nail，页面展示当前 vertical | 待验收 |
| FR-001 | 创建生成任务 | API + 手动 | 三种模式均可创建 job | 待验收 |
| FR-002 | 服务端历史列表 | API + 手动 | 清空 localStorage 后仍可显示历史 | 待验收 |
| FR-003 | 历史 package 回放 | API + 手动 | 点击历史项完整恢复预览 | 待验收 |
| FR-004 | 案例库选择 | API + 手动 | 选择案例后 case_id 带入生成任务 | 待验收 |
| FR-005 | 任务进度观察 | API + 手动 | 显示 status、stage、耗时、错误 | 待验收 |
| FR-006 | 内容预览 | 手动 | 标题、正文、标签、页面、图片完整展示 | 待验收 |
| FR-007 | 参考图上传 | API + 手动 | 上传图片后可用于 local_path 模式 | 待验收 |
| FR-008 | 安全渲染 | 静态检查 + 手动 | 用户可控内容不通过 innerHTML 渲染 | 待验收 |
| FR-009 | 静态资源访问 | 手动 | 图片 URL 可打开，缺失图片有状态 | 待验收 |
| FR-010 | 错误处理 | API + 手动 | 失败、404、损坏 package 均有合理表现 | 待验收 |
| FR-011 | reference_source 校验 | API + 手动 | 非法组合被拒绝 | 待验收 |
| FR-012 | vertical 隔离 | API + 手动 | 跨 vertical case 被拒绝，未知 vertical 不 fallback | 待验收 |
| FR-013 | note_package 标准化 | API + 手动 | package 包含 vertical 等必填字段 | 待验收 |
| FR-014 | History Service | Service + API | output 扫描、旧结构兼容、损坏跳过 | 待验收 |
| FR-015 | Package Service | Service + API | 安全读取、fallback、路径清洗 | 待验收 |
| FR-016 | Case Service | Service + API | 案例读取、过滤、vertical 校验 | 待验收 |
| FR-017 | Progress 模块 | API + 手动 | running、succeeded、failed、partial_failed 状态正确展示 | 待验收 |
| FR-018 | 防跑偏机制 | 文档 + 验收报告 | 每个 Milestone 输出验收报告并做范围检查 | 待验收 |

这张表后续可以作为独立的 `acceptance_matrix.md` 文件维护。每完成一个 Milestone，都应更新状态，而不是等最终验收时一次性填写。

---

## **12.3 页面验收标准**

Web MVP v1.0 页面必须满足以下标准。

### **12.3.1 生成工作台**

```text
用户可以输入 brief；
用户可以选择基础生成；
用户可以选择参考图生成；
用户可以选择案例复用；
用户可以提交任务；
参数错误时有明确提示；
三种模式切换不会残留非法参数；
payload 中 reference_source 明确存在。
```

---

### **12.3.2 任务进度**

```text
用户可以看到 job_id；
用户可以看到 status；
用户可以看到 stage；
用户可以看到 elapsed_seconds；
用户可以看到 note_id，如有；
用户可以看到 error_code，如有；
用户可以看到 error_message，如有；
用户可以看到 error_stage，如有；
running 状态会继续轮询；
终态会停止轮询。
```

---

### **12.3.3 内容预览**

```text
用户可以看到标题；
用户可以看到正文；
用户可以看到标签；
用户可以看到多页内容；
用户可以看到图片；
图片缺失时有缺失状态；
用户可以复制标题；
用户可以复制正文；
用户可以复制标签；
用户可以复制全部文案；
package 字段缺失时页面不崩溃；
partial_failed 时仍展示成功部分。
```

---

### **12.3.4 历史记录**

```text
用户可以看到服务端历史列表；
用户可以点击历史项打开结果；
localStorage 清空后历史仍然存在；
历史为空时有空状态；
历史加载失败时有错误状态；
历史按 selectedVertical 过滤；
历史 package 回放与实时预览展示一致。
```

---

### **12.3.5 案例库**

```text
用户可以看到案例列表；
用户可以选择案例；
选择案例后工作台进入案例复用模式；
选择案例后 case_id 被带入 payload；
案例为空时有空状态；
案例加载失败时有错误状态；
案例按 selectedVertical 过滤。
```

---

### **12.3.6 垂类上下文**

```text
页面显示当前平台；
页面显示当前内容形态；
页面显示当前垂类；
前端状态中存在 selectedVertical；
API 调用使用 selectedVertical；
不把平台能力全部写死为 nail；
未知 vertical 不会自动回退成 nail。
```

---

## **12.4 API 验收标准**

所有核心 API 必须满足：

```text
返回结构稳定；
成功响应字段符合第 8 章 API 合约；
错误响应有明确 message；
建议错误响应包含 error_code；
不返回本地绝对路径；
不暴露不必要的服务器文件结构；
路径参数不得允许路径穿越；
reference_source 参数必须显式校验；
历史接口遇到单个损坏 package 不得整体失败；
package 接口在 note_id 不存在时返回 404；
未知 vertical 返回 4xx；
跨 vertical case_id 返回 4xx；
case.vertical 与请求 vertical 不一致时拒绝；
图片缺失不影响文本 package 回放；
上传接口拒绝非法文件。
```

核心 API 包括：

```text
GET /api/verticals；
POST /api/verticals/{vertical}/notes；
GET /api/jobs/{job_id}；
GET /api/verticals/{vertical}/notes；
GET /api/verticals/{vertical}/notes/{note_id}/package；
POST /api/verticals/{vertical}/reference-images；
GET /api/verticals/{vertical}/cases。
```

如果保留旧接口：

```text
/api/nail/...
```

必须明确它只是兼容层，不应成为 v1.0 新功能主路径。

---

## **12.5 测试验收标准**

代码合入前必须满足：

```text
Python 编译检查通过；
JavaScript 语法检查通过；
单元测试通过；
API 测试通过；
Service 测试通过；
discover 全量测试通过；
前端手动验收通过；
安全测试通过；
如涉及真实生成链路，真实链路测试通过或有明确豁免说明；
测试结果记录在验收报告中。
```

基础命令：

```bash
python3 -m py_compile project_paths.py verticals/nail/api/app.py verticals/nail/api/routes.py
node --check verticals/nail/web/app.js
python3 -m unittest tests.test_nail_api -v
python3 -m unittest discover -v
```

建议补充命令：

```bash
python3 -m unittest tests.test_verticals_api -v
python3 -m unittest tests.test_nail_history_api -v
python3 -m unittest tests.test_nail_package_api -v
python3 -m unittest tests.test_nail_cases_api -v
python3 -m unittest tests.test_reference_source_validation -v
python3 -m unittest tests.test_security -v
```

真实链路命令：

```bash
RUN_REAL_IMAGE_TESTS=1 python3 scripts/run_real_nail_image_integration.py
RUN_REAL_IMAGE_TESTS=1 python3 scripts/run_real_nail_ref_image_integration.py /path/to/ref.png
RUN_REAL_IMAGE_TESTS=1 python3 scripts/run_real_nail_case_id_integration.py <case_id>
```

---

## **12.6 手动验收 Checklist**

### **基础生成**

```text
[ ] 打开 Web 页面无报错。
[ ] 页面显示当前平台、内容形态、垂类。
[ ] 选择基础生成模式。
[ ] 输入 brief。
[ ] 点击生成。
[ ] payload 使用 reference_source=none。
[ ] 页面显示 job_id。
[ ] 页面显示任务进度。
[ ] running 状态显示 stage 和耗时。
[ ] 任务成功后展示标题、正文、标签、页面和图片。
[ ] 可以复制标题、正文、标签和全部文案。
[ ] 生成结果进入服务端历史记录。
```

---

### **参考图生成**

```text
[ ] 选择参考图生成模式。
[ ] 页面显示参考图上传区域。
[ ] 上传参考图。
[ ] 非法文件会被拒绝。
[ ] 上传成功后显示参考图状态。
[ ] 输入 brief。
[ ] 点击生成。
[ ] payload 使用 reference_source=local_path。
[ ] payload 包含 reference_image_path。
[ ] payload 不包含 case_id。
[ ] 任务成功后结果可预览。
[ ] 历史记录标记为 local_path。
```

---

### **案例复用生成**

```text
[ ] 打开案例库。
[ ] 案例列表加载成功。
[ ] 案例为空时显示空状态。
[ ] 选择一个案例。
[ ] 工作台切换到案例复用模式。
[ ] 页面显示已选案例。
[ ] case_id 正确带入。
[ ] 点击生成。
[ ] payload 使用 reference_source=case_id。
[ ] payload 包含 case_id。
[ ] payload 不包含 reference_image_path。
[ ] 任务成功后结果可预览。
```

---

### **历史记录回放**

```text
[ ] 清空 localStorage。
[ ] 刷新页面。
[ ] 历史记录仍然从服务端加载。
[ ] 历史记录按当前 selectedVertical 过滤。
[ ] 点击历史项。
[ ] 成功打开 note package。
[ ] 标题、正文、标签、页面、图片展示完整。
[ ] 页面显示“已从历史记录恢复”或等价状态。
[ ] 图片缺失时显示缺失状态。
[ ] package 字段缺失时页面不崩溃。
```

---

### **错误处理**

```text
[ ] brief 为空时不能提交
[ ] brief 为空时不能提交。
[ ] 参考图模式未上传图片时不能提交。
[ ] 案例模式未选择案例时不能提交。
[ ] 非法 reference_source 组合被后端拒绝。
[ ] note_id 不存在时 package 接口返回 404。
[ ] 损坏 package 不导致历史接口 500。
[ ] 未知 vertical 返回 4xx。
[ ] 未知 vertical 不会 fallback 到 nail。
[ ] 跨 vertical case_id 被拒绝。
[ ] job 查询失败时页面显示合理错误。
[ ] failed 任务显示 error_message 和 error_stage。
[ ] partial_failed 任务展示成功部分并提示失败部分。
```

---

### **安全渲染**

```text
[ ] 前端代码不包含 history/cases/preview 相关 innerHTML 拼接用户内容。
[ ] brief/title/caption/tags 中包含特殊字符时页面正常展示。
[ ] HTML 标签按文本显示，不被浏览器解析执行。
[ ] 错误信息按文本显示，不被浏览器解析执行。
[ ] 上传非法文件被拒绝。
[ ] 返回路径不含本地绝对路径。
[ ] note_id 路径穿越被拒绝。
[ ] case_id 路径穿越被拒绝。
[ ] reference_image_path 指向非允许目录时被拒绝。
```

---

### **垂类隔离**

```text
[ ] GET /api/verticals 返回 nail。
[ ] 页面显示 selectedVertical。
[ ] 前端 API 主路径使用 /api/verticals/{selectedVertical}/...。
[ ] 请求未知 vertical 返回 4xx。
[ ] 请求未知 vertical 不自动切换到 nail。
[ ] nail 历史列表不混入其他 vertical。
[ ] nail 案例列表不混入其他 vertical。
[ ] nail package 接口不能读取其他 vertical package。
[ ] nail 创建任务不能使用其他 vertical 的 case_id。
[ ] 旧 package 只有在能明确推断 vertical 时才进入对应历史列表。
```

---

## **12.7 防跑偏机制**

为了避免开发过程中再次出现“代码完成但产品偏离原始设想”的情况，Web MVP v1.0 必须执行防跑偏机制。

防跑偏机制的核心目标不是增加流程负担，而是保证每一项开发都能回到明确需求、明确验收、明确测试和明确产品入口上。

---

### **12.7.1 唯一输入原则**

```text
本文档是 v1.0 的唯一需求输入；
开发任务必须引用本文档中的 FR 编号；
未引用 FR 编号的开发内容不得计入 v1.0 完成范围；
口头讨论产生的新需求必须先写入变更记录；
没有写入文档的需求不作为验收依据。
```

这条原则用于防止开发过程中不断加入“看起来有用”的功能，导致 MVP 范围失控。

---

### **12.7.2 需求冻结原则**

```text
Milestone 0 完成后，Must Have 范围冻结；
冻结后如需新增需求，必须记录变更；
变更必须说明进入 v1.0、v1.1 还是 backlog；
影响验收标准的变更必须同步更新验收矩阵；
影响 API 合约的变更必须同步更新第 8 章；
影响测试范围的变更必须同步更新第 11 章。
```

需求冻结不代表不能调整，而是任何调整都必须可追踪。

---

### **12.7.3 任务映射原则**

```text
每个开发任务必须对应一个或多个 FR；
每个 FR 必须对应至少一个测试或验收项；
不允许出现“有代码但无需求编号”的功能；
不允许出现“有需求但无测试验收”的功能；
不允许只完成后端能力却没有前端入口；
不允许只完成 API 字段却没有用户流程；
不允许只通过 mock，却没有说明真实链路风险。
```

任务拆解时建议使用如下格式：

```text
任务：实现服务端历史列表
对应 FR：FR-002、FR-014
涉及 API：GET /api/verticals/{vertical}/notes
涉及测试：tests.test_nail_history_api、tests.test_history_service
涉及页面：History 模块
验收方式：API 测试 + 手动验收
```

---

### **12.7.4 阶段检查原则**

每个 Milestone 完成后必须做一次范围检查。

检查内容包括：

```text
功能完成度；
页面入口；
API 合约；
测试覆盖；
手动验收；
安全边界；
技术债务；
已知限制；
范围偏差；
后续计划。
```

未通过 Milestone 验收，不应直接进入下一阶段。

如果确实需要并行推进，必须在验收报告中标记：

```text
当前阶段未完成项；
是否阻塞下一阶段；
临时绕过方案；
补齐时间；
责任人。
```

---

### **12.7.5 产品优先原则**

MVP v1.0 的验收不能只看代码，也不能只看接口。

必须坚持：

```text
API 存在不等于功能完成；
后端支持不等于前端可用；
localStorage 恢复不等于服务端历史；
case_id 参数存在不等于案例库完成；
JSON 可读不等于内容预览完成；
任务提交成功不等于生成流程可观察；
生成成功不等于结果可用；
vertical 字段存在不等于 vertical 概念贯通；
旧接口兼容不等于新架构完成。
```

对于本项目，尤其要防止以下偏差：

```text
历史记录仍依赖 localStorage；
案例复用仍依赖手动输入 case_id；
前端仍写死 /api/nail/...；
未知 vertical 自动 fallback 到 nail；
跨 vertical case_id 被静默使用；
package 返回本地绝对路径；
Preview 只能展示 JSON，不能复制使用；
任务失败没有阶段和原因；
测试只覆盖 happy path。
```

---

### **12.7.6 验收报告原则**

每次阶段验收必须输出验收报告。

报告必须包含：

```text
验收阶段；
验收日期；
代码分支；
HEAD commit；
origin/main commit；
验收人；
开发执行人；
本阶段目标；
完成功能；
API 验收；
自动化测试结果；
手动验收结果；
发现问题；
技术债务；
范围偏差检查；
验收结论。
```

验收结论只能选择：

```text
通过；
有条件通过；
不通过。
```

不能使用模糊结论，例如：

```text
基本可以；
差不多；
先这样；
后面再看。
```

如果是有条件通过，必须写清楚：

```text
未完成项；
为什么不阻塞当前阶段；
补齐计划；
截止时间；
责任人。
```

---

### **12.7.7 变更记录原则**

所有范围变化必须记录。

变更记录至少包括：

```text
变更编号；
变更日期；
变更提出人；
变更原因；
变更内容；
影响范围；
是否影响 API；
是否影响前端；
是否影响测试；
是否影响验收；
决定进入 v1.0、v1.1 还是 backlog；
决定人。
```

推荐格式：

```markdown
## Change-001：新增案例库筛选字段

- 日期：YYYY-MM-DD
- 提出人：xxx
- 原因：案例数量增加后需要按 style_tag 过滤
- 变更内容：GET /api/verticals/{vertical}/cases 增加 style_tag 查询参数
- 影响范围：Case Service、Cases 前端模块、API 测试
- 是否影响 v1.0 验收：是
- 决定：进入 v1.0
- 决定人：xxx
```

没有记录的变化，不作为验收依据。

---

### **12.7.8 技术债务管理原则**

技术债务可以存在，但不能隐形存在。

每项技术债务必须记录：

```text
债务内容；
产生原因；
影响范围；
风险等级；
是否影响当前验收；
计划处理版本；
责任人。
```

例如：

```text
技术债务：任务状态 v1.0 使用内存存储
产生原因：MVP 阶段优先交付服务端历史与回放能力
影响范围：服务重启后 running job 状态可能丢失
风险等级：P2
是否影响当前验收：不阻塞，因为已生成 package 可通过历史恢复
计划处理版本：v1.1 引入 SQLite 或文件状态存储
```

---

## **12.8 阶段验收报告模板**

以下模板应保存为独立文件，供每个 Milestone 复用。

```markdown
## Web MVP v1.0 阶段验收报告

### 基本信息

- 验收阶段：
- 验收日期：
- 代码分支：
- HEAD commit：
- origin/main commit：
- 验收人：
- 开发执行人：

### 本阶段目标

填写本 Milestone 的目标。

### 完成功能

| FR 编号 | 功能 | 完成情况 | 备注 |
|---|---|---|---|
| FR-xxx | xxx | 已完成/部分完成/未完成 | xxx |

### API 验收

| API | 验收结果 | 备注 |
|---|---|---|
| GET /api/verticals | 通过/失败 | xxx |
| POST /api/verticals/{vertical}/notes | 通过/失败 | xxx |
| GET /api/jobs/{job_id} | 通过/失败 | xxx |
| GET /api/verticals/{vertical}/notes | 通过/失败 | xxx |
| GET /api/verticals/{vertical}/notes/{note_id}/package | 通过/失败 | xxx |
| POST /api/verticals/{vertical}/reference-images | 通过/失败 | xxx |
| GET /api/verticals/{vertical}/cases | 通过/失败 | xxx |

### 自动化测试结果

执行命令：

```bash
python3 -m py_compile project_paths.py verticals/nail/api/app.py verticals/nail/api/routes.py
node --check verticals/nail/web/app.js
python3 -m unittest tests.test_nail_api -v
python3 -m unittest discover -v
```

测试结果：

```text
填写测试输出摘要。
```

### Service 测试结果

执行命令：

```bash
python3 -m unittest tests.test_history_service -v
python3 -m unittest tests.test_package_service -v
python3 -m unittest tests.test_case_service -v
```

测试结果：

```text
填写测试输出摘要。
```

### 手动验收结果

| 验收项 | 结果 | 备注 |
|---|---|---|
| 页面加载 | 通过/失败 | xxx |
| 基础生成 | 通过/失败 | xxx |
| 参考图生成 | 通过/失败 | xxx |
| 案例复用 | 通过/失败 | xxx |
| 任务进度 | 通过/失败 | xxx |
| 内容预览 | 通过/失败 | xxx |
| 历史回放 | 通过/失败 | xxx |
| 案例库选择 | 通过/失败 | xxx |
| 安全渲染 | 通过/失败 | xxx |
| vertical 隔离 | 通过/失败 | xxx |

### 真实链路测试结果

| 链路 | 是否执行 | 结果 | job_id | note_id | 备注 |
|---|---|---|---|---|---|
| 基础生成 | 是/否 | 通过/失败 | xxx | xxx | xxx |
| 参考图生成 | 是/否 | 通过/失败 | xxx | xxx | xxx |
| 案例复用 | 是/否 | 通过/失败 | xxx | xxx | xxx |

未执行原因：

```text
如未执行真实链路测试，在这里说明原因、风险和补测计划。
```

### 发现问题

| 问题 | 严重程度 | 是否阻塞 | 修复计划 |
|---|---|---|---|
| xxx | P0/P1/P2 | 是/否 | xxx |

### 技术债务记录

| 技术债务 | 影响范围 | 优先级 | 是否影响验收 | 后续计划 |
|---|---|---|---|---|
| xxx | xxx | P0/P1/P2 | 是/否 | xxx |

### 范围偏差检查

- [ ] 是否所有开发内容都对应 FR 编号？
- [ ] 是否存在未定义的新功能？
- [ ] 是否存在后端有能力但前端无入口？
- [ ] 是否存在 API 字段与文档不一致？
- [ ] 是否存在 Must Have 未完成但被标记完成？
- [ ] 是否存在只通过 localStorage 实现的历史能力？
- [ ] 是否存在只能手填 case_id、没有案例库 UI 的情况？
- [ ] 是否存在 reference_source 没有在 UI 和 API 中显式贯通的问题？
- [ ] 是否存在 vertical 概念未贯通的问题？
- [ ] 是否存在未知 vertical fallback 到 nail 的问题？
- [ ] 是否存在跨 vertical case_id 未被拒绝的问题？
- [ ] 是否存在返回本地绝对路径的问题？
- [ ] 是否存在 innerHTML 渲染用户可控内容的问题？
- [ ] 是否存在测试未覆盖但被标记完成的功能？

### 验收结论

结论只能选择一项：

- [ ] 通过
- [ ] 有条件通过
- [ ] 不通过

结论说明：

```text
填写说明。
```

如为有条件通过，必须填写：

```text
未完成项：
不阻塞原因：
补齐计划：
截止时间：
责任人：
```
```

---

## **12.9 文档落地建议**

本文档不应只停留在聊天记录中，而应成为项目仓库里的正式需求、技术方案和验收基准。

推荐放置方式一：

```text
docs/
  nail_web_mvp_v1_requirements.md
  nail_web_mvp_v1_acceptance_matrix.md
  nail_web_mvp_v1_test_plan.md
  technical_debt.md
  v1.1_backlog.md
  reports/
    milestone_0_acceptance_report.md
    milestone_1_acceptance_report.md
    milestone_2_acceptance_report.md
    milestone_3_acceptance_report.md
    milestone_4_acceptance_report.md
```

推荐放置方式二：

```text
verticals/
  nail/
    docs/
      web_mvp_v1_requirements.md
      web_mvp_v1_acceptance_matrix.md
      web_mvp_v1_test_plan.md
      technical_debt.md
      v1.1_backlog.md
      reports/
        milestone_0_acceptance_report.md
        milestone_1_acceptance_report.md
        milestone_2_acceptance_report.md
        milestone_3_acceptance_report.md
        milestone_4_acceptance_report.md
```

如果团队希望突出这是平台级能力，而不是 nail 私有能力，可以采用混合结构：

```text
docs/
  vertical_content_studio_mvp_v1_requirements.md
  vertical_content_studio_mvp_v1_acceptance_matrix.md
  vertical_content_studio_mvp_v1_test_plan.md

verticals/
  nail/
    docs/
      nail_vertical_config.md
      nail_seed_cases.md
      nail_acceptance_notes.md
```

这样可以把平台级需求和 nail 垂类落地配置区分开。

---

### **12.9.1 建议拆分文件**

为了便于开发和验收，建议将本文档拆成以下文件：

```text
requirements.md：
  包含第 0-8 章，重点描述背景、范围、用户流程、FR、API 合约。

technical_plan.md：
  包含第 9 章，重点描述技术路线、服务实现、前端实现、技术债务。

milestones.md：
  包含第 10 章，重点描述实施步骤、里程碑、交付物。

test_plan.md：
  包含第 11 章，重点描述测试分类、测试命令、测试用例、安全测试。

acceptance.md：
  包含第 12 章，重点描述验收标准、防跑偏机制、验收报告模板。
```

如果项目规模较小，也可以先合并为一个文件：

```text
docs/vertical_content_studio_mvp_v1.md
```

但验收矩阵和阶段报告建议独立维护。

---

### **12.9.2 建议提交动作**

Milestone 0 开始前，建议执行：

```text
1. 将本文档提交到仓库。
2. 将功能验收矩阵拆成独立文件。
3. 将测试方案拆成独立文件。
4. 创建 docs/reports/ 目录。
5. 创建 technical_debt.md。
6. 创建 v1.1_backlog.md。
7. 创建 tasks/v1.0_task_breakdown.md。
8. 为每个开发任务绑定 FR 编号。
9. 召开需求确认会议。
10. 冻结 v1.0 Must Have 范围。
```

提交后，建议在 README 或项目入口文档中写明：

```text
Web MVP v1.0 的唯一需求输入为 docs/vertical_content_studio_mvp_v1.md。
所有开发任务必须引用 FR 编号。
所有验收以 docs/acceptance.md 和 docs/reports/ 为准。
```

---

### **12.9.3 API 合约同步要求**

如果后续开发中 API 发生变化，必须同步更新文档。

需要同步的情况包括：

```text
新增 API；
删除 API；
修改路径；
修改请求字段；
修改响应字段；
修改错误码；
修改 reference_source 枚举；
修改 note_package 结构；
修改 case item 结构；
修改 job status 结构；
修改上传返回结构。
```

API 合约变更不能只改代码，不改文档。

---

### **12.9.4 验收矩阵维护要求**

验收矩阵不应是一次性文档，而应在每个 Milestone 后更新。

状态建议使用：

```text
待验收；
开发中；
已完成；
部分完成；
阻塞；
延期到 v1.1；
移出范围。
```

每次状态变化应记录：

```text
更新时间；
对应 commit；
对应测试结果；
对应验收报告；
备注。
```

---

## **12.10 第 12 章验收要求**

第 12 章本身也需要被验收。

在进入开发前，应确认以下事项：

```text
所有 Must Have 范围都有 FR 编号；
所有核心页面模块都有 FR 覆盖；
所有核心用户流程都有 FR 覆盖；
所有 P0 FR 都有明确验收标准；
每个 FR 都能映射到测试方案；
每个开发任务都能引用至少一个 FR；
不存在“只写了想法但无法测试”的需求；
不存在“只写了接口但没有页面入口”的需求；
不存在“后端支持但前端不可用”的功能；
不存在“localStorage 历史替代服务端历史”的偏差；
不存在“手填 case_id 替代案例库”的偏差；
验收矩阵可以逐项跟踪；
防跑偏机制可以被执行；
阶段验收报告模板可以直接使用；
技术债务记录机制明确；
变更记录机制明确。
```

如果某项开发任务无法映射到任何 FR，则必须先判断：

```text
是否应该新增 FR；
是否应该放入 v1.1；
是否应该放入 backlog；
是否属于范围外功能；
是否应该取消该任务。
```

不得在没有需求编号、没有验收标准、没有测试映射的情况下直接开发。

---

### **12.10.1 第 12 章通过标准**

第 12 章通过标准如下：

```text
验收口径清晰；
功能验收矩阵完整；
页面验收标准完整；
API 验收标准完整；
测试验收标准完整；
手动验收 checklist 可执行；
防跑偏机制可执行；
阶段验收报告模板可复用；
文档落地路径明确；
后续维护机制明确。
```

如果以上任一项缺失，应在 Milestone 0 阶段补齐后再进入正式开发。

---

### **12.10.2 第 12 章不通过情形**

以下情况应判定第 12 章不通过：

```text
FR 与验收矩阵无法对应；
只有功能描述，没有验收方式；
只有 API 描述，没有页面验收；
只有自动化测试，没有手动验收；
没有规定 localStorage 历史不能作为最终方案；
没有规定 case_id 必须有案例库入口；
没有规定 vertical 隔离；
没有规定未知 vertical 不得 fallback 到 nail；
没有规定跨 vertical case_id 必须拒绝；
没有规定阶段验收报告；
没有规定范围变更记录。
```

---