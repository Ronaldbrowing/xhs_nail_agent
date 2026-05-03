# Nail Web MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a same-origin FastAPI-hosted static Web MVP for creating nail note jobs, polling job status, and previewing note packages without changing the image-generation backend workflow.

**Architecture:** FastAPI will continue serving the existing JSON API while also serving one static HTML page plus JS/CSS assets from `verticals/nail/web/`. The browser app will submit requests to the existing `/api/nail/notes` endpoint, poll `/api/jobs/{job_id}`, then fetch `/api/nail/notes/{note_id}/package` and render metadata and page cards/images.

**Tech Stack:** FastAPI, Starlette static/file responses, vanilla HTML/CSS/JS, Python unittest with FastAPI TestClient.

---

### Task 1: Add failing tests for web asset hosting

**Files:**
- Modify: `tests/test_nail_api.py`
- Modify: `verticals/nail/api/app.py`
- Create: `verticals/nail/web/index.html`
- Create: `verticals/nail/web/app.js`
- Create: `verticals/nail/web/style.css`

- [ ] **Step 1: Write the failing tests**
- [ ] **Step 2: Run `python3 -m unittest tests.test_nail_api -v` and confirm the new web tests fail**
- [ ] **Step 3: Implement `GET /`, `/web/app.js`, `/web/style.css`, and HTML references**
- [ ] **Step 4: Re-run `python3 -m unittest tests.test_nail_api -v` and confirm they pass**

### Task 2: Implement browser workflow UI

**Files:**
- Create: `verticals/nail/web/index.html`
- Create: `verticals/nail/web/app.js`
- Create: `verticals/nail/web/style.css`

- [ ] **Step 1: Add a form with brief/style/skin_tone/nail_length/generate_images/max_workers fields**
- [ ] **Step 2: Implement payload sanitization, job polling with timeout/failure exit, and package rendering**
- [ ] **Step 3: Render image cards only from safe `output/...` paths and render placeholders when images are absent**
- [ ] **Step 4: Keep defaults at `generate_images=false` and `max_workers=1`**

### Task 3: Verify API smoke flow still works

**Files:**
- Modify: `tests/test_nail_api.py`
- Modify: `verticals/nail/api/app.py`
- Create: `verticals/nail/web/index.html`
- Create: `verticals/nail/web/app.js`
- Create: `verticals/nail/web/style.css`

- [ ] **Step 1: Run `python3 -m unittest tests.test_nail_api -v`**
- [ ] **Step 2: Run `python3 -m unittest discover -v`**
- [ ] **Step 3: Run `python3 scripts/smoke_fastapi_api.py`**
- [ ] **Step 4: Capture startup command, route URLs, and one `generate_images=false` manual flow summary**
