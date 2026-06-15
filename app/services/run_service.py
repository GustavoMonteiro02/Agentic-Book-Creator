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

WORKFLOW_RUN_BLUEPRINTS = {
    "input_gathering": [
        ("Input Gathering Agent", "Finds missing context in the book idea.", ["input_questions", "missing_information"]),
        ("Gemini", "Generates adaptive questions when LLM credentials are configured.", ["input_questions"]),
        ("Checkpoint Service", "Stores the questions and run checkpoint.", ["checkpoints"]),
    ],
    "book_plan": [
        ("Input Understanding Agent", "Turns saved answers into structured requirements.", ["book_requirements"]),
        ("Book Strategy Agent", "Creates the editorial promise, reader, and learning path.", ["book_strategy"]),
        ("Structure Designer Agent", "Creates the parts, chapters, exercises, and mini projects.", ["book_structure"]),
        ("Checkpoint Service", "Stores the generated plan.", ["checkpoints"]),
    ],
    "structure_revision": [
        ("Human Feedback Gate", "Records the latest revision request.", ["structure_revision_requests"]),
        ("Structure Designer Agent", "Revises the existing structure from that request.", ["book_structure"]),
        ("Gemini", "Applies semantic editorial changes when available.", ["book_structure"]),
        ("Checkpoint Service", "Stores the revised structure and run metadata.", ["checkpoints"]),
    ],
    "structure_approval": [
        ("Human Approval Gate", "Unlocks chapter generation.", ["structure_approved"]),
        ("Checkpoint Service", "Stores the approval decision.", ["checkpoints"]),
    ],
    "chapter_planning": [
        ("Chapter Planner Agent", "Builds the chapter objective, concepts, examples, and exercises.", ["chapter_plans"]),
        ("Checkpoint Service", "Stores the chapter plan.", ["checkpoints"]),
    ],
    "chapter_drafting": [
        ("Chapter Writer Agent", "Drafts the chapter markdown from the plan and project memory.", ["chapter_drafts"]),
        ("Checkpoint Service", "Stores the draft.", ["checkpoints"]),
    ],
    "chapter_review": [
        ("Technical Reviewer Agent", "Checks the draft for gaps, clarity, and implementation risk.", ["chapter_reviews"]),
        ("Checkpoint Service", "Stores the technical review.", ["checkpoints"]),
    ],
    "chapter_edit": [
        ("Editor Agent", "Turns the reviewed draft into final markdown.", ["final_chapters"]),
        ("Checkpoint Service", "Stores the final chapter.", ["checkpoints"]),
    ],
    "chapter_generation": [
        ("Chapter Planner Agent", "Builds the chapter objective, concepts, examples, and exercises.", ["chapter_plans"]),
        ("Chapter Writer Agent", "Drafts the chapter markdown from the plan and project memory.", ["chapter_drafts"]),
        ("Technical Reviewer Agent", "Checks the draft for gaps, clarity, and implementation risk.", ["chapter_reviews"]),
        ("Editor Agent", "Turns the reviewed draft into final markdown.", ["final_chapters"]),
        ("Checkpoint Service", "Stores the full chapter run.", ["checkpoints"]),
    ],
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
            "workflow_nodes": _workflow_nodes(run_type, state, include_current_checkpoint=True),
            "artifact_summary": _artifact_summary(state, include_current_checkpoint=True),
            "runtime_warnings": _runtime_warnings(state),
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


def _workflow_nodes(run_type: str, state: BookState, include_current_checkpoint: bool = False) -> list[dict]:
    nodes = WORKFLOW_RUN_BLUEPRINTS.get(run_type, [])
    return [
        {
            "name": name,
            "role": role,
            "status": "completed"
            if all(_artifact_present(state, field, include_current_checkpoint) for field in artifact_fields)
            else "waiting",
            "artifacts": [
                {
                    "field": field,
                    "summary": _artifact_value_summary(state.get(field), field, include_current_checkpoint),
                }
                for field in artifact_fields
            ],
        }
        for name, role, artifact_fields in nodes
    ]


def _artifact_present(state: BookState, field: str, include_current_checkpoint: bool = False) -> bool:
    if field == "checkpoints" and include_current_checkpoint:
        return True
    value = state.get(field)
    if isinstance(value, bool):
        return value
    return bool(value)


def _artifact_value_summary(value, field: str | None = None, include_current_checkpoint: bool = False) -> str:
    if field == "checkpoints" and include_current_checkpoint:
        return f"{len(value or []) + 1} item(s)"
    if isinstance(value, bool):
        return "approved" if value else "not approved"
    if isinstance(value, list):
        return f"{len(value)} item(s)"
    if isinstance(value, dict):
        keys = ", ".join(list(value.keys())[:4])
        return f"{len(value)} field(s)" + (f": {keys}" if keys else "")
    if value:
        return str(value)
    return "not produced yet"


def _artifact_summary(state: BookState, include_current_checkpoint: bool = False) -> dict:
    checkpoint_count = len(state.get("checkpoints", [])) + (1 if include_current_checkpoint else 0)
    return {
        "questions": len(state.get("input_questions", [])),
        "answers": len(state.get("user_answers", [])),
        "requirements_ready": bool(state.get("book_requirements")),
        "strategy_ready": bool(state.get("book_strategy")),
        "structure_ready": bool(state.get("book_structure")),
        "structure_approved": bool(state.get("structure_approved")),
        "revision_requests": len(state.get("structure_revision_requests", [])),
        "chapter_plans": len(state.get("chapter_plans", [])),
        "chapter_drafts": len(state.get("chapter_drafts", [])),
        "chapter_reviews": len(state.get("chapter_reviews", [])),
        "final_chapters": len(state.get("final_chapters", [])),
        "checkpoints": checkpoint_count,
    }


def _runtime_warnings(state: BookState) -> list[dict]:
    warnings = []
    for field in ["book_requirements", "book_strategy", "book_structure"]:
        value = state.get(field, {})
        if isinstance(value, dict) and value.get("llm_runtime", {}).get("status") == "fallback_used":
            warnings.append({"field": field, **value["llm_runtime"]})
    return warnings
