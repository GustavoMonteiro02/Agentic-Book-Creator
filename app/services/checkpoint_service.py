from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from app.agents.state import BookState
from app.database.repositories import project_repository


EXCLUDED_SNAPSHOT_FIELDS = {"checkpoints"}


class CheckpointService:
    def create_checkpoint(self, state: BookState, node_name: str) -> BookState:
        checkpoint = {
            "id": str(uuid4()),
            "node_name": node_name,
            "status": state.get("status", "unknown"),
            "created_at": datetime.utcnow().isoformat(),
            "snapshot": _snapshot_state(state),
        }
        state["checkpoints"] = [*state.get("checkpoints", []), checkpoint]
        return state

    def list_checkpoints(self, project_id: str) -> list[dict]:
        state = project_repository.get(project_id)
        return [
            {
                "id": checkpoint["id"],
                "node_name": checkpoint["node_name"],
                "status": checkpoint["status"],
                "created_at": checkpoint["created_at"],
            }
            for checkpoint in state.get("checkpoints", [])
        ]

    def restore_checkpoint(self, project_id: str, checkpoint_id: str) -> BookState:
        state = project_repository.get(project_id)
        checkpoint = _find_checkpoint(state, checkpoint_id)
        restored = dict(checkpoint["snapshot"])
        restored["checkpoints"] = state.get("checkpoints", [])
        restored["status"] = f"restored:{checkpoint['node_name']}"
        return project_repository.save(restored)


def _snapshot_state(state: BookState) -> dict:
    return {key: value for key, value in state.items() if key not in EXCLUDED_SNAPSHOT_FIELDS}


def _find_checkpoint(state: BookState, checkpoint_id: str) -> dict:
    for checkpoint in state.get("checkpoints", []):
        if checkpoint.get("id") == checkpoint_id:
            return checkpoint
    raise KeyError(checkpoint_id)


checkpoint_service = CheckpointService()
