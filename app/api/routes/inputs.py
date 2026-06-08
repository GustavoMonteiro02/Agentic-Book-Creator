from fastapi import APIRouter, HTTPException

from app.schemas.inputs import UserAnswersRequest
from app.services.book_service import book_service

router = APIRouter(prefix="/projects/{project_id}", tags=["inputs"])


@router.post("/idea")
def save_idea(project_id: str):
    try:
        return book_service.generate_questions(project_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc


@router.post("/questions")
def generate_questions(project_id: str):
    try:
        return book_service.generate_questions(project_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc


@router.post("/answers")
def submit_answers(project_id: str, payload: UserAnswersRequest):
    try:
        return book_service.submit_answers(project_id, [answer.model_dump() for answer in payload.answers])
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc
