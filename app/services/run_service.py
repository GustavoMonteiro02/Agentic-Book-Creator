from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from app.agents.state import BookState
from app.config import get_settings
from app.services.checkpoint_service import checkpoint_service
from app.services.model_routing_service import routing_metadata


DEFAULT_LLM_METADATA = {
    "prompt_version": "mvp-v1",
    "llm_model_version": "configured-at-runtime",
    "embedding_model_version": "not-enabled",
    "chunking_strategy_version": "not-enabled",
    "retrieval_config_version": "not-enabled",
    "index_version": "not-enabled",
    "temperature": 0,
}


def record_run(
    state: BookState,
    run_type: str,
    status: str = "completed",
    langsmith_trace_url: str | None = None,
    metadata: dict | None = None,
) -> BookState:
    now = datetime.utcnow().isoformat()
    settings = get_settings()
    llm_enabled = _llm_enabled(settings)
    run = {
        "id": str(uuid4()),
        "project_id": state["project_id"],
        "run_type": run_type,
        "status": status,
        "langsmith_trace_url": langsmith_trace_url,
        "llm_metadata": {
            **DEFAULT_LLM_METADATA,
            "llm_provider": settings.llm_provider,
            "llm_model_version": settings.llm_model if llm_enabled else "deterministic-fallback",
            "llm_enabled": llm_enabled,
            **routing_metadata(run_type),
            **(metadata or {}),
        },
        "started_at": now,
        "finished_at": now,
    }
    state["execution_runs"] = [*state.get("execution_runs", []), run]
    state = checkpoint_service.create_checkpoint(state, run_type)
    return state


def _llm_enabled(settings) -> bool:
    if not settings.llm_enabled:
        return False
    if settings.llm_provider == "gemini":
        return bool(settings.gemini_api_key or settings.google_api_key)
    if settings.llm_provider == "openai":
        return bool(settings.openai_api_key)
    return False
