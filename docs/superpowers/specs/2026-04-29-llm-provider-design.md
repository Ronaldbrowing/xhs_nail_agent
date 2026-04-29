# LLMProvider Unified Configuration Design

Date: 2026-04-29

Status: Proposed, pre-implementation

Owner: Codex

## Goal

Unify all LLM and image-model configuration behind a single `LLMProvider` abstraction so the workflow can run against any OpenAI-compatible backend, not just OpenAI official endpoints.

This design must support:

- at least two providers immediately: `openai` and `apimart`
- current server-side CLI workflow
- future Web and mobile app access through a backend-managed workflow API
- future UI-based provider and model configuration without changing business logic modules

## Why This Change Is Needed

The current codebase mixes provider concerns directly into business modules:

- text modules independently read `OPENAI_API_KEY`
- image modules partially use `APIMART_API_KEY` and partially fall back to `OPENAI_API_KEY`
- provider base URLs are inconsistent, including legacy `new.apipudding.com`
- model names like `gpt-4o-mini` are hardcoded in multiple files
- there is no single place to express “use provider X with model aliases Y”

This makes the current workflow hard to operate, hard to extend, and hard to expose safely to a frontend.

## Design Principles

1. Business modules should not know which provider is active.
2. Business modules should ask for a capability or model alias, not a concrete vendor model name.
3. Provider credentials must remain server-side only.
4. Configuration should work from environment variables now and be easy to replace with database-backed UI configuration later.
5. OpenAI-compatible providers should share one client factory whenever possible.

## Scope

This design covers:

- text generation provider selection
- vision/text multimodal provider selection when using the OpenAI-compatible SDK
- image generation provider configuration
- model alias mapping for business workflows
- server-side configuration boundaries for future app integration

This design does not yet cover:

- non-OpenAI-compatible native SDK adapters
- tenant-level persisted UI configuration storage
- per-user billing or provider quotas

## Recommended Architecture

Introduce a provider registry layer and make all current business modules consume it.

### New Core Concepts

#### 1. Provider Profile

A provider profile describes how to talk to one backend.

Suggested fields:

- `provider_id`
- `label`
- `api_base`
- `api_key_env`
- `api_key`
- `sdk_type`
- `supports_chat_completions`
- `supports_responses`
- `supports_images`
- `supports_async_tasks`
- `default_models`

For the first implementation, `sdk_type` can be `openai_compatible`.

#### 2. Model Alias Map

Business code should use stable aliases instead of vendor model names.

Suggested aliases:

- `planner_small`
- `copy_small`
- `tag_small`
- `hook_small`
- `vision_small`
- `image_default`

Example mapping:

- `openai.copy_small -> gpt-4o-mini`
- `apimart.copy_small -> gpt-4o-mini`
- `apimart.image_default -> gpt-image-2`

This keeps product logic stable when changing providers or models later.

#### 3. Unified Provider Runtime

Add a single runtime entrypoint that resolves:

- active provider
- provider credentials
- provider base URL
- concrete model name for a given alias

Business modules should call helpers such as:

- `get_text_client()`
- `get_text_model(alias)`
- `get_image_provider_config()`

## Provider Strategy

### Provider 1: OpenAI

- base URL: official SDK default
- credentials: `OPENAI_API_KEY`
- use when `LLM_PROVIDER=openai`

### Provider 2: APIMART

- base URL: `https://api.apimart.ai/v1`
- credentials: `APIMART_API_KEY`
- use when `LLM_PROVIDER=apimart`
- use the same OpenAI Python SDK client with `base_url` overridden

This matches APIMART’s documented OpenAI-compatible integration model.

## Configuration Model

### Immediate Environment Variable Layer

The first implementation should support:

- `LLM_PROVIDER`
- `OPENAI_API_KEY`
- `OPENAI_API_BASE`
- `APIMART_API_KEY`
- `APIMART_API_BASE`
- `TEXT_MODEL_PLANNER_SMALL`
- `TEXT_MODEL_COPY_SMALL`
- `TEXT_MODEL_TAG_SMALL`
- `TEXT_MODEL_HOOK_SMALL`
- `TEXT_MODEL_VISION_SMALL`
- `IMAGE_MODEL_DEFAULT`

Defaults should be provider-aware.

For APIMART, `APIMART_API_BASE` should default to:

`https://api.apimart.ai/v1`

### Future UI Configuration Layer

The design should anticipate a backend configuration source such as:

- JSON config file
- database table
- admin panel form

