from app.agents.chapter_planner_agent import plan_chapter
from app.agents.chapter_writer_agent import write_chapter
from app.agents.editor_agent import edit_chapter
from app.agents.graph import HumanApprovalRequired, SimpleBookWorkflow
from app.agents.technical_reviewer_agent import review_chapter
from app.database.repositories import project_repository


class ChapterService:
    def __init__(self) -> None:
        self.workflow = SimpleBookWorkflow()

    def generate_chapter(self, project_id: str, chapter_number: int):
        state = project_repository.get(project_id)
        state["current_chapter_number"] = chapter_number
        state = self.workflow.generate_chapter(state)
        return project_repository.save(state)

    def plan_chapter(self, project_id: str, chapter_number: int):
        state = self._get_approved_state(project_id, chapter_number)
        state = plan_chapter(state)
        return project_repository.save(state)

    def draft_chapter(self, project_id: str, chapter_number: int):
        state = self._get_approved_state(project_id, chapter_number)
        if not state.get("chapter_plans"):
            state = plan_chapter(state)
        state = write_chapter(state)
        return project_repository.save(state)

    def review_chapter(self, project_id: str, chapter_number: int):
        state = self._get_approved_state(project_id, chapter_number)
        if not state.get("chapter_drafts"):
            if not state.get("chapter_plans"):
                state = plan_chapter(state)
            state = write_chapter(state)
        state = review_chapter(state)
        return project_repository.save(state)

    def edit_chapter(self, project_id: str, chapter_number: int):
        state = self._get_approved_state(project_id, chapter_number)
        if not state.get("chapter_drafts"):
            if not state.get("chapter_plans"):
                state = plan_chapter(state)
            state = write_chapter(state)
        if not state.get("chapter_reviews"):
            state = review_chapter(state)
        state = edit_chapter(state)
        return project_repository.save(state)

    def get_chapter(self, project_id: str, chapter_number: int):
        state = project_repository.get(project_id)
        for chapter in state.get("final_chapters", []):
            if chapter.get("chapter_number") == chapter_number:
                return chapter
        return None

    def _get_approved_state(self, project_id: str, chapter_number: int):
        state = project_repository.get(project_id)
        state["current_chapter_number"] = chapter_number
        if not state.get("structure_approved"):
            raise HumanApprovalRequired("Structure must be approved before chapter generation.")
        return state


chapter_service = ChapterService()
