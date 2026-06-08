from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from app.database.repositories import project_repository


class MemoryService:
    def add_memory(self, project_id: str, memory_type: str, content: str, source: str = "human", expires_at: datetime | None = None):
        state = project_repository.get(project_id)
        memory = {
            "id": str(uuid4()),
            "memory_type": memory_type,
            "content": content,
            "source": source,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": expires_at.isoformat() if expires_at else None,
        }
        state["project_memory"] = [*state.get("project_memory", []), memory]
        project_repository.save(state)
        return memory

    def list_memory(self, project_id: str, include_expired: bool = False):
        state = project_repository.get(project_id)
        memories = state.get("project_memory", [])
        if include_expired:
            return memories
        return [memory for memory in memories if not _is_expired(memory)]

    def delete_memory(self, project_id: str, memory_id: str) -> bool:
        state = project_repository.get(project_id)
        memories = state.get("project_memory", [])
        filtered = [memory for memory in memories if memory.get("id") != memory_id]
        state["project_memory"] = filtered
        project_repository.save(state)
        return len(filtered) != len(memories)


def _is_expired(memory: dict) -> bool:
    expires_at = memory.get("expires_at")
    if not expires_at:
        return False
    return datetime.fromisoformat(expires_at) <= datetime.utcnow()


memory_service = MemoryService()
