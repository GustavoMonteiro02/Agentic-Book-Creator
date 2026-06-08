from app.agents.state import BookState


def review_chapter(state: BookState) -> BookState:
    draft = state.get("chapter_drafts", [{}])[-1]
    markdown = draft.get("markdown", "")
    issues = []

    if "```python" not in markdown:
        issues.append({"type": "missing_code", "location": "Code Sketch", "comment": "Chapter should include Python code.", "severity": "medium"})
    if len(markdown.split()) < 150:
        issues.append({"type": "thin_content", "location": "chapter", "comment": "Chapter is too short for the intended format.", "severity": "medium"})

    review = {
        "chapter_number": draft.get("chapter_number", 1),
        "review_type": "technical",
        "technical_score": 8 if not issues else 6,
        "approved": not any(issue["severity"] == "high" for issue in issues),
        "issues": issues,
        "improvement_suggestions": ["Add concrete production examples in the LLM-backed implementation."],
    }

    return {**state, "chapter_reviews": [*state.get("chapter_reviews", []), review], "status": "chapter_reviewed"}
