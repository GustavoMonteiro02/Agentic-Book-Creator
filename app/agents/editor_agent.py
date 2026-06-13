from app.agents.state import BookState
from app.llm.client import llm_client
from app.prompts.editor_prompt import EDITOR_PROMPT


def edit_chapter(state: BookState) -> BookState:
    draft = state.get("chapter_drafts", [{}])[-1]
    markdown = draft.get("markdown", "")
    final_markdown = markdown + "\n## Editorial Note\n\nThis version is ready for human review and can be expanded with project-specific examples.\n"

    final_markdown = llm_client.generate_text(
        system_prompt=EDITOR_PROMPT,
        user_payload={
            "book_requirements": state.get("book_requirements", {}),
            "book_strategy": state.get("book_strategy", {}),
            "technical_review": state.get("chapter_reviews", [])[-1:] or [],
            "chapter_draft": draft,
        },
        fallback=final_markdown,
    )

    final = {
        "chapter_number": draft.get("chapter_number", 1),
        "title": draft.get("title", "Chapter"),
        "markdown": final_markdown,
    }

    return {**state, "final_chapters": [*state.get("final_chapters", []), final], "status": "chapter_finalized"}
