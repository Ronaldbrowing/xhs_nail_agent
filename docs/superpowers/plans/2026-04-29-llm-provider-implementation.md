# LLMProvider Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Introduce a unified `LLMProvider` runtime for text and image model configuration, supporting both `openai` and `apimart` without leaking provider details into business modules.

**Architecture:** Add a single `src/llm_provider.py` registry/config layer, migrate all OpenAI-compatible client creation to that layer, and replace hardcoded model strings with stable alias lookups. Keep provider secrets server-side and preserve current workflow entrypoints.

**Tech Stack:** Python 3, `openai` Python SDK, `unittest`, environment-variable configuration, existing workflow modules.

---

## File Structure

- Create: `src/llm_provider.py`
- Create: `tests/test_llm_provider.py`
- Modify: `gpt_image2_generator.py`
- Modify: `apimart_image_url_generator.py`
- Modify: `verticals/nail/title_generator.py`
- Modify: `verticals/nail/caption_generator.py`
- Modify: `verticals/nail/tag_generator.py`
- Modify: `verticals/nail/comment_hook_generator.py`
- Modify: `verticals/nail/note_planner.py`
- Modify: `verticals/nail/visual_dna_builder.py`
- Modify: `verticals/nail/vision_analyze_helper.py`
- Modify: `verticals/nail/note_workflow.py`
- Modify: `README.md`
- Modify: `docs/ARCHITECTURE.md`

## Task 1: Add provider runtime tests

**Files:**
- Create: `tests/test_llm_provider.py`

- [ ] **Step 1: Write failing tests for provider config and model aliases**
- [ ] **Step 2: Run `python3 -m unittest tests.test_llm_provider -v` and verify failure**
- [ ] **Step 3: Implement minimal `src/llm_provider.py` to satisfy config tests**
- [ ] **Step 4: Re-run the targeted test and verify pass**

## Task 2: Migrate text client factories

**Files:**
- Modify: `verticals/nail/title_generator.py`
- Modify: `verticals/nail/caption_generator.py`
- Modify: `verticals/nail/tag_generator.py`
- Modify: `verticals/nail/comment_hook_generator.py`
- Modify: `verticals/nail/note_planner.py`
- Modify: `verticals/nail/visual_dna_builder.py`
- Modify: `verticals/nail/vision_analyze_helper.py`
- Test: `tests/test_llm_provider.py`

- [ ] **Step 1: Add failing regression tests asserting alias-based model resolution and APIMART base URL default**
- [ ] **Step 2: Run the targeted tests and verify failure**
- [ ] **Step 3: Replace per-file `_get_openai_client()` logic with `src.llm_provider` helpers**
- [ ] **Step 4: Re-run the targeted tests and verify pass**

## Task 3: Migrate image provider configuration

**Files:**
- Modify: `gpt_image2_generator.py`
- Modify: `apimart_image_url_generator.py`
- Test: `tests/test_llm_provider.py`

- [ ] **Step 1: Add failing tests for image provider defaults and API key resolution**
- [ ] **Step 2: Run the targeted tests and verify failure**
- [ ] **Step 3: Move image base URL, key lookup, and default image model into `src.llm_provider.py`**
- [ ] **Step 4: Re-run the targeted tests and verify pass**

## Task 4: Preserve workflow compatibility

**Files:**
- Modify: `verticals/nail/note_workflow.py`
- Modify: `tests/test_nail_acceptance_regressions.py`

- [ ] **Step 1: Add a failing smoke test that `NailNoteWorkflow` still succeeds with provider-backed config**
- [ ] **Step 2: Run `python3 -m unittest tests.test_nail_acceptance_regressions -v` and verify failure if needed**
- [ ] **Step 3: Apply the minimal compatibility fix in `note_workflow.py`**
- [ ] **Step 4: Re-run the smoke/regression tests and verify pass**

## Task 5: Update user-facing docs after code matches behavior

**Files:**
- Modify: `README.md`
- Modify: `docs/ARCHITECTURE.md`

- [ ] **Step 1: Update README environment variable and provider setup sections**
- [ ] **Step 2: Update architecture docs to describe `LLMProvider` and server-side key boundary**
- [ ] **Step 3: Run a grep-based verification for stale `new.apipudding.com` or single-provider docs**

## Task 6: Final verification

**Files:**
- Test: `tests/test_llm_provider.py`
- Test: `tests/test_nail_acceptance_regressions.py`

- [ ] **Step 1: Run `python3 -m unittest tests.test_llm_provider -v`**
- [ ] **Step 2: Run `python3 -m unittest tests.test_nail_acceptance_regressions -v`**
- [ ] **Step 3: Run `rg -n "new\\.apipudding|OPENAI_API_KEY" verticals/nail gpt_image2_generator.py apimart_image_url_generator.py README.md docs/ARCHITECTURE.md` and inspect results**
- [ ] **Step 4: Commit the implementation intentionally**
