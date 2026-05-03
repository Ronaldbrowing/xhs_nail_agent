
# Nail Web Studio MVP v1.0 产品需求、技术方案与验收基准

本文档定义的是一个面向小红书图文笔记生产的多垂类内容生成工作台。美甲 nail 是 v1.0 的首个落地垂类，用于验证通用工作台、垂类配置、任务生成、历史回放、案例复用和内容预览链路。

除特别说明外，本文中的“内容生成任务”“历史记录”“案例库”“参考来源”“任务进度”“内容预览”等能力均为通用平台能力，不应与 nail 垂类强绑定。

v1.0 的验收范围是：通用平台能力完成，并以 nail 垂类作为首个 vertical 完成端到端验收。



## 构建一份完整、准确、可追溯版本的文档

这份文档的目标不是“描述想法”，而是成为后面推进项目的**唯一输入、唯一范围边界、唯一验收依据**。

### **这份文档应该解决的核心问题**

现在遇到的问题，本质上不是某个功能没做，而是“需求基准没有被工程化”。之前有原始设想，但可能还停留在愿景、模块、Sprint、功能列表层面；开发过程中又切到了 P0-P3 的工程修复语境，导致最后形成了一个“工程可用但产品不完整”的版本。

所以这次文档要明确回答几类问题：

```text
我们到底要做一个什么产品？
哪些功能必须做，哪些功能暂缓？
页面应该长什么样，用户如何流转？
后端要提供哪些接口和数据？
每个功能怎么测试？
做到什么程度才算完成？
中途新增或修改需求怎么处理？
每个阶段怎么检查有没有跑偏？
```

如果这几个问题写不清楚，后面继续开发时仍然可能出现：

```text
工程师做了接口，但没有前端入口；
做了 localStorage，但没有服务端历史；
做了 case_id 参数，但没有案例库 UI；
做了进度轮询，但没有任务详情；
做了功能，但验收时不知道算不算完成。
```

因此，下一步应该先做“需求冻结与验收基线”，而不是继续写代码。

---

### **文档整体结构建议**

我建议文档分成 12 个部分，每个部分都有明确作用。

```text
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

这 12 部分足够覆盖你关心的“原始需求、技术路线、实现方案、实施步骤、测试方案、验收标准、中途检查”。

---

## **第一部分：项目背景与目标**

这一部分要回答“为什么要做这个 Web MVP”。

不要只写“做一个页面调用接口”，而要把产品目标说清楚。

建议这样写：

```markdown

## 0. 核心术语与抽象层

Vertical Content Studio 是一个面向小红书图文笔记生产的多垂类内容生成工作台。系统需要区分以下几个层级：

1. 内容平台 content_platform
   - 表示内容最终面向的平台。
   - v1.0 固定为 xhs，即小红书。
   - 未来可扩展到 douyin、wechat、bilibili 等，但不纳入 v1.0。

2. 内容形态 content_type
   - 表示生成内容的类型。
   - v1.0 固定为 image_text_note，即图文笔记。
   - 未来可扩展到 short_video_script、carousel_post、product_note 等。

3. 垂类 vertical
   - 表示行业细分赛道。
   - v1.0 首个落地垂类为 nail。
   - 未来可扩展到 outfit、home、pet、food、travel、fitness、mom_baby 等。

4. 场景 scenario
   - 表示某个垂类下的具体内容场景。
   - 例如 nail 下可有 summer_cat_eye、short_nail、wedding_nail、commuter_nail。
   - outfit 下可有 commute_outfit、date_outfit、vacation_outfit。

5. 工作流 workflow
   - 表示某个 vertical/scenario 对应的生成流程。
   - 不同垂类可以共享通用流程，也可以有自己的垂类适配逻辑。

6. 案例 case
   - 表示可复用的优质内容资产。
   - case 必须归属于某个 vertical，可选归属于某个 scenario。
   - case_id 在全局唯一，或者通过 vertical + case_id 唯一。

7. 笔记 note
   - 表示一次生成得到的完整小红书图文笔记结果。
   - note 必须包含 content_platform、content_type、vertical、note_id 等基础字段。

8. 参考来源 reference_source
   - 表示生成任务参考资料的来源。
   - v1.0 支持 none、local_path、case_id。
   - 后续可扩展到 history_note、url、brand_asset、knowledge_base。


## 1. 项目背景与目标

当前系统已在 nail 美甲场景中验证了小红书图文笔记生成的基础能力，但现有实现仍主要围绕单一垂类、单一页面和局部接口链路展开，缺少一个面向多垂类扩展的通用内容生产工作台。

Vertical Content Studio MVP v1.0 的目标不是简单提供一个美甲生成页面，而是建立一套可复用、可扩展、可验收的多垂类小红书图文内容生产框架。

v1.0 以 nail 美甲作为首个落地垂类，完成从生成、参考图、案例复用、任务进度、结果预览、历史回放到案例管理的完整闭环。同时，所有核心模型、API、前端模块和验收标准必须保留 vertical 维度，确保后续可以增加新的行业细分赛道，而不需要重写整个系统。


该工作台需要支持以下核心目标：

1. 用户可以选择目标垂类 vertical，并创建对应的小红书图文笔记生成任务。
2. 用户可以在指定垂类下输入内容需求 brief，并选择生成模式。
3. 用户可以选择无参考、上传参考图、复用案例三种生成模式。
4. 用户可以观察长任务生成进度，理解任务当前阶段和失败原因。
5. 用户可以查看完整生成结果，包括标题、正文、标签、多页图文结构、图片和诊断信息。
6. 用户可以从历史记录中找回过去生成的内容，并按 vertical 过滤。
7. 用户可以浏览某个 vertical 下的案例库，并选择案例用于下一次生成。
8. 系统必须支持以 nail 作为首个 vertical 完成端到端验收，同时为新增 vertical 保留清晰扩展点。

