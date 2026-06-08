from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from app.agents.state import BookState


def record_run(state: BookState, run_type: str, status: str = "completed", langsmith_trace_url: str | None = None) -> BookState:
    now = datetime.utcnow().isoformat()
    run = {
        "id": str(uuid4()),
        "project_id": state["project_id"],
        "run_type": run_type,
        "status": status,
        "langsmith_trace_url": langsmith_trace_url,
        "started_at": now,
        "finished_at": now,
    }
    state["execution_runs"] = [*state.get("execution_runs", []), run]
    return state
