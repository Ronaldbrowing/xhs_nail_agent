# Nail Web/App Readiness

当前仓库已经为下一阶段的 Web 端或手机 App 调用准备了轻量服务层，重点不是先上框架，而是先把接口模型、任务状态和 diagnostics 稳定下来。

## Service 入口

文件：

- `verticals/nail/service/schemas.py`
- `verticals/nail/service/nail_note_service.py`
- `verticals/nail/service/job_store.py`

同步入口：

```python
from verticals.nail.service.nail_note_service import create_nail_note
from verticals.nail.service.schemas import NailNoteCreateRequest

response = create_nail_note(
    NailNoteCreateRequest(
        brief="夏日蓝色猫眼短甲",
        generate_images=True,
        reference_image_path=None,
        case_id=None,
        max_workers=1,
    )
)
```

## Request 模型

`NailNoteCreateRequest`

- `brief`
- `style_id`
- `skin_tone`
- `nail_length`
- `nail_shape`
- `note_goal`
- `page_count`
- `generate_images`
- `generate_copy`
- `generate_tags`
- `quality`
- `aspect`
- `direction`
- `reference_image_path`
- `case_id`
- `max_workers`

这个请求模型可以直接转换为 `NailNoteUserInput`，后续接 FastAPI、Flask、云函数或移动端后端都不需要再自己拼 workflow 参数。

## Response 模型

`NailNoteCreateResponse`

- `request_id`
- `note_id`
- `status`
- `package_path`
- `output_dir`
- `success`
- `partial_failure`
- `qa_score`
- `pages`
- `diagnostics`
- `errors`

推荐前端直接读取 `diagnostics.reference`、`diagnostics.timing` 和 `diagnostics.page_timings` 来展示任务进度、耗时、引用来源和失败页。

## Job Store

当前 `job_store.py` 先使用内存字典并同步写一份本地 JSON，支持：

- `create_job()`
- `update_job()`
- `get_job()`
- `list_jobs()`

状态枚举：

- `queued`
- `running`
- `succeeded`
- `failed`
- `partial_failed`

## 当前后端稳定能力

- `generate_images=False` 仍能生成完整发布包。
- `reference_image_path` 与 `case_id` 口径已分离。
- Note 级 reference 只解析一次，多页复用。
- `save_case=False` 可避免 6 页工作流污染通用案例库。
- `archive_mode="note_only"` 可避免每页单独写 per-image archive。
- `note_package.json` 包含结构化 diagnostics，适合前端直接消费。

## 下一阶段接入建议

- 先在后端包一层 HTTP API，把 `create_nail_note()` 暴露成同步或异步接口。
- 异步模式优先，前端只提交请求并轮询 `request_id`。
- 上传本地参考图时，先由后端保存文件，再把保存后的路径填进 `reference_image_path`。
- `case_id` 适合做“从案例库中选模板继续生成”的 UI 入口。
- Web/App 展示页建议优先展示：
  - `status`
  - `qa_score`
  - `diagnostics.reference`
  - `diagnostics.timing`
  - `diagnostics.page_timings`
  - `pages[].image_path`
