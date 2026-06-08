from app.agents.graph import SimpleBookWorkflow
from app.database.repositories import project_repository


class ChapterService:
    def __init__(self) -> None:
        self.workflow = SimpleBookWorkflow()

    def generate_chapter(self, project_id: str, chapter_number: int):
        state = project_repository.get(project_id)
        state["current_chapter_number"] = chapter_number
        state = self.workflow.generate_chapter(state)
        return project_repository.save(state)

    def get_chapter(self, project_id: str, chapter_number: int):
        state = project_repository.get(project_id)
        for chapter in state.get("final_chapters", []):
            if chapter.get("chapter_number") == chapter_number:
                return chapter
        return None


chapter_service = ChapterService()
