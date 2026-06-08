from app.agents.input_gathering_agent import gather_input


def test_gather_input_asks_only_for_missing_information():
    state = {
        "initial_user_idea": "Livro prático sobre agentes de IA para RPA developers com código e mini projetos.",
        "user_answers": [],
    }

    result = gather_input(state)

    fields = [question["field"] for question in result["input_questions"]]
    assert "target_audience" not in fields
    assert "chapter_format" not in fields
    assert result["status"] == "awaiting_input"
