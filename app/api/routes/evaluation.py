from fastapi import APIRouter

from app.evaluation.retrieval import RetrievalCase, evaluate_retrieval
from app.schemas.evaluation import RetrievalEvalRequest

router = APIRouter(prefix="/projects/{project_id}/evaluate", tags=["evaluation"])


@router.post("/retrieval")
def evaluate_project_retrieval(project_id: str, payload: RetrievalEvalRequest):
    cases = [
        RetrievalCase(
            query=case.query,
            expected_document_ids=set(case.expected_document_ids),
            retrieved_document_ids=case.retrieved_document_ids,
        )
        for case in payload.cases
    ]
    result = evaluate_retrieval(cases, k=payload.k)
    return {"project_id": project_id, **result}
