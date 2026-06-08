from app.agents.state import BookState
from app.database.repositories import project_repository
from app.services.run_service import DEFAULT_LLM_METADATA


class DiagnosticsService:
    def get_project_diagnostics(self, project_id: str) -> dict:
        state = project_repository.get(project_id)
        text_blocks = _collect_text_blocks(state)
        token_estimate = estimate_tokens("\n\n".join(text_blocks))
        run_count_by_type = _count_runs_by_type(state.get("execution_runs", []))
        latest_run = state.get("execution_runs", [])[-1] if state.get("execution_runs") else {}

        quality_signals = {
            "has_human_approval_gate": True,
            "structure_approved": bool(state.get("structure_approved")),
            "has_technical_review": bool(state.get("chapter_reviews")),
            "has_final_markdown": bool(state.get("final_chapters")),
            "rag_enabled": False,
        }

        return {
            "project_id": project_id,
            "status": state.get("status", "unknown"),
            "llm_metadata": latest_run.get("llm_metadata", DEFAULT_LLM_METADATA),
            "estimated_total_tokens": token_estimate,
            "estimated_cost_usd": estimate_cost_usd(token_estimate),
            "run_count_by_type": run_count_by_type,
            "artifact_counts": {
                "questions": len(state.get("input_questions", [])),
                "memory_items": len(state.get("project_memory", [])),
                "chapter_plans": len(state.get("chapter_plans", [])),
                "chapter_drafts": len(state.get("chapter_drafts", [])),
                "chapter_reviews": len(state.get("chapter_reviews", [])),
                "final_chapters": len(state.get("final_chapters", [])),
            },
            "quality_signals": quality_signals,
            "debugging_checklist": build_debugging_checklist(quality_signals),
        }


def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    return max(1, round(len(text) / 4))


def estimate_cost_usd(token_count: int, price_per_1k_tokens: float = 0.002) -> float:
    return round((token_count / 1000) * price_per_1k_tokens, 6)


def _collect_text_blocks(state: BookState) -> list[str]:
    blocks = [state.get("initial_user_idea", "")]
    blocks.extend(str(answer.get("answer", "")) for answer in state.get("user_answers", []))
    blocks.extend(chapter.get("markdown", "") for chapter in state.get("chapter_drafts", []))
    blocks.extend(chapter.get("markdown", "") for chapter in state.get("final_chapters", []))
    return [block for block in blocks if block]


def _count_runs_by_type(runs: list[dict]) -> dict:
    counts: dict[str, int] = {}
    for run in runs:
        run_type = run.get("run_type", "unknown")
        counts[run_type] = counts.get(run_type, 0) + 1
    return counts


def build_debugging_checklist(quality_signals: dict) -> list[dict]:
    checklist = [
        {
            "question": "Was the input clear enough to generate a structured brief?",
            "status": "check",
            "category": "input_understanding",
        },
        {
            "question": "Was the book structure approved before chapter generation?",
            "status": "pass" if quality_signals["structure_approved"] else "needs_attention",
            "category": "human_review",
        },
        {
            "question": "Was a technical review produced before final editing?",
            "status": "pass" if quality_signals["has_technical_review"] else "needs_attention",
            "category": "technical_review",
        },
        {
            "question": "Is the answer grounded in retrieved source context?",
            "status": "not_applicable" if not quality_signals["rag_enabled"] else "check",
            "category": "rag_grounding",
        },
        {
            "question": "Would a deterministic rule be better than an LLM for this step?",
            "status": "check",
            "category": "system_design",
        },
    ]
    return checklist


diagnostics_service = DiagnosticsService()
