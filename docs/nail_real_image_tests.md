# Nail Real Image Tests

真实图片集成测试默认不会调用 API。只有显式加上 `RUN_REAL_IMAGE_TESTS=1` 才会真的发起请求。

## 运行方式

无参考图链路：

```bash
RUN_REAL_IMAGE_TESTS=1 python3 scripts/run_real_nail_image_integration.py
RUN_REAL_IMAGE_TESTS=1 python3 scripts/run_real_nail_image_integration.py --max-workers 2
```

本地参考图链路：

```bash
RUN_REAL_IMAGE_TESTS=1 python3 scripts/run_real_nail_ref_image_integration.py
RUN_REAL_IMAGE_TESTS=1 python3 scripts/run_real_nail_ref_image_integration.py output/nail_xxx/page_01_cover.png
```

`case_id` 案例复用链路：

```bash
RUN_REAL_IMAGE_TESTS=1 python3 scripts/run_real_nail_case_id_integration.py --case-id case_038
RUN_REAL_IMAGE_TESTS=1 python3 scripts/run_real_nail_case_id_integration.py --case-id case_038 --max-workers 2
```

## 三类 reference source

- `reference_source=none`
  纯文生图，不传 `reference_image_path` 和 `case_id`。
- `reference_source=local_path`
  只传本地参考图，必须打印 `reference_image_path=...` 和 `case_id=None`。
- `reference_source=case_id`
  只传案例库 ID，必须打印 `case_id=...` 和 `reference_image_path=None`。

## 输出目录

每次运行都会在 `output/nail_*` 下生成一份笔记结果目录，至少包含：

- `note_package.json`
- `archive.json`
- `page_01_cover.png` 到其余页面图片

## note_package.json 关键字段

- `success`
- `partial_failure`
- `output_dir`
- `package_path`
- `archive_path`
- `pages`
- `diagnostics.reference`
- `diagnostics.timing`
- `diagnostics.page_timings`
- `diagnostics.generation_mode`
- `diagnostics.qa_score`

## diagnostics 说明

`diagnostics.reference`
- `source_type`: `none` / `local_path` / `case_id`
- `case_id`
- `reference_image_path`
- `resolved_image_path`
- `dna_summary_included`

`diagnostics.timing`
- `workflow_started_at`
- `workflow_finished_at`
- `workflow_duration_sec`
- `image_generation_duration_sec`
- `avg_page_generation_sec`

`diagnostics.page_timings`
- `page_no`
- `role`
- `status`
- `duration_sec`
- `used_reference`
- `image_path`

## 性能建议

- 串行 `max_workers=1`：最稳定，适合日常验收，但 6 页通常更慢。
- 有限并发 `max_workers=2`：通常更快，但更容易触发 API 限流或上游波动。
- `quality="draft"`：适合测试。
- `quality="final"` 或 `premium`：适合生产出图。
