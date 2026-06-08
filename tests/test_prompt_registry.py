from fastapi.testclient import TestClient

from app.api.main import app
from app.prompts.registry import get_prompt, list_prompts


def test_prompt_registry_lists_versioned_prompts_without_templates_by_default():
    prompts = list_prompts()

    assert len(prompts) >= 8
    assert all(prompt["version"] == "mvp-v1" for prompt in prompts)
    assert all("template" not in prompt for prompt in prompts)


def test_prompt_registry_returns_prompt_template_by_name():
    prompt = get_prompt("technical_review")

    assert prompt["name"] == "technical_review"
    assert prompt["model_route"] == "strong_llm"
    assert "Review the chapter" in prompt["template"]


def test_prompt_registry_api_endpoints():
    client = TestClient(app)

    list_response = client.get("/prompts")
    assert list_response.status_code == 200
    assert "template" not in list_response.json()[0]

    get_response = client.get("/prompts/chapter_writer")
    assert get_response.status_code == 200
    assert get_response.json()["output_contract"] == "ChapterDraftMarkdown"

    missing_response = client.get("/prompts/unknown")
    assert missing_response.status_code == 404