```

这里要刻意强调一句：

```text
Web MVP v1.0 不是“接口调试页面”，而是“可复用的内容生产工作台”。
```

这句话可以作为产品方向的锚点。后面开发时，如果某个实现只满足“能调接口”，但不满足“可持续生产使用”，就可以判定为不完整。

---

## **第二部分：当前实现状态与差距**

这一部分非常关键。它不是为了否定当前实现，而是为了明确“已有基础”和“待补差距”。

建议不要写成情绪化的“跑偏了”，而写成：

```text
当前版本为 Web MVP v0 内部验证版，已完成工程最小闭环，但未达到 Web MVP v1.0 产品工作台标准。当前实现不仅是产品形态简化，而且存在垂类强绑定问题。
```

可以这样写：

| 模块 | 当前状态 | 通用化问题 | v1.0 要求 |
| --- | --- | --- | --- |
| 产品命名 | Nail Web Studio | 产品名绑定 nail | 改为 Vertical Content Studio |
| API 路径 | /api/nail/... | 路径绑定单垂类 | 设计 /api/verticals/{vertical}/... 或兼容层 |
| 数据模型 | note/case 默认美甲 | 缺少 vertical 字段 | note、case、job 必须包含 vertical |
| 前端文案 | 美甲图文 | UI 绑定行业 | 支持选择垂类，nail 为默认 |
| 历史记录 | 只扫描 nail output | 无法跨垂类查询 | 历史按 vertical 过滤 |
| 案例库 | nail cases | 无法管理多垂类案例 | case 归属 vertical/scenario |
| 测试命名 | test_nail_api | 测试绑定 nail | 通用测试 + nail 垂类测试 |
| 工作流 | NailNoteWorkflow | workflow 绑定 nail | 定义 vertical adapter |

这一部分的目的，是把“现在已经做到什么”和“未来必须补什么”分开，避免后面重复争论。

这里也建议明确一个版本判断：

```markdown
### 2.1 当前版本判断

当前版本可定义为 Web MVP v0 内部验证版。它已经证明后端任务、前端轮询、结果展示、参考图上传、case_id 参数、静态文件访问等底层链路可行。

但它尚未达到 Web MVP v1.0 的产品工作台标准。主要差距在于：

- 历史记录依赖浏览器 localStorage，而非服务端历史。
- 案例库没有可视化浏览与选择能力。
- 任务进度缺少阶段、页级状态和诊断信息。
- 生成模式没有以产品形态明确区分。
- 缺少统一的验收矩阵和防跑偏机制。
```

---

## **第三部分：产品定位与用户场景**

这一部分要把“用户是谁、怎么用、为什么用”写清楚。

建议定义一个核心用户：

```text
内容生产者 / 运营者 / 项目开发者本人
```

核心场景可以这样写：

```markdown
## 3. 产品定位与用户场景

Vertical Content Studio MVP v1.0 面向小红书图文笔记内容生产场景，服务于需要在多个行业细分赛道中批量生成、复用、查看和管理内容资产的用户。

系统的长期目标不是单一美甲工具，而是一个可扩展到多个 vertical 的内容生产工作台。v1.0 选择 nail 美甲作为首个验证垂类，以降低范围复杂度，同时要求底层模型、API、页面和验收标准具备多垂类扩展能力。


### 3.1 核心使用场景

场景一：选择垂类并基础生成  
用户进入工作台，选择目标 vertical，例如 nail。用户输入内容方向，例如“夏日短甲猫眼美甲”，系统根据 nail 垂类配置生成适合小红书发布的标题、正文、标签和多页图文结构。

场景二：参考图生成  
用户在某个 vertical 下上传参考图，系统结合该垂类的图像理解规则和内容风格，生成相关图文内容。v1.0 在 nail 垂类中验证该能力。

场景三：案例复用生成  
用户从当前 vertical 的案例库中选择一个历史案例或优质案例，系统基于该案例的风格、结构或标签生成新的内容。

场景四：跨历史回放  
用户可以在历史记录中按 vertical 查看过去生成的 note package，即使浏览器缓存清空，也可以从服务端 output 或持久化存储中恢复结果。

场景五：新增垂类扩展  
当未来新增 outfit、home、pet 等垂类时，开发者不应重写工作台，而应通过新增 vertical 配置、workflow adapter、case 数据和测试用例完成扩展。
```

这里的关键是把“历史回放”和“案例复用”定义成核心场景，而不是附加功能。因为你现在最担心的就是这些被弱化。

---

## **第四部分：MVP v1.0 范围定义**

### 4.0 v1.0 范围原则

MVP v1.0 采用“通用底座 + 首个垂类落地”的范围策略。

v1.0 必须完成：
- 通用工作台页面结构。
- 通用任务、历史、案例、预览、参考来源模型。
- vertical 字段在 API、数据模型、输出包、历史记录和案例库中的贯通。
- nail 作为首个 vertical 的完整端到端链路。

v1.0 不要求完成多个真实业务垂类的内容生成质量验证，但必须提供新增 vertical 的清晰扩展方式，并至少通过一个 mock 或 sample vertical 验证通用路由、模型和页面不被 nail 写死。

这是整份文档最重要的部分之一。要明确：

```text
必须做什么
可以不做什么
明确不做什么
```

我建议把范围分成 Must、Should、Could、Won’t 四类。

### **4.1 v1.0 必须包含的范围**

```markdown
## 4. MVP v1.0 范围定义

### 4.1 Must Have：v1.0 必须完成

1. 生成工作台
   - 支持输入内容需求。
   - 支持选择生成模式：基础生成、参考图生成、案例复用。
   - 支持提交任务并获得 job_id。
   - 支持 generate_images 参数。
   - 支持基础错误提示。

2. 任务进度
   - 支持根据 job_id 查询任务状态。
   - 显示任务状态：queued、running、succeeded、failed、partial_failed、timeout、restored。
   - 显示当前阶段 stage，如 planning、copywriting、image_generation、qa、saving。
   - 显示错误信息和错误阶段。
   - 显示任务耗时。

3. 内容预览
   - 展示 selected_title。
   - 展示正文 caption/body。
   - 展示 tags。
   - 展示多页页面结构。
   - 展示生成图片。
   - 支持复制标题、正文、标签。
   - 支持从 note_package.json 恢复预览。

4. 历史记录
   - 提供服务端历史列表接口。
   - 前端展示历史记录列表。
   - 历史记录必须来自服务端 output 目录或持久化存储，不得只依赖 localStorage。
   - 点击历史记录可以打开对应 note package 并完整回放。

5. 案例库
   - 提供案例列表接口。
   - 前端展示案例列表。
   - 用户可以选择案例并将 case_id 用于新任务。
   - 案例选择必须与生成工作台联动。

6. 参考来源
   - 显式支持三种 reference_source：
     - none
     - local_path
     - case_id
   - 三种模式在 UI 和 API 中必须互斥。
   - 后端必须校验非法组合。

7. 静态资源访问
   - 支持访问 output 图片。
   - 支持访问 input 上传参考图。
   - 前端展示的图片 URL 必须可直接打开。

8. 基础安全
   - 前端不得使用 innerHTML 渲染用户可控内容。
   - 上传文件必须校验后缀和类型。
   - 后端不得返回本地绝对路径。
   - 历史接口不得允许路径穿越。
```

### **4.2 Should Have：建议 v1.0 包含**

```markdown
### 4.2 Should Have：建议完成

