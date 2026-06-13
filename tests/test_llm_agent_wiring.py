from app.agents.book_strategy_agent import create_strategy


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
