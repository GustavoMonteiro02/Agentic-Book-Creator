from pydantic import BaseModel


class DiagnosticsResponse(BaseModel):
    project_id: str
    status: str
    llm_metadata: dict
    estimated_total_tokens: int
    estimated_cost_usd: float
    run_count_by_type: dict
    artifact_counts: dict
    quality_signals: dict
