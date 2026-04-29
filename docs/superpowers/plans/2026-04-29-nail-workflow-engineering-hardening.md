# Nail Workflow Engineering Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stabilize the nail note workflow around reference resolution, image-generation side effects, diagnostics, QA, real integration scripts, and a future service-facing API without breaking the verified real image generation path.

**Architecture:** Introduce a note-level `ReferenceContext` that resolves reference state exactly once, thread it through image generation and orchestrator calls, and separate per-image side effects from note-level packaging. Add structured timing/reference diagnostics to the note package and expose a service wrapper with request/response schemas for future Web/App callers.

**Tech Stack:** Python 3.9, Pydantic, unittest, ThreadPoolExecutor, existing orchestrator/image generation modules.

---

### Task 1: Lock current behavior with tests

**Files:**
- Create: `tests/test_nail_reference_context.py`
- Modify: `tests/test_nail_acceptance_regressions.py`
- Create: `tests/test_nail_service_models.py`

- [ ] Add tests for conflicting `reference_image_path` + `case_id`, local path resolution, case ID resolution, `save_case=False`, `archive_mode="none"`, and service DTO conversion.
- [ ] Run targeted tests to verify the new tests fail for the expected reasons before implementation.

### Task 2: Add note-level ReferenceContext

**Files:**
- Create: `verticals/nail/reference_context.py`
- Modify: `verticals/nail/visual_dna_builder.py`
- Modify: `verticals/nail/note_workflow.py`

- [ ] Implement `ReferenceContext` and `build_reference_context()` with explicit conflict handling, local path resolution, case metadata loading, and DNA summary extraction.
- [ ] Update the workflow to resolve reference context once and reuse it for VisualDNA, image generation, diagnostics, and QA.

### Task 3: Refactor note image generation for reference reuse and timing

**Files:**
- Modify: `verticals/nail/note_image_generator.py`
- Modify: `verticals/nail/note_workflow_schemas.py`

- [ ] Add `max_workers` to `NailNoteUserInput`.
- [ ] Thread `reference_context` through `generate_note_images()` and `_generate_single_page()`.
- [ ] Add sequential/limited-parallel generation, per-page timing capture, stable page ordering, and structured page failures.

### Task 4: Harden orchestrator reference handling and side effects

**Files:**
- Modify: `orchestrator_v2.py`
- Modify: `case_reference_resolver.py` if needed

- [ ] Extend `run()` with backward-compatible parameters for resolved reference paths, archive control, save-case control, and request IDs.
- [ ] Ensure image-to-image truly uses the reference image path and that `case_id` resolution only happens when needed.
- [ ] Disable case-library pollution for note workflows and skip per-image archive writes when `archive_mode="none"` or `"note_only"`.
- [ ] Return richer diagnostics, timing, and reference metadata.

### Task 5: Improve prompt structure and QA layering

**Files:**
- Modify: `verticals/nail/page_prompt_builder.py`
- Modify: `verticals/nail/note_qa.py`
- Modify: `verticals/nail/package_writer.py`

- [ ] Reorganize prompt composition into shared DNA, page delta, and output requirements while keeping existing constraints.
- [ ] Expand QA into structure/content/image/reference scoring with warnings and issues.
- [ ] Ensure diagnostics, QA scores, and reference/timing details are serialized into `note_package.json`.

### Task 6: Add service-facing API models and job store

**Files:**
- Create: `verticals/nail/service/__init__.py`
- Create: `verticals/nail/service/schemas.py`
- Create: `verticals/nail/service/job_store.py`
- Create: `verticals/nail/service/nail_note_service.py`

- [ ] Define Pydantic request/response/page summary models for future Web/App callers.
- [ ] Add a minimal in-memory/local JSON job store and status lifecycle helpers.
- [ ] Implement synchronous `create_nail_note()` that converts requests to workflow input and returns structured diagnostics.

### Task 7: Fix real integration script contract and docs

**Files:**
- Modify: `scripts/run_real_nail_image_integration.py`
- Modify: `scripts/run_real_nail_ref_image_integration.py`
- Create: `scripts/run_real_nail_case_id_integration.py`
- Create: `docs/nail_real_image_tests.md`
- Create: `docs/nail_web_app_readiness.md`

- [ ] Split the three script entry points so `none`, `local_path`, and `case_id` references are explicit and logged.
- [ ] Add the `RUN_REAL_IMAGE_TESTS=1` guard.
- [ ] Document usage, outputs, diagnostics, performance guidance, and the new service layer.

### Task 8: Verify end-to-end and commit cleanly

**Files:**
- Verify only

- [ ] Run targeted unit tests during each TDD cycle.
- [ ] Run `python3 -m unittest discover -v` as the final proof.
- [ ] Review `git status` so only intended tracked files are staged; avoid the existing untracked case-library artifacts.