1. 历史记录支持按时间倒序展示。
2. 历史记录展示 brief、标题、图片数量、qa_score、reference_source。
3. 案例库支持关键词过滤。
4. 任务完成后展示 diagnostics.reference、diagnostics.timing、page_timings。
5. 支持复制单页内容。
6. 支持打开输出目录对应的静态资源链接。
```

### **4.3 Could Have：可以后续做**

```markdown
### 4.3 Could Have：可后续增强

1. 单页重生成。
2. 多任务并发管理。
3. 批量下载图片。
4. 导出 Markdown 发布包。
5. 更完整的案例评分与标签系统。
6. 用户登录与多用户隔离。
```

### **4.4 Won’t Have：v1.0 明确不做**

这一部分非常重要，能避免中途无限扩展。

```markdown
### 4.4 Won’t Have：v1.0 不做

1. 不做复杂账号系统。
2. 不做云端部署和权限系统。
3. 不做复杂图片编辑器。
4. 不做完整 CMS。
5. 不做多用户协作。
6. 不做自动发布到小红书。
7. 不做大规模数据库迁移，除非服务端历史扫描无法满足需求。
```

这部分能保护项目边界，防止“顺手再做一点”导致范围失控。

---

## **第五部分：信息架构与页面结构**

你原始设想里有 5 个核心页面，这次要把它写成明确的信息架构。

建议先不要执着于“必须 5 个独立路由页面”，可以定义为 5 个一级模块。实现上可以是单页 Tab，也可以是多路由，但产品上必须完整。

```markdown
## 5. 信息架构与页面结构

Web MVP v1.0 包含 5 个核心模块：

1. 生成工作台 Studio
2. 任务进度 Jobs
3. 内容预览 Preview
4. 历史记录 History
5. 案例库 Cases
```

可以加一张结构表：

| 模块 | 主要目的 | 核心内容 | 是否必须 |
|---|---|---|---|
| 生成工作台 | 创建新任务 | brief、模式、参考图、case_id、参数 | 必须 |
| 任务进度 | 查看任务状态 | job_id、stage、status、error、timing | 必须 |
| 内容预览 | 查看生成结果 | 标题、正文、标签、页面、图片 | 必须 |
| 历史记录 | 回放过去结果 | note 列表、打开 package | 必须 |
| 案例库 | 复用优质案例 | case 列表、搜索、选择 case_id | 必须 |

然后明确每个模块至少要有哪些字段和动作。

### **5.1 生成工作台**

```markdown
生成工作台必须包含：

字段：
- 内容需求 brief
- 生成模式 reference_source
- 是否生成图片 generate_images
- 参考图上传 reference_image_path，仅 local_path 模式显示
- 案例选择 case_id，仅 case_id 模式显示

动作：
- 提交生成任务
- 清空表单
- 从案例库带入 case_id
- 从历史记录复用 brief 或 case
```

### **5.2 任务进度**

```markdown
任务进度模块必须包含：

字段：
- job_id
- note_id，如果已生成
- status
- stage
- progress_text
- started_at
- updated_at
- elapsed_seconds
- error_code
- error_message

动作：
- 自动轮询
- 手动刷新
- 成功后打开预览
- 失败后查看错误详情
```

### **5.3 内容预览**

```markdown
内容预览模块必须包含：

字段：
- note_id
- selected_title
- caption/body
- tags
- pages
- image_urls
- qa_score
- diagnostics

动作：
- 复制标题
- 复制正文
- 复制标签
- 打开图片
- 从 package 恢复
```

### **5.4 历史记录**

```markdown
历史记录模块必须包含：

字段：
- note_id
- created_at
- brief
- selected_title
- status
- reference_source
- page_count
- generated_image_count
- qa_score

动作：
- 加载历史列表
- 打开历史 package
- 复用为新任务
```

### **5.5 案例库**

```markdown
案例库模块必须包含：

字段：
- case_id
- title
- style_tags
- source_note_id
- qa_score
- preview_image

动作：
- 浏览案例
- 搜索案例
- 选择案例
- 使用案例生成
```

---

## **第六部分：核心用户流程**

这一部分要防止工程师只按接口做，而忽略用户实际路径。

我建议写 4 条主流程。

### **流程一：基础生成**

```markdown
用户进入生成工作台。
用户选择“基础生成”。
用户输入 brief。
用户点击生成。
系统创建 job 并进入任务进度。
任务成功后系统展示内容预览。
用户复制标题、正文、标签，查看图片。
系统将结果写入服务端历史。
用户可以之后从历史记录再次打开。
```

### **流程二：参考图生成**

```markdown
用户进入生成工作台。
用户选择“参考图生成”。
用户上传参考图。
系统返回 reference_image_path。
用户输入 brief。
用户点击生成。
系统创建 job，payload 中 reference_source=local_path。
任务成功后展示内容预览。
预览中展示 reference diagnostics。
历史记录中标记 reference_source=local_path。
```

### **流程三：案例复用生成**

```markdown
用户进入案例库。
用户浏览或搜索案例。
用户点击“使用此案例”。
系统跳转或回填生成工作台。
生成模式变为“案例复用”。
case_id 自动填入。
用户补充 brief。
用户点击生成。
系统创建 job，payload 中 reference_source=case_id。
任务完成后展示结果。
```

### **流程四：历史回放**

```markdown
用户进入历史记录。
前端调用服务端历史列表接口。
系统展示历史 note 列表。
用户点击某条历史记录。
前端调用 note package 接口。
系统渲染历史预览。
页面状态显示“已从历史记录恢复”。
该过程不依赖 localStorage。
```

这四条流程是后续验收的核心。每次开发完成都要手动跑一遍。

---

## **第七部分：功能需求明细**

这一部分要写成可开发、可测试的需求项。不要只写“支持历史记录”，而要写清楚输入、输出、异常、完成标准。

推荐格式：

```text
FR-编号
功能名称
用户故事
功能描述
输入
输出
异常处理
验收标准
```

举几个关键示例。

### **FR-001 创建生成任务**

```markdown
### FR-001 创建生成任务

用户故事：
作为内容生产者，我希望输入内容需求并创建生成任务，以便系统为我生成小红书美甲图文内容。

功能描述：
用户在生成工作台填写 brief，选择生成模式和参数后，点击生成。前端调用创建任务接口，后端返回 job_id。前端进入任务进度状态并开始轮询。

输入：
- brief，必填
- generate_images，布尔值
- reference_source，枚举值：none/local_path/case_id
- reference_image_path，local_path 模式必填
- case_id，case_id 模式必填

输出：
- job_id
- status

异常处理：
- brief 为空时前端阻止提交。
- reference_source=local_path 但未上传图片时前端阻止提交。
- reference_source=case_id 但未选择案例时前端阻止提交。
- 后端返回错误时展示错误信息。

