from app.agents.state import BookState
from app.llm.client import llm_client
from app.prompts.book_strategy_prompt import BOOK_STRATEGY_PROMPT


def create_strategy(state: BookState) -> BookState:
    requirements = state.get("book_requirements", {})
    topic = requirements.get("main_topic", "Agentic AI")
    audience = requirements.get("target_audience", "automation developers")

    strategy = {
        "suggested_title": "Building Agentic AI Systems",
        "subtitle": "A practical guide for automation engineers and developers",
        "book_promise": f"Turn {topic} into practical, production-minded workflows.",
        "target_reader": audience,
        "learning_outcomes": [
            "Design stateful agent workflows",
            "Use structured outputs and human approval gates",
            "Connect FastAPI, persistence, tracing, and RAG into one system",
        ],
        "teaching_approach": "Progressive chapters that combine concepts, examples, code, and mini projects.",
        "style_guide": requirements.get("tone", "practical and clear"),
        "difficulty_progression": "Start with mental models, move into workflows, then production concerns.",
        "primary_reader_value": "A concrete path from agent demos to maintainable agentic applications.",
    }

    strategy = llm_client.generate_json(
        system_prompt=BOOK_STRATEGY_PROMPT,
        user_payload={"book_requirements": requirements},
        fallback=strategy,
    )

    return {**state, "book_strategy": strategy, "status": "strategy_ready"}
