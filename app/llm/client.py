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
        return bool(self.settings.llm_enabled and self.settings.openai_api_key)

    def generate_json(self, system_prompt: str, user_payload: dict, fallback: dict) -> dict:
        if not self.is_configured():
            return fallback

        content = self._complete(
            system_prompt=(
                f"{system_prompt}\n\n"
                "Return only valid JSON. Do not include markdown fences, commentary, or extra text."
            ),
            user_content=json.dumps(user_payload, ensure_ascii=False),
        )
        return _parse_json_or_fallback(content, fallback)

    def generate_text(self, system_prompt: str, user_payload: dict, fallback: str) -> str:
        if not self.is_configured():
            return fallback
        return self._complete(system_prompt=system_prompt, user_content=json.dumps(user_payload, ensure_ascii=False))

    def _complete(self, system_prompt: str, user_content: str) -> str:
        if self.settings.llm_provider != "openai":
            raise LLMNotConfigured(f"Unsupported LLM provider: {self.settings.llm_provider}")

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


def _parse_json_or_fallback(content: str, fallback: dict) -> dict:
    try:
        parsed: Any = json.loads(content)
    except json.JSONDecodeError:
        return fallback
    return parsed if isinstance(parsed, dict) else fallback


llm_client = LLMClient()
