from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from app.database.repositories import project_repository
from app.rag.ingest import chunk_by_headings


class SourceService:
    def upload_source(self, project_id: str, filename: str, content: str, content_type: str = "text/markdown") -> dict:
        state = project_repository.get(project_id)
        source_id = str(uuid4())
        chunks = chunk_by_headings(
            content,
            metadata={
                "project_id": project_id,
                "source_id": source_id,
                "filename": filename,
                "content_type": content_type,
            },
        )
        source = {
            "id": source_id,
            "filename": filename,
            "content_type": content_type,
            "chunk_count": len(chunks),
            "created_at": datetime.utcnow().isoformat(),
        }
        indexed_chunks = [
            {
                "id": f"{source_id}:{chunk.chunk_index}",
                "source_id": source_id,
                "text": chunk.text,
                "chunk_index": chunk.chunk_index,
                "metadata": chunk.metadata,
            }
            for chunk in chunks
        ]

        state["sources"] = [*state.get("sources", []), source]
        state["source_chunks"] = [*state.get("source_chunks", []), *indexed_chunks]
        state["status"] = "source_indexed"
        project_repository.save(state)
        return source

    def list_sources(self, project_id: str) -> list[dict]:
        state = project_repository.get(project_id)
        return state.get("sources", [])

    def list_chunks(self, project_id: str, source_id: str | None = None) -> list[dict]:
        state = project_repository.get(project_id)
        chunks = state.get("source_chunks", [])
        if source_id:
            return [chunk for chunk in chunks if chunk.get("source_id") == source_id]
        return chunks


source_service = SourceService()
