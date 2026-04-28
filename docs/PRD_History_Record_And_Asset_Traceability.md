在正式进入 NailNoteWorkflow Phase 1 前，新增 Phase 0.5：History Record & Asset Traceability。

目标：
从未来前端 app / web 页面出发，建立完整历史记录和资产归档规范。历史记录不仅要保存生成图，还要保存用户输入、参考图、系统规划、prompt、页面产物、文案、QA、workflow trace、metrics、lineage 和前端列表索引。

核心要求：
1. 每次任务创建独立 record_dir：
   output/records/{record_id}/

2. record_dir 下至少包含：
   - note_package.json 或 generation_package.json
   - archive.json
   - input.json
   - workflow_trace.json
   - assets/references/
   - assets/generated/
   - assets/thumbnails/
   - qa/

3. 新增或扩展数据结构：
   - RecordMeta
   - ReferenceAsset
   - GeneratedAsset
   - PagePackage
   - CopywritingPackage
   - QualityReport
   - WorkflowTrace
   - HistoryIndexItem
   - NailNotePackage

4. 所有资产路径必须使用项目相对路径，不允许写入绝对路径。

5. 参考图必须支持数组 references[]，即使当前只使用一张参考图。

6. 每张参考图必须保存：
   - reference_id
   - enabled
   - source_type
   - source_value
   - source_task
   - source_record_id
   - original_path
   - archived_path
   - thumbnail_path
   - filename
   - content_type
   - file_size
   - width
   - height
   - sha256
   - exists
   - usage_policy
   - influence_scope
   - dna

7. 每个生成页面 pages[] 必须保存：
   - page_id
   - page_index
   - role
   - title
   - goal
   - status
   - image.path
   - image.thumbnail_path
   - image.url
   - image.width
   - image.height
   - image.ratio
   - image.content_type
   - image.file_size
   - image.sha256
   - reference_ids
   - used_reference
   - prompt.visual_brief
   - prompt.final_prompt
   - prompt.negative_prompt
   - generation.mode
   - generation.provider
   - generation.model
   - generation.task_id
   - generation.started_at
   - generation.completed_at
   - generation.duration_ms
   - generation.retry_count
   - qa.score
   - qa.passed
   - qa.issues
   - qa.checks

8. 顶层 note_package.json 必须保存：
   - record_id
   - record_type
   - schema_version
   - workflow_name
   - workflow_version
   - status
   - created_at
   - updated_at
   - input
   - references
   - planning
   - visual_dna
   - prompts
   - pages
   - copywriting
   - quality
   - workflow_trace
   - metrics
   - lineage
   - user_feedback
   - display
   - files

9. input 必须保存用户原始输入，不要只保存系统改写后的 prompt。至少包含：
   - brief
   - style_id
   - note_goal
   - page_count
   - skin_tone
   - nail_length
   - nail_shape
   - color_preference
   - avoid_elements
   - allow_text_on_image
   - generate_images
   - generate_copy
   - generate_tags
   - language

10. planning 必须保存系统理解和规划结果。至少包含：
   - detected_intent
   - matched_style_id
   - matched_style_reason
   - target_audience
   - content_angle
   - visual_strategy
   - copy_strategy
   - page_plan

11. prompts 必须保存多层 prompt，不要只保存最终 prompt。至少包含：
   - global_prompt
   - negative_prompt
   - template_id
   - template_version
   - compiled_at
   - pages[].visual_brief
   - pages[].final_prompt
   - pages[].negative_prompt
   - pages[].allow_text_on_image

12. copywriting 必须保存小红书发布所需文案。至少包含：
   - titles[]
   - selected_title
   - caption.opening
   - caption.body
   - caption.ending
   - caption.full_text
   - tags[]
   - comment_hooks[]

