from app.agents.state import BookState


def edit_chapter(state: BookState) -> BookState:
    draft = state.get("chapter_drafts", [{}])[-1]
    markdown = draft.get("markdown", "")
    final_markdown = markdown + "\n## Editorial Note\n\nThis version is ready for human review and can be expanded with project-specific examples.\n"

    final = {
        "chapter_number": draft.get("chapter_number", 1),
        "title": draft.get("title", "Chapter"),
        "markdown": final_markdown,
    }

    return {**state, "final_chapters": [*state.get("final_chapters", []), final], "status": "chapter_finalized"}