验收标准：
- 基础生成可以成功创建 job。
- 参考图生成可以成功创建 job。
- 案例复用生成可以成功创建 job。
- 三种模式 payload 正确且互斥。
```

### **FR-002 服务端历史列表**

```markdown
### FR-002 服务端历史列表

用户故事：
作为内容生产者，我希望即使清空浏览器缓存，也能从历史记录中找回过去生成的内容。

功能描述：
后端提供历史列表接口，扫描服务端 output 目录下的 note_package.json，返回可回放的历史 note 列表。前端在历史记录模块展示该列表。

输入：
- 无必填参数。
- 可选 limit、offset、keyword。

输出：
- notes 数组。
- 每个 note 包含 note_id、created_at、brief、selected_title、status、reference_source、page_count、generated_image_count、qa_score。

异常处理：
- 某个 note_package.json 损坏时跳过该项并记录 diagnostics。
- output 目录为空时返回空数组，不返回 500。
- 不返回本地绝对路径。
- 不允许路径穿越。

验收标准：
- localStorage 为空时仍然可以看到服务端历史。
- 点击历史记录可以打开对应 package。
- 损坏 JSON 不导致接口整体失败。
- 返回路径不包含本机绝对路径。
```

### **FR-003 历史 package 回放**

```markdown
### FR-003 历史 package 回放

用户故事：
作为内容生产者，我希望点击历史记录后可以完整恢复过去生成的标题、正文、标签、页面结构和图片。

功能描述：
前端点击历史项后，调用 note package 接口，使用与实时任务成功后相同的渲染逻辑展示结果。

输入：
- note_id

输出：
- note_package

异常处理：
- note_id 不存在时展示“历史记录不存在或已被删除”。
- package 存在但图片缺失时仍展示文本，并标记图片缺失。
- package 字段不完整时使用 fallback 文案，不导致页面崩溃。

验收标准：
- 可以从历史列表打开任意有效 note。
- 展示内容与生成完成后的预览一致。
- 页面状态显示“已从历史记录恢复”。
```

### **FR-004 案例库选择**

```markdown
### FR-004 案例库选择

用户故事：
作为内容生产者，我希望从案例库选择一个优质案例作为参考，而不是手动输入 case_id。

功能描述：
前端展示案例库列表，用户点击“使用此案例”后，生成工作台进入 case_id 模式，并自动填入对应 case_id。

输入：
- 可选 keyword
- 可选 style_tag

输出：
- cases 数组

异常处理：
- 无案例时展示空状态。
- case_id 不存在时提交任务失败并提示。
- 案例加载失败时展示错误信息和重试按钮。

验收标准：
- 案例库可以展示至少一个案例。
- 点击案例后生成工作台正确切换到案例复用模式。
- 提交任务时 payload 包含 reference_source=case_id 和 case_id。
```

### **FR-005 任务进度观察**

```markdown
### FR-005 任务进度观察

用户故事：
作为内容生产者，我希望知道长任务当前执行到哪一步，以判断是否正常运行。

功能描述：
前端根据 job_id 轮询任务状态接口，展示 status、stage、elapsed_seconds、error 等信息。

输入：
- job_id

输出：
- status
- stage
- note_id
- elapsed_seconds
- error_code
- error_message

异常处理：
- job_id 不存在时，如果存在 note_id，则尝试 package fallback。
- 任务失败时停止轮询并展示错误。
- 任务超时时停止轮询并提示。
- 网络错误时允许用户手动重试。

