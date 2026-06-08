from pydantic import BaseModel, Field


class RetrievalEvalCase(BaseModel):
    query: str = Field(min_length=1)
    expected_document_ids: list[str] = Field(min_length=1)
    retrieved_document_ids: list[str]


class RetrievalEvalRequest(BaseModel):
    cases: list[RetrievalEvalCase] = Field(min_length=1)
    k: int = Field(default=5, ge=1)
