from app.agents.book_strategy_agent import create_strategy
from app.agents.structure_designer_agent import design_structure


class FakeLLMClient:
    def generate_json(self, system_prompt, user_payload, fallback):
        return {
            "suggested_title": "LLM Generated Title",
            "subtitle": "Generated subtitle",
            "book_promise": "Generated promise",
            "target_reader": "Generated reader",
            "learning_outcomes": ["Generated outcome"],
            "teaching_approach": "Generated approach",
            "style_guide": "Generated style",
            "difficulty_progression": "Generated progression",
            "primary_reader_value": "Generated value",
        }


def test_strategy_agent_uses_llm_client_when_available(monkeypatch):
    import app.agents.book_strategy_agent as strategy_agent

    monkeypatch.setattr(strategy_agent, "llm_client", FakeLLMClient())
    result = create_strategy({"book_requirements": {"main_topic": "AI agents"}})

    assert result["book_strategy"]["suggested_title"] == "LLM Generated Title"


class FakeStructureLLMClient:
    def generate_json(self, system_prompt, user_payload, fallback):
        existing_structure = user_payload["existing_structure"]
        return {
            **existing_structure,
            "last_revision_applied": user_payload["revision_requests"][-1],
            "change_summary": "LLM intentionally preserved the outline.",
        }


def test_structure_agent_does_not_override_llm_revision_output(monkeypatch):
    import app.agents.structure_designer_agent as structure_agent

    monkeypatch.setattr(structure_agent, "llm_client", FakeStructureLLMClient())
    existing_structure = {
        "book_title": "Agentic Systems",
        "parts": [
            {
                "part_title": "Foundations",
                "part_goal": "Teach the basics.",
                "chapters": [{"chapter_number": 1, "title": "Intro", "sections": [], "exercises": []}],
            }
        ],
    }

    result = design_structure(
        {
            "book_structure": existing_structure,
            "structure_revision_requests": ["adiciona mais capítulos sobre debug e RAG"],
        }
    )

    assert result["book_structure"]["change_summary"] == "LLM intentionally preserved the outline."
    assert len(result["book_structure"]["parts"][0]["chapters"]) == 1
