from fastapi import APIRouter, HTTPException

from app.agents.graph import HumanApprovalRequired
from app.services.chapter_service import chapter_service

router = APIRouter(prefix="/projects/{project_id}/chapters", tags=["chapters"])


@router.post("/{chapter_number}/plan")
def plan_chapter(project_id: str, chapter_number: int):
    return generate_chapter(project_id, chapter_number)


@router.post("/{chapter_number}/generate")
def generate_chapter(project_id: str, chapter_number: int):
    try:
        return chapter_service.generate_chapter(project_id, chapter_number)
    except HumanApprovalRequired as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc


@router.post("/{chapter_number}/review")
def review_chapter(project_id: str, chapter_number: int):
    return generate_chapter(project_id, chapter_number)


@router.post("/{chapter_number}/edit")
def edit_chapter(project_id: str, chapter_number: int):
    return generate_chapter(project_id, chapter_number)


@router.get("/{chapter_number}")
def get_chapter(project_id: str, chapter_number: int):
    try:
        chapter = chapter_service.get_chapter(project_id, chapter_number)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc
    if chapter is None:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return chapter
