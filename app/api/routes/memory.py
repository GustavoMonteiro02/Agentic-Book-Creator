from fastapi import APIRouter, HTTPException

from app.schemas.memory import MemoryCreate
from app.services.memory_service import memory_service

router = APIRouter(prefix="/projects/{project_id}/memory", tags=["memory"])


@router.post("")
def add_memory(project_id: str, payload: MemoryCreate):
    try:
        return memory_service.add_memory(
            project_id=project_id,
            memory_type=payload.memory_type,
            content=payload.content,
            source=payload.source,
            expires_at=payload.expires_at,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc


@router.get("")
def list_memory(project_id: str, include_expired: bool = False):
    try:
        return memory_service.list_memory(project_id, include_expired=include_expired)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc


@router.delete("/{memory_id}")
def delete_memory(project_id: str, memory_id: str):
    try:
        deleted = memory_service.delete_memory(project_id, memory_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc
    if not deleted:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"deleted": True}
