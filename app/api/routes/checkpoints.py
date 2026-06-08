from fastapi import APIRouter, HTTPException

from app.services.checkpoint_service import checkpoint_service

router = APIRouter(prefix="/projects/{project_id}/checkpoints", tags=["checkpoints"])


@router.get("")
def list_checkpoints(project_id: str):
    try:
        return checkpoint_service.list_checkpoints(project_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc


@router.post("/{checkpoint_id}/restore")
def restore_checkpoint(project_id: str, checkpoint_id: str):
    try:
        return checkpoint_service.restore_checkpoint(project_id, checkpoint_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Checkpoint not found") from exc
