from fastapi import APIRouter, HTTPException, Response

from app.services.export_service import export_service

router = APIRouter(prefix="/projects/{project_id}/export", tags=["export"])


@router.post("/markdown")
def export_markdown(project_id: str):
    try:
        markdown = export_service.export_markdown(project_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc
    return Response(content=markdown, media_type="text/markdown")
