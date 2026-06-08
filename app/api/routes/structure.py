from fastapi import APIRouter, HTTPException

from app.schemas.structure import ApproveStructureRequest
from app.services.book_service import book_service
from app.services.project_service import project_service

router = APIRouter(prefix="/projects/{project_id}", tags=["structure"])


@router.post("/requirements")
def get_requirements(project_id: str):
    try:
        return project_service.get_project(project_id).get("book_requirements", {})
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc


@router.post("/strategy")
def get_strategy(project_id: str):
    try:
        return project_service.get_project(project_id).get("book_strategy", {})
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc


@router.post("/structure")
def get_structure(project_id: str):
    try:
        return project_service.get_project(project_id).get("book_structure", {})
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc


@router.post("/approve-structure")
def approve_structure(project_id: str, payload: ApproveStructureRequest):
    try:
        return book_service.approve_structure(project_id, payload.approved, payload.revision_request)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc
