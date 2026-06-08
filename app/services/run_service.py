from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from app.agents.state import BookState


DEFAULT_LLM_METADATA = {
    "prompt_version": "mvp-v1",
    "llm_model_version": "deterministic-local-v1",
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
    run = {
        "id": str(uuid4()),
        "project_id": state["project_id"],
        "run_type": run_type,
        "status": status,
        "langsmith_trace_url": langsmith_trace_url,
        "llm_metadata": {**DEFAULT_LLM_METADATA, **(metadata or {})},
        "started_at": now,
        "finished_at": now,
    }
    state["execution_runs"] = [*state.get("execution_runs", []), run]
    return state
