from app.agents.state import BookState


def design_structure(state: BookState) -> BookState:
    strategy = state.get("book_strategy", {})
    title = strategy.get("suggested_title", "Building Agentic AI Systems")

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

    return {**state, "book_structure": structure, "status": "structure_ready"}
