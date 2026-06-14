from app.agents.state import BookState
from app.llm.client import llm_client
from app.prompts.structure_designer_prompt import STRUCTURE_DESIGNER_PROMPT


def design_structure(state: BookState) -> BookState:
    strategy = state.get("book_strategy", {})
    title = strategy.get("suggested_title", "Building Agentic AI Systems")
    revision_requests = state.get("structure_revision_requests", [])

    structure = {
        "book_title": title,
        "parts": [
            {
                "part_title": "Foundations",
                "part_goal": "Build the reader's mental model for agentic workflows.",
                "chapters": [
                    {
                        "chapter_number": 1,
                        "title": "From Automation Scripts to Agentic Workflows",
                        "goal": "Explain what changes when software starts planning, using tools, and waiting for humans.",
                        "sections": [
                            {"title": "Why agentic systems matter", "purpose": "Frame the business and technical value."},
                            {"title": "State, tools, and control flow", "purpose": "Introduce the core architecture."},
                            {"title": "Human approval as a product feature", "purpose": "Position HITL as reliability engineering."},
                        ],
                        "practical_example": "Convert an RPA handoff into a multi-step AI workflow.",
                        "mini_project": "Map a simple editorial assistant as a state machine.",
                        "exercises": [
                            "Identify missing state in a prompt-only workflow.",
                            "Design one approval gate for a risky automation.",
                        ],
                    }
                ],
            },
            {
                "part_title": "Building the System",
                "part_goal": "Implement the backend, agents, persistence, and tracing.",
                "chapters": [
                    {
                        "chapter_number": 2,
                        "title": "Designing the LangGraph State",
                        "goal": "Turn product requirements into durable workflow state.",
                        "sections": [
                            {"title": "State schema", "purpose": "Define the shared contract."},
                            {"title": "Node boundaries", "purpose": "Keep agents testable."},
                        ],
                        "practical_example": "Build a typed BookState.",
                        "mini_project": "Add a revision loop to the graph.",
                        "exercises": ["Add an error field to the state model."],
                    }
                ],
            },
        ],
    }
    structure = _apply_revision_fallback(structure, revision_requests)

    structure = llm_client.generate_json(
        system_prompt=STRUCTURE_DESIGNER_PROMPT,
        user_payload={
            "book_requirements": state.get("book_requirements", {}),
            "book_strategy": strategy,
            "existing_structure": state.get("book_structure", {}),
            "revision_requests": revision_requests,
        },
        fallback=structure,
    )

    return {**state, "book_structure": structure, "status": "structure_ready"}


def _apply_revision_fallback(structure: dict, revision_requests: list[str]) -> dict:
    latest_revision = revision_requests[-1].lower() if revision_requests else ""
    if not any(word in latest_revision for word in ["small", "short", "smaller", "curto", "curta"]):
        return structure

    first_part = dict(structure["parts"][0])
    first_chapter = dict(first_part["chapters"][0])
    first_chapter["sections"] = first_chapter.get("sections", [])[:2]
    first_chapter["exercises"] = first_chapter.get("exercises", [])[:1]
    first_chapter["goal"] = f"{first_chapter['goal']} Keep the scope intentionally compact."
    first_part["part_goal"] = f"{first_part['part_goal']} This revision keeps the outline smaller."
    first_part["chapters"] = [first_chapter]
    return {**structure, "parts": [first_part]}
