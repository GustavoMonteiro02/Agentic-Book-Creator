from datetime import datetime
from uuid import uuid4

from app.agents.state import BookState
from app.database.models import BookProject
from app.database.session import SessionLocal, init_database


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
            "project_memory": [],
            "execution_runs": [],
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


class SQLAlchemyProjectRepository:
    def create(self, title: str, initial_idea: str) -> BookState:
        init_database()
        project_id = str(uuid4())
        now = datetime.utcnow().isoformat()
        state = _initial_state(project_id=project_id, title=title, initial_idea=initial_idea, created_at=now, updated_at=now)

        with SessionLocal() as session:
            project = BookProject(
                id=project_id,
                title=title,
                initial_idea=initial_idea,
                status=state["status"],
                state_json=state,
            )
            session.add(project)
            session.commit()

        return state

    def list(self) -> list[BookState]:
        init_database()
        with SessionLocal() as session:
            projects = session.query(BookProject).order_by(BookProject.created_at.desc()).all()
            return [_state_from_project(project) for project in projects]

    def get(self, project_id: str) -> BookState:
        init_database()
        with SessionLocal() as session:
            project = session.get(BookProject, project_id)
            if project is None:
                raise KeyError(project_id)
            return _state_from_project(project)

    def save(self, state: BookState) -> BookState:
        init_database()
        state["updated_at"] = datetime.utcnow().isoformat()
        with SessionLocal() as session:
            project = session.get(BookProject, state["project_id"])
            if project is None:
                raise KeyError(state["project_id"])
            project.title = state.get("title", project.title)
            project.initial_idea = state.get("initial_user_idea", project.initial_idea)
            project.status = state.get("status", project.status)
            project.state_json = dict(state)
            session.commit()
        return state


def _initial_state(project_id: str, title: str, initial_idea: str, created_at: str, updated_at: str) -> BookState:
    return {
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
        "project_memory": [],
        "execution_runs": [],
        "errors": [],
        "status": "created",
        "title": title,
        "created_at": created_at,
        "updated_at": updated_at,
    }


def _state_from_project(project: BookProject) -> BookState:
    state = dict(project.state_json or {})
    state.setdefault("project_id", project.id)
    state.setdefault("title", project.title)
    state.setdefault("initial_user_idea", project.initial_idea)
    state.setdefault("status", project.status)
    state.setdefault("raw_user_inputs", [project.initial_idea])
    state.setdefault("user_answers", [])
    state.setdefault("input_questions", [])
    state.setdefault("structure_approved", False)
    state.setdefault("structure_revision_requests", [])
    state.setdefault("current_chapter_number", 1)
    state.setdefault("chapter_plans", [])
    state.setdefault("chapter_drafts", [])
    state.setdefault("chapter_reviews", [])
    state.setdefault("final_chapters", [])
    state.setdefault("user_feedback", [])
    state.setdefault("project_memory", [])
    state.setdefault("execution_runs", [])
    state.setdefault("errors", [])
    state.setdefault("created_at", project.created_at.isoformat())
    state.setdefault("updated_at", project.updated_at.isoformat())
    return state


project_repository = SQLAlchemyProjectRepository()
