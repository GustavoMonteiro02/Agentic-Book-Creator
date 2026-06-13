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