验收标准：
- queued/running/succeeded/failed 状态均可正确展示。
- succeeded 后自动渲染预览。
- failed 后展示错误原因。
- job 404 fallback 能恢复已有 note package。
```

---

## **第八部分：数据模型与 API 合约**

这一部分是防止“前后端各做各的”的关键。

建议明确核心数据对象：

```text
CreateNoteRequest
JobStatus
NoteHistoryItem
NotePackage
CaseItem
UploadReferenceImageResponse
```

### **8.1 CreateNoteRequest**

```json
{
  "brief": "夏日短甲猫眼美甲",
  "generate_images": true,
  "reference_source": "none",
  "reference_image_path": null,
  "case_id": null
}
```

规则必须写清楚：

```markdown
reference_source 取值：
- none：不得传 reference_image_path 和 case_id
- local_path：必须传 reference_image_path，不得传 case_id
- case_id：必须传 case_id，不得传 reference_image_path
```

这条非常重要，因为它能防止当前“后端靠推断”的模糊状态继续存在。

### **8.2 JobStatus**

```json
{
  "job_id": "job_xxx",
  "status": "running",
  "stage": "image_generation",
  "note_id": null,
  "progress_text": "正在生成第 3 页图片",
  "elapsed_seconds": 128,
  "error_code": null,
  "error_message": null
}
```

### **8.3 NoteHistoryItem**

```json
{
  "note_id": "nail_20260430_xxx",
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

### **8.4 CaseItem**

```json
{
  "case_id": "case_summer_cat_eye_001",
  "title": "夏日短甲猫眼案例",
  "style_tags": ["短甲", "猫眼", "夏日"],
  "source_note_id": "nail_20260430_xxx",
  "qa_score": 0.91,
  "preview_image_url": "/static/output/xxx/page_01.png"
}
```

### **8.5 API 清单**

| 方法 | 路径 | 目的 | v1.0 必须 |
|---|---|---|---|
| POST | `/api/nail/notes` | 创建生成任务 | 是 |
| GET | `/api/jobs/{job_id}` | 查询任务状态 | 是 |
| GET | `/api/nail/notes` | 获取历史记录 | 是 |
| GET | `/api/nail/notes/{note_id}/package` | 获取历史 package | 是 |
| POST | `/api/nail/reference-images` | 上传参考图 | 是 |
| GET | `/api/nail/cases` | 获取案例列表 | 是 |

这里要注意，路径只是建议，如果你当前项目已有路径，可以在文档里以实际路径为准。但必须形成稳定合约。

---

## **第九部分：技术路线与实现方案**

这里要回答“怎么做”，但不要写得过度复杂。基于你现在已有 FastAPI 和静态前端，我建议 v1.0 不要大规模换技术栈，先基于现有架构补齐产品能力。

建议技术路线：

```markdown
## 9. 技术路线与实现方案

Web MVP v1.0 延续当前 FastAPI + 静态前端的轻量架构，不在 v1.0 引入复杂前端框架、账号系统或数据库迁移，优先补齐服务端历史、案例库、任务进度、模式建模和验收测试。

技术原则：

1. 保持现有核心生成链路稳定。
2. 优先补齐产品闭环，不重写已可用的底层逻辑。
3. 历史记录第一阶段通过扫描 output 目录下的 note_package.json 实现。
4. 案例库第一阶段可以基于已有案例目录或配置文件实现。
5. API 合约必须显式定义 reference_source，避免隐式推断。
6. 前端渲染必须使用安全 DOM API，不使用 innerHTML 渲染用户可控内容。
7. 所有新增能力必须有自动化测试和手动验收路径。
```

### **9.1 后端实现方案**

```markdown
后端主要改造点：

1. schemas.py
   - 新增或完善 CreateNoteRequest。
   - 新增 NoteHistoryItem。
   - 新增 CaseItem。
   - 新增 JobStatus 中 stage、elapsed_seconds、error 字段。

2. routes.py
   - 新增 GET /api/nail/notes。
   - 新增 GET /api/nail/cases。
   - 完善 POST /api/nail/notes 的 reference_source 校验。
   - 完善 GET /api/nail/notes/{note_id}/package 的错误处理。

3. history service
   - 扫描 OUTPUT_DIR。
   - 读取 note_package.json。
   - 提取历史列表字段。
   - 跳过损坏 JSON。
   - 对路径做安全转换。

4. case service
   - 从案例目录、配置文件或历史优质 note 中构建案例列表。
   - 返回可用于前端选择的 case_id 和展示信息。

5. job service
   - 在任务状态中增加 stage 和 timing。
   - 失败时返回结构化错误。
```

### **9.2 前端实现方案**

```markdown
前端主要改造点：

1. 页面结构
   - 保留 Studio 主工作台。
   - 增加 History 模块。
   - 增加 Cases 模块。
   - 强化 Progress 模块。
   - 强化 Preview 模块。

2. 状态管理
   - 维护 currentJob。
   - 维护 currentNotePackage。
   - 维护 selectedReferenceSource。
   - 维护 selectedCase。
   - 维护 historyList。
   - 维护 caseList。

3. 生成模式
   - 使用 radio/tab 明确三种模式：
     - 基础生成
     - 参考图生成
     - 案例复用
   - 不同模式只显示对应输入项。
   - 提交前做互斥校验。

4. 历史记录
   - 页面加载时调用 GET /api/nail/notes。
   - 渲染历史列表。
   - 点击历史项后调用 package 接口。
   - 复用现有预览渲染函数。

5. 案例库
   - 页面加载或切换时调用 GET /api/nail/cases。
   - 渲染案例卡片。
   - 选择案例后回填工作台。

6. 安全渲染
   - 所有用户可控内容使用 textContent。
   - 图片 URL 做基础校验。
   - 不用 innerHTML 拼接历史、案例、预览内容。
```

### **9.3 是否要引入数据库**

我的建议是：v1.0 暂时不要强制引入数据库。

可以这样写：

```markdown
v1.0 默认使用 output 目录扫描作为历史记录来源。该方式实现成本低，能快速解决历史回放问题。

只有在以下情况出现时，才进入 SQLite 方案：

1. output 目录扫描性能不可接受。
2. 需要复杂搜索、分页、状态更新。
3. 需要记录生成失败但未产生 package 的任务。
4. 需要多用户隔离或长期稳定归档。

因此，v1.0 的第一阶段不强制引入数据库，但接口设计应保持未来可替换为 SQLite 的能力。
```

这个判断比较稳：先解决真实问题，不为了架构完整而过度开发。

---

## **第十部分：实施步骤与里程碑**

这里要避免一次性大改。建议分成 4 个里程碑，每个里程碑都能独立验收。

### **Milestone 0：需求冻结与基线确认**

```markdown
目标：
冻结本文档作为 Web MVP v1.0 唯一输入。

交付物：
- 本文档 v1.0。
- 当前 v0 差距清单。
- v1.0 功能验收矩阵。
- 开发任务拆解。

验收：
- 所有 Must Have 功能都有对应 FR 编号。
- 所有 FR 都有测试方案。
- 所有 API 都有输入输出定义。
- 明确 Won’t Have 范围。
```

### **Milestone 1：服务端历史与 package 回放**

```markdown
目标：
解决历史记录不依赖 localStorage 的问题。

开发内容：
- GET /api/nail/notes。
- 历史扫描 service。
- package 回放稳定性增强。
- 历史接口测试。

验收：
- 清空 localStorage 后仍可看到历史记录。
- 点击历史记录可以完整恢复预览。
- 损坏 package 不导致接口 500。
```

### **Milestone 2：生成模式与案例库**

```markdown
目标：
补齐基础生成、参考图生成、案例复用三种模式。

开发内容：
- reference_source 显式字段。
- 后端互斥校验。
- 前端三模式 UI。
- GET /api/nail/cases。
- 案例库选择回填。

验收：
- 三种模式均可提交任务。
- 非法参数组合被拒绝。
- 案例选择后可成功发起 case_id 任务。
```



### **Milestone 3：任务进度与内容预览增强**

```markdown
目标：
让长任务执行过程可观察，让生成结果可直接用于内容生产，而不仅仅是展示原始 package。

开发内容：

1. 任务进度增强
   - job status 中增加 stage 字段。
   - job status 中增加 elapsed_seconds。
   - job status 中增加 error_code、error_message、error_stage。
   - 前端 Progress 模块展示当前阶段、任务状态、耗时和错误信息。
   - 成功、失败、部分失败、超时状态均有明确 UI 表达。

2. 页面级结果展示
   - Preview 模块展示 selected_title。
   - Preview 模块展示正文 caption/body。
   - Preview 模块展示 tags。
   - Preview 模块展示 pages 数组。
   - 每一页展示 page title、copy、visual prompt、image_url。
   - 图片缺失时不让页面崩溃，而是显示“图片缺失”。

3. 复制与复用能力
   - 支持复制标题。
   - 支持复制正文。
   - 支持复制标签。
   - 支持复制单页文案。
   - 支持从历史 note 复用 brief 或 case。

4. 诊断信息展示
   - 展示 reference diagnostics。
   - 展示 timing diagnostics。
   - 展示 page_timings。
   - diagnostics 缺失时不报错，显示为空状态。

验收：
- running 任务可以显示当前 stage 和耗时。
- succeeded 任务可以展示完整标题、正文、标签、页面和图片。
- failed 任务可以展示错误原因和错误阶段。
- partial_failed 任务可以展示成功部分，同时标记失败部分。
- 历史 package 回放与实时任务成功后的预览展示一致。
- 复制按钮可正常复制对应内容。
- package 字段缺失时页面不崩溃。
```

这一阶段的重点不是新增大功能，而是把已有生成结果真正变成“可用内容”。如果只显示 JSON 或简单文本，用户仍然无法把它作为生产工作台使用。

---

### **Milestone 4：整体联调、回归测试与验收冻结**

```markdown
### Milestone 4：整体联调、回归测试与验收冻结

目标：
完成 Web MVP v1.0 的端到端验证，确认功能、接口、页面、测试和验收标准全部闭环。

开发内容：

1. 端到端联调
   - 基础生成链路联调。
   - 参考图生成链路联调。
   - 案例复用生成链路联调。
   - 历史记录回放链路联调。
   - 失败任务展示链路联调。

2. 自动化测试补齐
   - 后端 API 测试。
   - schema 校验测试。
   - 历史扫描测试。
   - 案例库接口测试。
   - package 回放测试。
   - 前端 JS 静态检查。
   - 安全渲染检查。

3. 手动验收脚本
   - 编写一份人工验收 checklist。
   - 每条用户流程必须有明确操作步骤。
   - 每条验收项必须标记通过、失败或不适用。
   - 失败项必须记录原因和修复 commit。

4. 文档冻结
   - 更新 README 或 docs。
   - 记录最终 API 合约。
   - 记录 Web MVP v1.0 使用说明。
   - 记录已知限制。
   - 记录后续 v1.1/v1.2 backlog。

验收：
- 所有 Must Have 功能通过验收。
- 所有自动化测试通过。
- 所有核心用户流程手动跑通。
- 当前实现与本文档需求逐项对应。
- 没有未解释的范围偏差。
- HEAD commit、测试结果、浏览器验证结果均记录在验收报告中。
```

Milestone 4 的核心意义是“收口”。不能只说代码写完了，而要把功能、测试、文档、验收报告都对齐。否则后面又会出现“代码层面通过，但产品层面没达到”的情况。

---

## **第十一部分：测试方案**

测试方案必须和需求逐项对应。这里建议分成五类：后端 API 测试、前端静态测试、前端交互测试、端到端链路测试、回归测试。

不要只依赖单元测试。因为这类 Web MVP 的主要风险不是某个函数错了，而是“功能链路断了”“前后端字段不一致”“页面没有入口”“历史不能恢复”。

---

### **11.1 测试原则**

```markdown
## 11. 测试方案

### 11.1 测试原则

Web MVP v1.0 的测试必须覆盖功能正确性、接口合约、历史恢复、页面交互和安全边界。

测试原则如下：

1. 每个 Must Have 功能必须至少有一条自动化测试或手动验收用例。
2. 每个 API 必须测试成功路径、失败路径和边界路径。
3. 历史记录功能不得只测试 localStorage，必须测试服务端历史来源。
4. reference_source 三种模式必须分别测试，并测试非法组合。
5. 前端渲染不得使用 innerHTML 拼接用户可控内容。
6. 所有真实链路测试必须记录 job_id、note_id、输出目录和测试结果。
7. 测试通过不等于产品验收通过，最终必须结合手动验收 checklist。
```

这部分尤其要强调一句：

```text
测试通过不等于产品验收通过。
```

因为之前的问题就是代码测试通过，但产品预期没完全满足。

---

### **11.2 后端 API 测试**

建议测试文件继续放在：

```text
tests/test_nail_api.py
```

也可以后续拆分成：

```text
tests/test_nail_history_api.py
tests/test_nail_cases_api.py
tests/test_nail_reference_source.py
```

后端 API 测试至少包括这些。

| 测试对象 | 测试内容 | 必须 |
|---|---|---|
| `/health` | 服务健康检查返回 ok | 是 |
| `POST /api/nail/notes` | 基础生成创建 job | 是 |
| `POST /api/nail/notes` | local_path 模式创建 job | 是 |
| `POST /api/nail/notes` | case_id 模式创建 job | 是 |
| `POST /api/nail/notes` | 非法 reference_source 组合被拒绝 | 是 |
| `GET /api/jobs/{job_id}` | 查询 job 状态 | 是 |
| `GET /api/nail/notes` | 获取服务端历史列表 | 是 |
| `GET /api/nail/notes/{note_id}/package` | 获取历史 package | 是 |
| `POST /api/nail/reference-images` | 上传参考图 | 是 |
| `GET /api/nail/cases` | 获取案例列表 | 是 |

可以把测试要求写成这样：

```markdown
### 11.2 后端 API 测试

必须覆盖以下测试：

1. 健康检查
   - 调用 GET /health。
   - 期望返回 200。
   - 期望 body.status = ok。

2. 创建任务：基础生成
   - reference_source=none。
   - 不传 reference_image_path。
   - 不传 case_id。
   - 期望返回 job_id。

3. 创建任务：参考图生成
   - reference_source=local_path。
   - 传 reference_image_path。
   - 不传 case_id。
   - 期望返回 job_id。

4. 创建任务：案例复用
   - reference_source=case_id。
   - 传 case_id。
   - 不传 reference_image_path。
   - 期望返回 job_id。

5. 创建任务：非法组合
   - reference_source=none 但传 reference_image_path，应返回 4xx。
   - reference_source=local_path 但未传 reference_image_path，应返回 4xx。
   - reference_source=case_id 但未传 case_id，应返回 4xx。
   - 同时传 reference_image_path 和 case_id，应返回 4xx。

6. 历史记录列表
   - 构造临时 output/note_id/note_package.json。
   - 调用 GET /api/nail/notes。
   - 期望返回 notes 数组。
   - 期望包含构造的 note_id。
   - 期望不返回本地绝对路径。

7. 损坏历史 package
   - 构造损坏 JSON 文件。
   - 调用 GET /api/nail/notes。
   - 期望接口不返回 500。
   - 期望跳过损坏项或返回 diagnostics。

8. package 回放
   - 调用 GET /api/nail/notes/{note_id}/package。
   - 期望返回 note package。
   - note_id 不存在时返回 404。

9. 案例库
   - 调用 GET /api/nail/cases。
   - 期望返回 cases 数组。
   - 每个 case 至少包含 case_id 和 title。
```

---

### **11.3 前端静态测试**

前端如果当前还是原生 JS，就至少要做语法检查和安全字符串检查。

```markdown
### 11.3 前端静态测试

必须执行：

```bash
node --check verticals/nail/web/app.js
```

必须检查：

1. app.js 语法正确。
2. 历史记录渲染逻辑存在。
3. 案例库渲染逻辑存在。
4. reference_source 三模式逻辑存在。
5. 不使用 innerHTML 渲染用户可控内容。
6. 不使用不安全的字符串拼接生成 HTML。
```

这里可以定义更具体的检查点：

```markdown
静态检查项：

- app.js 包含 loadHistory 或等价历史加载函数。
- app.js 包含 renderHistory 或等价历史渲染函数。
- app.js 包含 loadCases 或等价案例加载函数。
- app.js 包含 renderCases 或等价案例渲染函数。
- app.js 包含 reference_source 或等价显式模式字段。
- app.js 中历史、案例、预览模块不得使用 innerHTML 拼接用户内容。
```

这里的目的不是迷信字符串检查，而是给开发一个硬边界：不能为了快又回到不安全渲染。

---

### **11.4 前端交互测试**

这部分可以先以手动测试为主。后续如果引入 Playwright，再自动化。

```markdown
### 11.4 前端交互测试

必须手动验证以下交互：

1. 页面加载
   - 页面可以正常打开。
   - 生成工作台、任务进度、内容预览、历史记录、案例库模块可见或可切换。
   - 初始状态不会报错。

2. 生成模式切换
   - 选择基础生成时，不显示参考图必填项和 case_id 必填项。
   - 选择参考图生成时，显示参考图上传区域。
   - 选择案例复用时，显示案例选择或 case_id。
   - 三种模式切换不会残留非法参数。

3. 表单校验
   - brief 为空不能提交。
   - 参考图模式未上传图片不能提交。
   - 案例复用模式未选择案例不能提交。

4. 历史记录
   - localStorage 清空后，历史记录仍能从服务端加载。
   - 点击历史项后可以打开预览。
   - 历史为空时显示空状态。

5. 案例库
   - 案例库可以加载。
   - 点击案例后工作台进入案例复用模式。
   - case_id 被正确带入任务 payload。

6. 预览
   - 成功任务展示标题、正文、标签、页面和图片。
   - 图片缺失时显示缺失状态。
   - 复制按钮可用。

7. 错误展示
   - API 错误时显示错误提示。
   - job 失败时显示失败状态。
   - job 404 且有 note_id 时触发 fallback。
```

---

### **11.5 端到端真实链路测试**

这部分非常重要，因为你这个系统的核心是生成链路。Mock 测试通过不代表真实链路能跑。

建议保留真实链路测试开关：

```bash
RUN_REAL_IMAGE_TESTS=1
```

测试命令可以定义为：

```markdown
### 11.5 端到端真实链路测试

在具备真实图片生成环境时，必须执行以下链路：

```bash
RUN_REAL_IMAGE_TESTS=1 python3 scripts/run_real_nail_image_integration.py
RUN_REAL_IMAGE_TESTS=1 python3 scripts/run_real_nail_ref_image_integration.py /path/to/ref.png
RUN_REAL_IMAGE_TESTS=1 python3 scripts/run_real_nail_case_id_integration.py <case_id>
```

每条真实链路必须记录：

- 执行时间
- job_id
- note_id
- output_dir
- 是否生成 note_package.json
- 是否生成图片
- 是否可以通过 Web 历史记录打开
- 是否可以通过 package 接口回放
- 是否存在 partial_failed
- 错误信息，如有
```

也就是说，真实测试不只看脚本是否返回 0，还要确认 Web 工作台能不能回放结果。

---

### **11.6 回归测试命令**

建议文档里写死每次提交前必须跑的命令。

```markdown
### 11.6 回归测试命令

每次提交前必须执行：

```bash
python3 -m py_compile project_paths.py verticals/nail/api/app.py verticals/nail/api/routes.py
node --check verticals/nail/web/app.js
python3 -m unittest tests.test_nail_api -v
python3 -m unittest discover -v
```

如果新增了真实链路相关改动，还必须执行：

```bash
RUN_REAL_IMAGE_TESTS=1 python3 scripts/run_real_nail_image_integration.py
RUN_REAL_IMAGE_TESTS=1 python3 scripts/run_real_nail_ref_image_integration.py /path/to/ref.png
RUN_REAL_IMAGE_TESTS=1 python3 scripts/run_real_nail_case_id_integration.py <case_id>
```

验收报告中必须记录所有命令的输出摘要。
```

---

## **第十二部分：验收标准与防跑偏机制**

这一部分是整个文档的“控制系统”。它要解决你现在最担心的问题：后面开发又变成“做了很多代码，但不是你要的产品”。

验收标准必须分成四层：

```text
功能验收
接口验收
测试验收
产品体验验收
```

同时要有防跑偏机制：

```text
需求编号
任务映射
每日/每阶段检查
变更控制
验收矩阵
```

---

### **12.1 总体验收口径**

```markdown
## 12. 验收标准与防跑偏机制

### 12.1 总体验收口径

Web MVP v1.0 只有在同时满足以下条件时，才能判定为验收通过：

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
```

这里第 6、7、8 条是核心防偏差点。因为这正是当前 v0 和原始设想差距最大的地方。

---

### **12.2 功能验收矩阵**

建议文档中必须有验收矩阵。格式可以这样：

| 编号 | 功能 | 验收方式 | 通过标准 | 状态 |
|---|---|---|---|---|
| FR-001 | 创建生成任务 | API + 手动 | 三种模式均可创建 job | 待验收 |
| FR-002 | 服务端历史列表 | API + 手动 | 清空 localStorage 后仍可显示历史 | 待验收 |
| FR-003 | 历史 package 回放 | API + 手动 | 点击历史项完整恢复预览 | 待验收 |
| FR-004 | 案例库选择 | API + 手动 | 选择案例后 case_id 带入生成任务 | 待验收 |
| FR-005 | 任务进度观察 | API + 手动 | 显示 status、stage、耗时、错误 | 待验收 |
| FR-006 | 内容预览 | 手动 | 标题、正文、标签、页面、图片完整展示 | 待验收 |
| FR-007 | 参考图上传 | API + 手动 | 上传图片后可用于 local_path 模式 | 待验收 |
| FR-008 | 安全渲染 | 静态检查 | 用户可控内容不通过 innerHTML 渲染 | 待验收 |
| FR-009 | 静态资源访问 | 手动 | 图片 URL 可打开 | 待验收 |
| FR-010 | 错误处理 | API + 手动 | 失败、404、损坏 package 均有合理表现 | 待验收 |

这张表后续可以直接作为验收报告的一部分。每次开发完成一项，就更新状态。

---

### **12.3 页面验收标准**

页面验收要避免“接口有了但页面没有入口”的问题。

```markdown
### 12.3 页面验收标准

Web MVP v1.0 页面必须满足：

1. 生成工作台
   - 用户可以输入 brief。
   - 用户可以选择基础生成、参考图生成、案例复用。
   - 用户可以提交任务。
   - 参数错误时有明确提示。

2. 任务进度
   - 用户可以看到 job_id。
   - 用户可以看到 status。
   - 用户可以看到 stage。
   - 用户可以看到耗时。
   - 用户可以看到错误信息。

3. 内容预览
   - 用户可以看到标题。
   - 用户可以看到正文。
   - 用户可以看到标签。
   - 用户可以看到多页内容。
   - 用户可以看到图片。
   - 用户可以复制核心内容。

4. 历史记录
   - 用户可以看到服务端历史列表。
   - 用户可以点击历史项打开结果。
   - localStorage 清空后历史仍然存在。
   - 历史为空时有空状态。

5. 案例库
   - 用户可以看到案例列表。
   - 用户可以选择案例。
   - 选择案例后工作台进入案例复用模式。
```

这部分是为了防止后端做完接口，但前端还是没有历史、案例入口。

---

### **12.4 API 验收标准**

```markdown
### 12.4 API 验收标准

所有 API 必须满足：

1. 返回结构稳定。
2. 错误响应有明确 message。
3. 不返回本地绝对路径。
4. 不暴露不必要的服务器文件结构。
5. 路径参数不得允许路径穿越。
6. reference_source 参数必须显式校验。
7. 历史接口遇到单个损坏 package 不得整体失败。
8. package 接口在 note_id 不存在时返回 404。
```

API 验收尤其要注意历史接口。因为历史扫描 output 目录时，最容易出现路径、安全、损坏文件导致整体失败的问题。

---

### **12.5 测试验收标准**

```markdown
### 12.5 测试验收标准

代码合入前必须满足：

1. Python 编译检查通过。
2. JavaScript 语法检查通过。
3. 单元测试通过。
4. API 测试通过。
5. discover 全量测试通过。
6. 如涉及真实生成链路，真实链路测试通过。
7. 测试结果必须记录在验收报告中。

基础命令：

```bash
python3 -m py_compile project_paths.py verticals/nail/api/app.py verticals/nail/api/routes.py
node --check verticals/nail/web/app.js
python3 -m unittest tests.test_nail_api -v
python3 -m unittest discover -v
```
```

---

### **12.6 手动验收 Checklist**

这部分可以直接复制到后续验收报告中。

```markdown
### 12.6 手动验收 Checklist

#### 基础生成

- [ ] 打开 Web 页面无报错。
- [ ] 选择基础生成模式。
- [ ] 输入 brief。
- [ ] 点击生成。
- [ ] 页面显示 job_id。
- [ ] 页面显示任务进度。
- [ ] 任务成功后展示标题、正文、标签、页面和图片。
- [ ] 生成结果进入历史记录。

#### 参考图生成

- [ ] 选择参考图生成模式。
- [ ] 上传参考图。
- [ ] 上传成功后显示参考图状态。
- [ ] 输入 brief。
- [ ] 点击生成。
- [ ] payload 使用 reference_source=local_path。
- [ ] 任务成功后结果可预览。
- [ ] 历史记录标记为 local_path。

#### 案例复用生成

- [ ] 打开案例库。
- [ ] 案例列表加载成功。
- [ ] 选择一个案例。
- [ ] 工作台切换到案例复用模式。
- [ ] case_id 正确带入。
- [ ] 点击生成。
- [ ] payload 使用 reference_source=case_id。
- [ ] 任务成功后结果可预览。

#### 历史记录回放

- [ ] 清空 localStorage。
- [ ] 刷新页面。
- [ ] 历史记录仍然从服务端加载。
- [ ] 点击历史项。
- [ ] 成功打开 note package。
- [ ] 标题、正文、标签、页面、图片展示完整。
- [ ] 页面显示“已从历史记录恢复”或等价状态。

#### 错误处理

- [ ] brief 为空时不能提交。
- [ ] 参考图模式未上传图片时不能提交。
- [ ] 案例模式未选择案例时不能提交。
- [ ] 非法 reference_source 组合被后端拒绝。
- [ ] note_id 不存在时 package 接口返回 404。
- [ ] 损坏 package 不导致历史接口 500。
```

---

### **12.7 防跑偏机制**

这是最重要的管理部分。建议写得硬一点。

```markdown
### 12.7 防跑偏机制

为了避免开发过程中再次出现“代码完成但产品偏离原始设想”的情况，Web MVP v1.0 必须执行以下防跑偏机制：

1. 唯一输入原则
   - 本文档是 v1.0 的唯一需求输入。
   - 开发任务必须引用本文档中的 FR 编号。
   - 未引用 FR 编号的开发内容不得计入 v1.0 完成范围。

2. 需求冻结原则
   - Milestone 0 完成后，Must Have 范围冻结。
   - 如需新增需求，必须记录到变更记录。
   - 新需求必须标明进入 v1.0、v1.1 或 backlog。

3. 任务映射原则
   - 每个开发任务必须对应一个或多个 FR。
   - 每个 FR 必须对应至少一个测试或验收项。
   - 不允许出现“有代码但无需求编号”的功能。
   - 不允许出现“有需求但无测试验收”的功能。

4. 阶段检查原则
   - 每个 Milestone 完成后必须做一次范围检查。
   - 检查内容包括功能完成度、页面入口、API 合约、测试覆盖、验收状态。
   - 未通过 Milestone 验收，不进入下一阶段。

5. 产品优先原则
   - API 存在不等于功能完成。
   - 后端支持不等于前端可用。
   - localStorage 恢复不等于服务端历史。
   - case_id 参数存在不等于案例库完成。
   - JSON 可读不等于内容预览完成。

6. 验收报告原则
   - 每次阶段验收必须输出验收报告。
   - 报告必须包含 commit hash、测试命令、测试结果、手动验收结果、失败项、已知限制。
   - 验收报告必须明确“通过”“有条件通过”或“不通过”。

7. 变更记录原则
   - 所有范围变化必须记录。
   - 记录内容包括变更原因、影响范围、是否影响验收、决定人、日期。
   - 没有记录的变化不作为验收依据。
```

这里面有几句可以作为以后反复检查的“红线”：

```text
API 存在不等于功能完成。
后端支持不等于前端可用。
localStorage 恢复不等于服务端历史。
case_id 参数存在不等于案例库完成。
JSON 可读不等于内容预览完成。
```

这些话非常适合写进文档，因为它们正好对应当前项目已经出现过的问题。

---

### **12.8 阶段验收报告模板**

建议最后给一个固定模板，后面每个 Milestone 完成后都按这个写。

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
| GET /api/nail/notes | 通过/失败 | xxx |

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

### 范围偏差检查

- [ ] 是否所有开发内容都对应 FR 编号？
- [ ] 是否存在未定义的新功能？
- [ ] 是否存在后端有能力但前端无入口？
- [ ] 是否存在 API 字段与文档不一致？
- [ ] 是否存在 Must Have 未完成但被标记完成？
- [ ] 是否存在只通过 localStorage 实现的历史能力？
- [ ] 是否存在只能手填 case_id、没有案例库 UI 的情况？

### 验收结论

结论只能选择一项：

- [ ] 通过
- [ ] 有条件通过
- [ ] 不通过

结论说明：

```text
填写说明。
```

---

