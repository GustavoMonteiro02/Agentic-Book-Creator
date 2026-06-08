from datetime import datetime
from uuid import uuid4

from app.agents.state import BookState


class InMemoryProjectRepository:
    def __init__(self) -> None:
        self.projects: dict[str, BookState] = {}

    def create(self, title: str, initial_idea: str) -> BookState:
        project_id = str(uuid4())
        now = datetime.utcnow().isoformat()
        state: BookState = {
            "project_id": project_id,
            "initial_user_idea": initial_idea,
            "raw_user_inputs": [initial_idea],
            "user_answers": [],
            "structure_approved": False,
            "structure_revision_requests": [],
            "current_chapter_number": 1,
            "chapter_plans": [],
            "chapter_drafts": [],
            "chapter_reviews": [],
            "final_chapters": [],
            "user_feedback": [],
            "errors": [],
            "status": "created",
            "title": title,
            "created_at": now,
            "updated_at": now,
        }
        self.projects[project_id] = state
        return state

    def list(self) -> list[BookState]:
        return list(self.projects.values())

    def get(self, project_id: str) -> BookState:
        return self.projects[project_id]

    def save(self, state: BookState) -> BookState:
        state["updated_at"] = datetime.utcnow().isoformat()
        self.projects[state["project_id"]] = state
        return state


project_repository = InMemoryProjectRepository()
