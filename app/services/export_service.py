from app.database.repositories import project_repository


class ExportService:
    def export_markdown(self, project_id: str) -> str:
        state = project_repository.get(project_id)
        title = state.get("book_strategy", {}).get("suggested_title", state.get("title", "Untitled Book"))
        chapters = "\n\n".join(chapter.get("markdown", "") for chapter in state.get("final_chapters", []))
        return f"# {title}\n\n{chapters}".strip()


export_service = ExportService()