13. quality 必须保存维度化质量评估，不要只保存一个 score。至少包含：
   - overall_score
   - passed
   - grade
   - dimensions.visual_quality
   - dimensions.nail_detail
   - dimensions.style_match
   - dimensions.reference_alignment
   - dimensions.xiaohongshu_fit
   - dimensions.copy_quality
   - dimensions.publish_readiness
   - issues[]
   - suggestions[]

14. workflow_trace 必须保存每个阶段的状态、耗时和错误信息。至少包含：
   - stages[]
   - diagnostics.prompt_ok
   - diagnostics.reference_ok
   - diagnostics.generation_ok
   - diagnostics.quality_ok
   - diagnostics.archive_ok

15. metrics 必须保存基础性能与调用统计。至少包含：
   - total_duration_ms
   - image_generation_duration_ms
   - copy_generation_duration_ms
   - qa_duration_ms
   - api_calls.image_generation
   - api_calls.image_upload
   - api_calls.llm_copy
   - estimated_cost.currency
   - estimated_cost.amount
   - retry_count

16. lineage 必须保存记录血缘和复用关系。至少包含：
   - parent_record_id
   - derived_from_record_id
   - derived_from_page_id
   - reused_reference_ids
   - saved_to_case_library
   - case_ids
   - regeneration_of
   - variant_group_id

17. user_feedback 先预留结构，方便后续前端接入。至少包含：
   - favorite
   - rating
   - selected_pages
   - selected_title_id
   - notes
   - rejected_reason
   - created_case_from_record

18. display 必须提供前端列表页直接可用的轻量展示字段。至少包含：
   - title
   - subtitle
   - cover_image_path
   - reference_thumbnail_path
   - badge_text
   - style_label
   - status_label
   - score_label
   - search_text

19. 新增 history_index.jsonl：
   路径：
   output/records/history_index.jsonl

   每次生成完成后追加一行 HistoryIndexItem，用于前端历史列表快速加载。字段至少包含：
   - record_id
   - record_type
   - schema_version
   - created_at
   - updated_at
   - status
   - title
   - brief
   - style_id
   - style_label
   - note_goal
   - page_count
   - cover_image_path
   - reference_thumbnail_path
   - used_reference
   - overall_score
   - package_path
   - search_text

20. 参考图归档要求：
   - 当传入 reference_image 或通过 case_id 解析出参考图时，必须复制到当前 record_dir/assets/references/
   - archived_path 必须是项目相对路径
   - 如果能生成缩略图，则写入 thumbnail_path
   - 如果暂时不能生成缩略图，thumbnail_path 可以为 null，但字段必须存在
   - 原始路径只用于溯源，前端展示必须优先使用 archived_path 或 thumbnail_path
   - 不允许前端依赖本地绝对路径或远程临时 URL

21. 生成图归档要求：
   - 每张生成图必须复制或保存到 record_dir/assets/generated/
   - 每张生成图必须有 GeneratedAsset 结构
   - 如果是多页笔记，每页 image.path 必须指向自己的页面图片
   - 如果生成失败，该页仍然要保留 PagePackage，并写入 status=failed 和 error 信息

22. 缩略图要求：
   - 优先为参考图和生成图生成缩略图
   - 缩略图放到 record_dir/assets/thumbnails/ 或 assets/references/
   - 缩略图失败不应导致主流程失败，但 workflow_trace 中应记录 warning
   - 若当前阶段暂不实现缩略图生成，字段保留为 null

23. archive.json 要求：
   - archive.json 可以是完整 note_package 的压缩版或兼容版
   - 但必须包含 record_id、input、references、pages、quality、files
   - archive.json 中的路径同样必须是项目相对路径

24. 兼容现有基础单图链路：
   - 不破坏 orchestrator_v2.run() 的原有调用方式
   - 不破坏 NailWorkflow 的现有入口
   - 如果只是单图生成，也应生成 generation_package.json 或兼容的 note_package.json
   - 单图生成可以只有一个 page：
     page_id = "page_01"
     role = "single_image"
     page_index = 1