The implementation should therefore keep configuration loading behind a single function or class so env vars can later be replaced by:

- workspace-level settings
- deployment-level settings
- tenant-level settings

without touching the workflow modules.

## Frontend and Mobile App Boundary

Future Web or mobile apps must not call upstream LLM providers directly.

Required backend pattern:

1. frontend calls our backend
2. backend loads active provider config
3. backend executes workflow
4. backend returns workflow result package

Reasons:

- API keys remain server-side
- provider routing stays centralized
- model alias changes do not require frontend redeploys
- usage control and auditability remain possible

For later productization, the backend can expose a config surface like:

- active provider
- visible provider options
- model alias overrides
- image provider options

The frontend should only send business inputs, not raw provider secrets.

## Module Refactor Plan

### New Module

Create a new module, likely under `src/` or repo root:

- `src/llm_provider.py`

Responsibilities:

- load provider profiles
- resolve active provider
- construct OpenAI-compatible clients
- resolve text and image model aliases
- expose safe runtime metadata

### Existing Modules to Move Onto LLMProvider

Text-related:

- `verticals/nail/title_generator.py`
- `verticals/nail/caption_generator.py`
- `verticals/nail/tag_generator.py`
- `verticals/nail/comment_hook_generator.py`
- `verticals/nail/note_planner.py`
- `verticals/nail/visual_dna_builder.py`
- `verticals/nail/vision_analyze_helper.py`
- `verticals/nail/note_workflow.py`

Image-related:

- `gpt_image2_generator.py`
- `apimart_image_url_generator.py`

Documentation:

- `README.md`
- `docs/ARCHITECTURE.md`

## API Shape Recommendation

Keep the first implementation simple.

Suggested Python surface:

```python
from src.llm_provider import (
    get_active_provider,
    get_openai_compatible_client,
    get_model_name,
    get_image_settings,
)

client = get_openai_compatible_client()
model = get_model_name("copy_small")
```

Recommended behavior:

- if provider is `openai`, create `OpenAI(api_key=...)`
- if provider is `apimart`, create `OpenAI(base_url=..., api_key=...)`
- if provider is unknown, fail clearly

## Error Handling

Configuration errors must fail early and clearly.

Required examples:

- unknown `LLM_PROVIDER`
- missing provider API key
- missing model alias mapping
- provider selected for text but no text capability declared

Failure messages should say which provider was selected and which variable or alias is missing.

## Backward Compatibility

The refactor should preserve current workflow entrypoints:

- `orchestrator_v2.run()`
- `verticals.nail.note_workflow.NailNoteWorkflow`
- existing CLI scripts

Behavior changes should be limited to configuration loading and provider resolution.

No caller should need to import provider internals just to run the workflow.

## Documentation Plan

Implement in this order:

1. add this design doc
2. implement provider abstraction
3. update README to describe runtime configuration
4. update architecture doc to describe provider registry and server-only key boundary

This prevents README from describing behavior that does not yet exist.

## Testing Plan

Minimum verification after implementation:

- provider config resolves correctly for `openai`
- provider config resolves correctly for `apimart`
- text modules no longer read `OPENAI_API_KEY` directly
- APIMART base URL defaults to `https://api.apimart.ai/v1`
- image generation config uses unified provider settings
- business modules can resolve model aliases without hardcoded vendor names

Recommended tests:

- unit tests for config resolution
- unit tests for model alias resolution
- regression test for `NailNoteWorkflow(generate_images=False)`
- smoke test with `LLM_PROVIDER=apimart`

## Recommended Implementation Sequence

1. create `src/llm_provider.py`
2. migrate all text client factories to the provider runtime
3. migrate image generators to provider runtime
4. remove legacy `new.apipudding.com` default
5. update README and architecture docs to reflect the implemented behavior

## Open Questions Resolved

### Should the abstraction be called OpenAIProvider?

No. That would encode the wrong conceptual boundary. The correct abstraction is `LLMProvider`, with OpenAI-compatible transport as one implementation detail.

### Should the frontend choose raw model names?

No. The frontend should eventually configure model aliases or provider presets through backend-managed settings. Raw model strings should stay server-side.

### Should we store provider keys in the app client?

No. Keys must remain server-side only.

## Implementation Recommendation

Proceed with a single `LLMProvider` abstraction backed by:

- provider registry
- model alias mapping
- OpenAI-compatible client factory
- provider-aware image configuration

This is the smallest design that solves the current duplication while leaving a clean path for future Web and mobile app integration.
