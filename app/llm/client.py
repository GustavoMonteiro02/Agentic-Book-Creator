from __future__ import annotations

import json
from typing import Any

from app.config import get_settings


class LLMNotConfigured(RuntimeError):
    pass


class LLMClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    def is_configured(self) -> bool:
        if not self.settings.llm_enabled:
            return False
        if self.settings.llm_provider == "gemini":
            return bool(self._gemini_api_key())
        if self.settings.llm_provider == "openai":
            return bool(self.settings.openai_api_key)
        return False

    def generate_json(self, system_prompt: str, user_payload: dict, fallback: dict) -> dict:
        if not self.is_configured():
            return fallback

        try:
            content = self._complete(
                system_prompt=(
                    f"{system_prompt}\n\n"
                    "Return only valid JSON. Do not include markdown fences, commentary, or extra text."
                ),
                user_content=json.dumps(user_payload, ensure_ascii=False),
            )
        except Exception as exc:
            return _fallback_with_llm_error(fallback, exc)
        return _parse_json_or_fallback(content, fallback)

    def generate_text(self, system_prompt: str, user_payload: dict, fallback: str) -> str:
        if not self.is_configured():
            return fallback
        try:
            return self._complete(system_prompt=system_prompt, user_content=json.dumps(user_payload, ensure_ascii=False))
        except Exception:
            return fallback

    def _complete(self, system_prompt: str, user_content: str) -> str:
        if self.settings.llm_provider == "gemini":
            return self._complete_gemini(system_prompt=system_prompt, user_content=user_content)
        if self.settings.llm_provider == "openai":
            return self._complete_openai(system_prompt=system_prompt, user_content=user_content)
        raise LLMNotConfigured(f"Unsupported LLM provider: {self.settings.llm_provider}")

    def _complete_gemini(self, system_prompt: str, user_content: str) -> str:
        try:
            from google import genai
        except ImportError as exc:
            raise LLMNotConfigured("Install the google-genai package to enable Gemini calls.") from exc

        api_key = self._gemini_api_key()
        if not api_key:
            raise LLMNotConfigured("Set GEMINI_API_KEY or GOOGLE_API_KEY to enable Gemini calls.")

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=self.settings.llm_model,
            contents=f"System instructions:\n{system_prompt}\n\nUser payload:\n{user_content}",
        )
        return getattr(response, "text", "") or ""

    def _complete_openai(self, system_prompt: str, user_content: str) -> str:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise LLMNotConfigured("Install the openai package to enable real LLM calls.") from exc

        client = OpenAI(api_key=self.settings.openai_api_key)
        response = client.chat.completions.create(
            model=self.settings.llm_model,
            temperature=0.2,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
        )
        return response.choices[0].message.content or ""

    def _gemini_api_key(self) -> str | None:
        return self.settings.gemini_api_key or self.settings.google_api_key


def _parse_json_or_fallback(content: str, fallback: dict) -> dict:
    try:
        parsed: Any = json.loads(content)
    except json.JSONDecodeError:
        return fallback
    return parsed if isinstance(parsed, dict) else fallback


def _fallback_with_llm_error(fallback: dict, exc: Exception) -> dict:
    return {
        **fallback,
        "llm_runtime": {
            "status": "fallback_used",
            "error_type": exc.__class__.__name__,
            "message": _safe_error_message(exc),
        },
    }


def _safe_error_message(exc: Exception) -> str:
    message = str(exc).replace("\n", " ").strip()
    if len(message) > 500:
        return f"{message[:497]}..."
    return message or exc.__class__.__name__


llm_client = LLMClient()
