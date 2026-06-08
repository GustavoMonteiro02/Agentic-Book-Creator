from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException

from app.schemas.sources import SourceUpload
from app.services.source_service import source_service

router = APIRouter(prefix="/projects/{project_id}/sources", tags=["sources"])


@router.post("/upload")
def upload_source(project_id: str, payload: SourceUpload):
    try:
        return source_service.upload_source(project_id, payload.filename, payload.content, payload.content_type)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc


@router.get("")
def list_sources(project_id: str):
    try:
        return source_service.list_sources(project_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc


@router.get("/chunks")
def list_source_chunks(project_id: str, source_id: Optional[str] = None):
    try:
        return source_service.list_chunks(project_id, source_id=source_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc
