# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Multi-Agent Image Generation System — a multi-agent workflow that generates images using GPT-Image-2 via the apimart.ai API. The system compiles design prompts, generates images (text-to-image or image-to-image with reference), and maintains a case library for style reuse.

## Common Commands

```bash
# Text-to-image generation
python gpt_image2_generator.py 'your prompt here' 3:4

# Image-to-image (img2img) with reference
python apimart_image_url_generator.py  # use generate_image_with_reference()

# Run the full orchestrator workflow
python orchestrator_v2.py

# Interactive mode
python interactive_run.py

# Quick start
python quick_start.py

# Batch generation
python batch_generator_v2.py

# Case library
python case_library.py list
python case_library.py search <keyword>
```

## Architecture

### Main Workflow (orchestrator_v2.py)

5-stage pipeline:
1. **Prompt Engineer** (`step1_prompt_engineer`) — lightweight text pass-through (fallback mode)
2. **Style Scout** (`step2_style_scout`) — selects task type, direction, aspect, quality
3. **Image Generator** (`step3_image_generator`) — compiles prompt via `design_compiler` + calls GPT-Image-2 API
4. **QA** (`step4_qa`) — pass/fail quality check
5. **Metadata Archiver** (`step5_metadata`) — saves archive JSON to `output/`

Generated images are auto-saved to the case library with metadata.

### Image Generation

- `gpt_image2_generator.py` — text-to-image via `https://api.apimart.ai/v1/images/generations`
- `apimart_image_url_generator.py` — image-to-image (img2img) with reference image upload + task polling

Both support async task submission → polling → download workflow.

### Design Compiler (design_compiler.py)

Compiles structured prompts from:
- **5 task profiles**: `poster`, `product`, `ppt`, `infographic`, `teaching`
- **3 direction profiles**: `conservative`, `balanced`, `bold`
- **Aspect ratios**: 1:1, 3:4, 4:3, 16:9, 9:16, etc.
- **Quality tiers**: draft (2K), final, premium (3K)

### Case Library (case_library.py)

Organized under `case_library/{task}/` (poster/product/ppt/infographic/teaching).
Each case: `case_XXX_name/image.png + metadata.json`
Supports: add, list, search, interactive select, auto-save from generation results.

### Path Management (project_paths.py)

Centralizes: `PROJECT_ROOT`, `OUTPUT_DIR`, `CASE_LIBRARY_DIR`
Key utilities: `to_project_relative()`, `resolve_project_path()`

## Environment Variables

```bash
OPENAI_API_KEY          # primary API key
APIMART_API_KEY         # fallback API key
APIMART_API_BASE        # optional, defaults to https://api.apimart.ai
```

## Key Data Flow

```
User Input → Orchestrator
           → Prompt Engineer → Style Scout → Design Compiler → Image Generator
                                                              ↓
           ← QA ← Metadata Archiver ← Case Library ← Image Result
```

Image Generator branches:
- **No reference** → `gpt_image2_generator.generate_image()` (text-to-image)
- **With reference** → `apimart_image_url_generator.generate_image_with_reference()` (img2img)

Results are normalized via `_normalize_generation_result()` to handle both API return formats.

## Agent Directories

Subdirectories with `memory.json` + `role.md`: `image_generator/`, `prompt_engineer/`, `style_scout/`, `qa_bot/`, `metadata_manager/`, `refiner/`, `tools/` — context files for agent roles, not active code.
