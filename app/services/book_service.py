from __future__ import annotations

from app.agents.graph import SimpleBookWorkflow
from app.database.repositories import project_repository
from app.services.run_service import record_run


class BookService:
    def __init__(self) -> None:
        self.workflow = SimpleBookWorkflow()

    def generate_questions(self, project_id: str):
        state = project_repository.get(project_id)
        state = self.workflow.gather(state)
        state = record_run(state, "input_gathering")
        return project_repository.save(state)

    def submit_answers(self, project_id: str, answers: list[dict]):
        state = project_repository.get(project_id)
        merged_answers = {answer.get("field"): answer for answer in state.get("user_answers", [])}
        for answer in answers:
            merged_answers[answer["field"]] = answer
        state["user_answers"] = list(merged_answers.values())
        state["raw_user_inputs"] = [*state.get("raw_user_inputs", []), *[answer["answer"] for answer in answers]]
        state = self.workflow.create_book_plan(state)
        state = record_run(state, "book_plan")
        return project_repository.save(state)

    def approve_structure(self, project_id: str, approved: bool, revision_request: str | None = None):
        state = project_repository.get(project_id)
        state["structure_approved"] = approved
        if revision_request:
            state["structure_revision_requests"] = [*state.get("structure_revision_requests", []), revision_request]
            state = self.workflow.revise_structure(state)
        state["status"] = "structure_approved" if approved else "structure_revision_requested"
        state = record_run(state, "structure_approval" if approved else "structure_revision")
        return project_repository.save(state)


book_service = BookService()
