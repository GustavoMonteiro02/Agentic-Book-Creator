from app.agents.state import BookState


def plan_chapter(state: BookState) -> BookState:
    chapter_number = state.get("current_chapter_number", 1)
    chapter = _find_chapter(state.get("book_structure", {}), chapter_number)

    plan = {
        "chapter_number": chapter_number,
        "title": chapter.get("title", f"Chapter {chapter_number}"),
        "goal": chapter.get("goal", "Teach the chapter topic clearly."),
        "key_concepts": ["agentic workflow", "state", "human-in-the-loop", "tool use"],
        "pedagogical_sequence": ["motivation", "concepts", "example", "implementation", "review"],
        "examples": [chapter.get("practical_example", "Practical workflow example")],
        "analogies": ["An agentic workflow is like an editorial pipeline with checkpoints."],
        "code_required": ["TypedDict state", "node function", "conditional edge"],
        "exercises": chapter.get("exercises", []),
        "quality_criteria": ["clear", "technically accurate", "actionable", "consistent with strategy"],
    }

    return {
        **state,
        "chapter_plans": [*state.get("chapter_plans", []), plan],
        "status": "chapter_planned",
    }


def _find_chapter(structure: dict, chapter_number: int) -> dict:
    for part in structure.get("parts", []):
        for chapter in part.get("chapters", []):
            if chapter.get("chapter_number") == chapter_number:
                return chapter
    return {}