25. used_reference 语义必须保持严格：
   - used_reference=true 只能表示真实图生图分支成功使用了参考图
   - 不能退化成 bool(reference_image)
   - 如果参考图传入但路径无效，应写入 reference.exists=false，并在 diagnostics 中标记 reference_ok=false
   - 如果图生图失败后 fallback 到文生图，used_reference 必须为 false，同时要记录 fallback_reason

26. 错误和失败记录要求：
   - 即使任务失败，也要尽可能写入 record_dir 和 archive.json
   - status 可以为 failed 或 partial_success
   - error 必须包含用户可读 message 和开发可调试 detail
   - workflow_trace.stages[] 必须记录失败阶段
   - history_index.jsonl 也应追加失败记录，方便前端显示失败任务

27. 路径安全要求：
   - 所有输出路径必须使用 project_paths.to_project_relative()
   - 不允许写入 /Users/wiwi、Path.home()、~/.hermes、multi-agent-image 等旧路径
   - 不允许把 API Key、环境变量、完整本地用户目录写入 package
   - 如需调试信息，可放入 debug 字段，但默认前端不展示

28. 建议新增模块：
   - record_manager.py
   - asset_manager.py
   - history_index.py

   其中：
   record_manager.py 负责 record_id、record_dir、package 写入
   asset_manager.py 负责参考图、生成图、缩略图、hash、尺寸等资产归档
   history_index.py 负责追加 history_index.jsonl

29. 建议 record_id 格式：
   nail_YYYYMMDD_HHMMSS_{short_hash}

   示例：
   nail_20260429_000120_a1b2c3

   对于单图基础链路，可使用：
   image_YYYYMMDD_HHMMSS_{short_hash}

30. 最小验收命令一：无参考图文生图

运行一个无参考图任务，验证：
   - result.success == true
   - result.used_reference == false
   - result.references == [] 或 references[].enabled=false
   - 创建 output/records/{record_id}/
   - 生成 package json
   - 生成 archive.json
   - 生成 assets/generated/
   - history_index.jsonl 新增一行
   - 所有路径均为项目相对路径

31. 最小验收命令二：本地 reference_image 图生图

运行一个带本地参考图的任务，验证：
   - result.success == true
   - result.used_reference == true
   - references[0].enabled == true
   - references[0].archived_path 以 output/records/ 开头
   - archived_path 文件真实存在
   - pages[0].reference_ids 包含 ref_001
   - pages[0].used_reference == true
   - archive.json 中包含 references
   - history_index.jsonl 中 used_reference == true

32. 最小验收命令三：case_id 图生图

运行一个通过 case_id 解析参考图的任务，验证：
   - 能从 case_library 找到参考图
   - references[0].source_type == "case_id"
   - references[0].source_value == case_id
   - references[0].original_path 指向 case_library 下的项目相对路径
   - references[0].archived_path 指向 output/records/ 下的归档副本
   - used_reference == true

33. 最小验收命令四：无效参考图（fallback 到文生图）

运行一个传入但无效的 reference_image，验证：
   - used_reference=false（不错误标记为 true）
   - 如走 fallback 到文生图：status=success，generation.mode=text_to_image
   - 如走直接失败：status=failed，references=[]，workflow_trace 记录 failed_stage
   - diagnostics.reference_ok == false 或 workflow_trace 中有 reference warning
   - fallback_reason 必须记录（如 "reference_image_not_found"）
   - 不允许错误标记 used_reference=true

34. grep 审计：
   执行：
   grep -RIn "\.hermes\|multi-agent-image\|Path.home()\|/Users/wiwi\|/root/.hermes" \
     --exclude-dir=.git \
     --exclude-dir=.venv \
     --exclude="*.bak*" \
     .

   要求：
   - 核心运行链路不出现旧路径硬编码
   - 新增 record / asset / history 模块不出现绝对路径硬编码
