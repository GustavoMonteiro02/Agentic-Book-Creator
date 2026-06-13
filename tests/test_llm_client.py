from app.llm.client import _parse_json_or_fallback


def test_parse_json_or_fallback_returns_valid_json_object():
    result = _parse_json_or_fallback('{"answer": "ok"}', {"answer": "fallback"})

    assert result == {"answer": "ok"}


def test_parse_json_or_fallback_uses_fallback_for_invalid_json():
    fallback = {"answer": "fallback"}

    assert _parse_json_or_fallback("not json", fallback) == fallback
    assert _parse_json_or_fallback("[1, 2]", fallback) == fallback
