from fastapi import APIRouter, HTTPException

from app.schemas.project import ProjectCreate
from app.services.project_service import project_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("")
def create_project(payload: ProjectCreate):
    return project_service.create_project(payload.title, payload.initial_idea)


@router.get("")
def list_projects():
    return project_service.list_projects()


@router.get("/{project_id}")
def get_project(project_id: str):
    try:
        return project_service.get_project(project_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc
