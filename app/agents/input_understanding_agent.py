from app.agents.state import BookState


def understand_input(state: BookState) -> BookState:
    answers = {answer.get("field"): answer.get("answer") for answer in state.get("user_answers", [])}
    idea = state.get("initial_user_idea", "")

    requirements = {
        "main_topic": idea,
        "target_audience": answers.get("target_audience", "developers and automation engineers"),
        "reader_level": answers.get("reader_level", "intermediate"),
        "book_goal": answers.get("book_goal", "help readers build practical agentic AI systems"),
        "tone": answers.get("tone", "practical and clear"),
        "technical_depth": answers.get("technical_depth", "hands-on with code examples"),
        "content_preferences": ["theory", "code", "analogies", "exercises", "mini projects"],
        "required_topics": _split_answer(answers.get("required_topics", "LangGraph, LangChain, FastAPI, RAG")),
        "topics_to_avoid": _split_answer(answers.get("topics_to_avoid", "")),
        "preferred_structure": answers.get("preferred_structure", "basic to advanced with projects"),
        "chapter_format": _split_answer(answers.get("chapter_format", "introduction, concepts, code, mistakes, exercises, mini project")),
        "output_formats": _split_answer(answers.get("output_formats", "Markdown")),
    }

    return {**state, "book_requirements": requirements, "status": "requirements_ready"}


def _split_answer(value: str) -> list[str]:
    return [item.strip() for item in value.replace(";", ",").split(",") if item.strip()]
