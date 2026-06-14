from app.agents.state import BookState
from app.llm.client import llm_client
from app.prompts.structure_designer_prompt import STRUCTURE_DESIGNER_PROMPT


def design_structure(state: BookState) -> BookState:
    strategy = state.get("book_strategy", {})
    title = strategy.get("suggested_title", "Building Agentic AI Systems")
    revision_requests = state.get("structure_revision_requests", [])

    default_structure = {
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
    original_structure = state.get("book_structure") or default_structure
    fallback_structure = _apply_revision_fallback(original_structure, revision_requests)

    structure = llm_client.generate_json(
        system_prompt=STRUCTURE_DESIGNER_PROMPT,
        user_payload={
            "book_requirements": state.get("book_requirements", {}),
            "book_strategy": strategy,
            "existing_structure": original_structure,
            "revision_requests": revision_requests,
            "agent_contract": {
                "llm_is_revision_authority": True,
                "expected_output": "Complete revised book structure JSON.",
                "debugging_fields": [
                    "revision_notes",
                    "last_revision_applied",
                    "change_summary",
                ],
            },
        },
        fallback=fallback_structure,
    )

    return {**state, "book_structure": structure, "status": "structure_ready"}


def _apply_revision_fallback(structure: dict, revision_requests: list[str]) -> dict:
    if revision_requests:
        structure = {
            **structure,
            "revision_notes": revision_requests,
            "last_revision_applied": revision_requests[-1],
        }
    latest_revision = revision_requests[-1].lower() if revision_requests else ""
    if _wants_more_chapters(latest_revision):
        structure = _add_revision_chapters(structure, latest_revision)
    if _wants_smaller_structure(latest_revision):
        structure = _compact_structure(structure)
    return structure


def _wants_more_chapters(revision: str) -> bool:
    return any(
        phrase in revision
        for phrase in [
            "more chapters",
            "add chapters",
            "additional chapters",
            "mais capítulos",
            "mais capitulos",
            "adiciona capítulos",
            "adiciona capitulos",
            "novos capítulos",
            "novos capitulos",
        ]
    )


def _wants_smaller_structure(revision: str) -> bool:
    return any(word in revision for word in ["small", "short", "smaller", "curto", "curta"])


def _chapter_count(structure: dict) -> int:
    return sum(len(part.get("chapters", [])) for part in structure.get("parts", []))


def _compact_structure(structure: dict) -> dict:
    first_part = dict(structure["parts"][0])
    first_chapter = dict(first_part["chapters"][0])
    first_chapter["sections"] = first_chapter.get("sections", [])[:2]
    first_chapter["exercises"] = first_chapter.get("exercises", [])[:1]
    first_chapter["goal"] = f"{first_chapter['goal']} Keep the scope intentionally compact."
    first_part["part_goal"] = f"{first_part['part_goal']} This revision keeps the outline smaller."
    first_part["chapters"] = [first_chapter]
    return {**structure, "parts": [first_part]}


def _add_revision_chapters(structure: dict, revision: str) -> dict:
    parts = [dict(part) for part in structure.get("parts", [])]
    if not parts:
        parts = [{"part_title": "Expanded Structure", "part_goal": "Add requested coverage.", "chapters": []}]

    existing_count = sum(len(part.get("chapters", [])) for part in parts)
    desired_total = _desired_chapter_count(revision, existing_count)
    chapters_to_add = max(1, desired_total - existing_count)
    next_number = _next_chapter_number(parts)
    target_part = parts[-1]
    target_chapters = [dict(chapter) for chapter in target_part.get("chapters", [])]

    templates = [
        (
            "Debugging and Observability for Agent Workflows",
            "Teach readers how to inspect runs, checkpoints, state changes, and model decisions.",
            "Trace a failed revision request from UI event to stored workflow run.",
            "Build a workflow debug dashboard for an agentic book pipeline.",
        ),
        (
            "Working with Source Documents and RAG",
            "Show how PDFs and reference material can ground book chapters.",
            "Upload a PDF, chunk it, and connect retrieved notes to a chapter plan.",
            "Create a source-grounded chapter generator.",
        ),
        (
            "Packaging the Agentic Book Creator",
            "Turn the local workflow into a runnable Docker product with clear operator controls.",
            "Run FastAPI, Streamlit, PostgreSQL, and Gemini configuration through Docker Compose.",
            "Ship a reproducible local authoring environment.",
        ),
    ]
    for index in range(chapters_to_add):
        title, goal, practical_example, mini_project = templates[index % len(templates)]
        target_chapters.append(
            {
                "chapter_number": next_number,
                "title": title,
                "goal": f"{goal} Added from revision request: {revision_requests_label(revision)}.",
                "sections": [
                    {"title": "What the agent is doing", "purpose": "Expose the internal workflow state in human terms."},
                    {"title": "How to debug it", "purpose": "Show the logs, checkpoints, payloads, and run metadata to inspect."},
                    {"title": "How to improve it", "purpose": "Connect user feedback to concrete workflow changes."},
                ],
                "practical_example": practical_example,
                "mini_project": mini_project,
                "exercises": [
                    "Identify one hidden workflow state and make it visible in the UI.",
                    "Add one regression test that proves the workflow changed.",
                ],
            }
        )
        next_number += 1

    target_part["chapters"] = target_chapters
    target_part["part_goal"] = f"{target_part.get('part_goal', 'Expand the book.')} Expanded after revision feedback."
    parts[-1] = target_part
    return {**structure, "parts": parts}


def _desired_chapter_count(revision: str, existing_count: int) -> int:
    for token in revision.replace(",", " ").split():
        if token.isdigit():
            return max(existing_count + 1, int(token))
    return existing_count + 2


def _next_chapter_number(parts: list[dict]) -> int:
    numbers = [
        chapter.get("chapter_number", 0)
        for part in parts
        for chapter in part.get("chapters", [])
        if isinstance(chapter.get("chapter_number", 0), int)
    ]
    return (max(numbers) if numbers else 0) + 1


def revision_requests_label(revision: str) -> str:
    return revision.strip() or "expand the structure"
