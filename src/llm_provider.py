"""
Unified provider runtime for OpenAI-compatible LLM and image backends.
"""

from dataclasses import dataclass
import os
from typing import Dict, Optional


APIMART_DEFAULT_BASE = "https://api.apimart.ai/v1"


@dataclass(frozen=True)
class ProviderProfile:
    provider_id: str
    label: str
    api_base: Optional[str]
    api_key: str
    default_models: Dict[str, str]


_DEFAULT_MODEL_ALIASES: Dict[str, Dict[str, str]] = {
    "openai": {
        "planner_small": "gpt-4o-mini",
        "copy_small": "gpt-4o-mini",
        "tag_small": "gpt-4o-mini",
        "hook_small": "gpt-4o-mini",
        "vision_small": "gpt-4o-mini",
        "image_default": "gpt-image-2",
    },
    "apimart": {
        "planner_small": "gpt-4o-mini",
        "copy_small": "gpt-4o-mini",
        "tag_small": "gpt-4o-mini",
        "hook_small": "gpt-4o-mini",
        "vision_small": "gpt-4o-mini",
        "image_default": "gpt-image-2",
    },
}


def _resolve_provider_id() -> str:
    explicit = (os.getenv("LLM_PROVIDER") or "").strip().lower()
    if explicit:
        return explicit

    if os.getenv("APIMART_API_KEY") or os.getenv("APIMART_API_BASE"):
        return "apimart"

    # Backward-compatible default for this repo's existing gateway-oriented setup.
    return "apimart"


def _require_api_key(provider_id: str) -> str:
    if provider_id == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            return api_key
        raise RuntimeError("Missing API key for provider=openai. Expected OPENAI_API_KEY.")

    if provider_id == "apimart":
        api_key = (
            os.getenv("APIMART_API_KEY")
            or os.getenv("OPENAI_API_KEY")
            or os.getenv("API_KEY")
        )
        if api_key:
            return api_key
        raise RuntimeError(
            "Missing API key for provider=apimart. Tried APIMART_API_KEY, OPENAI_API_KEY, API_KEY."
        )

    raise ValueError(f"Unknown LLM provider: {provider_id}")


def _provider_api_base(provider_id: str) -> Optional[str]:
    if provider_id == "openai":
        return os.getenv("OPENAI_API_BASE") or None
    if provider_id == "apimart":
        return os.getenv("APIMART_API_BASE", APIMART_DEFAULT_BASE)
    raise ValueError(f"Unknown LLM provider: {provider_id}")


def get_active_provider() -> ProviderProfile:
    provider_id = _resolve_provider_id()
    if provider_id not in _DEFAULT_MODEL_ALIASES:
        raise ValueError(f"Unknown LLM provider: {provider_id}")

    return ProviderProfile(
        provider_id=provider_id,
        label=provider_id,
        api_base=_provider_api_base(provider_id),
        api_key=_require_api_key(provider_id),
        default_models=dict(_DEFAULT_MODEL_ALIASES[provider_id]),
    )


def get_model_name(alias: str) -> str:
    provider = get_active_provider()
    env_name = f"TEXT_MODEL_{alias.upper()}"
    if alias == "image_default":
        env_name = "IMAGE_MODEL_DEFAULT"

    override = os.getenv(env_name)
    if override:
        return override

    model = provider.default_models.get(alias)
    if model:
        return model

    raise KeyError(f"Unknown model alias: {alias}")


def get_openai_client_kwargs() -> dict:
    provider = get_active_provider()
    kwargs = {"api_key": provider.api_key}
    if provider.api_base:
        kwargs["base_url"] = provider.api_base
    return kwargs


def get_openai_compatible_client():
    from openai import OpenAI

    return OpenAI(**get_openai_client_kwargs())


def get_text_client():
    return get_openai_compatible_client()


def get_text_model(alias: str) -> str:
    return get_model_name(alias)


def get_image_settings() -> dict:
    provider = get_active_provider()
    return {
        "provider_id": provider.provider_id,
        "api_base": provider.api_base,
        "api_key": provider.api_key,
        "model": get_model_name("image_default"),
    }
