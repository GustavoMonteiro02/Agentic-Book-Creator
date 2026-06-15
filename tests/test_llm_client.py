from app.llm.client import _fallback_with_llm_error
from app.llm.client import _parse_json_or_fallback
from app.llm.client import LLMClient


class SettingsStub:
    llm_enabled = True
    llm_provider = "gemini"
    llm_model = "gemini-2.5-flash"
    openai_api_key = None
    gemini_api_key = "gemini-key"
    google_api_key = None


def test_parse_json_or_fallback_returns_valid_json_object():
    result = _parse_json_or_fallback('{"answer": "ok"}', {"answer": "fallback"})

    assert result == {"answer": "ok"}


def test_parse_json_or_fallback_uses_fallback_for_invalid_json():
    fallback = {"answer": "fallback"}

    assert _parse_json_or_fallback("not json", fallback) == fallback
    assert _parse_json_or_fallback("[1, 2]", fallback) == fallback


def test_llm_client_is_configured_with_gemini_key():
    client = LLMClient()
    client.settings = SettingsStub()

    assert client.is_configured() is True


def test_json_generation_uses_diagnostic_fallback_when_provider_fails(monkeypatch):
    client = LLMClient()
    client.settings = SettingsStub()

    def fail_completion(system_prompt, user_content):
        raise RuntimeError("429 RESOURCE_EXHAUSTED retry later")

    monkeypatch.setattr(client, "_complete", fail_completion)
    result = client.generate_json("system", {"topic": "agents"}, {"answer": "fallback"})

    assert result["answer"] == "fallback"
    assert result["llm_runtime"]["status"] == "fallback_used"
    assert result["llm_runtime"]["error_type"] == "RuntimeError"
    assert "RESOURCE_EXHAUSTED" in result["llm_runtime"]["message"]


def test_fallback_error_message_is_truncated():
    result = _fallback_with_llm_error({"answer": "fallback"}, RuntimeError("x" * 600))

    assert result["llm_runtime"]["message"].endswith("...")
    assert len(result["llm_runtime"]["message"]) == 500
