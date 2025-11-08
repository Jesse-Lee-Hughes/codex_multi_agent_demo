"""Utility helpers for integrating Croaked with OpenAI models."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

try:  # pragma: no cover - exercised indirectly
    from openai import OpenAI  # type: ignore
    from openai import APIStatusError, InternalServerError  # type: ignore
except ImportError:  # pragma: no cover - handled via availability flag
    OpenAI = None
    APIStatusError = InternalServerError = Exception


HARD_TOKEN_LIMIT = 200_000


class LanguageResponderError(RuntimeError):
    """Raised when the language model cannot produce a response."""


@dataclass(slots=True)
class OpenAIResponder:
    """Thin wrapper around OpenAI's Responses API."""

    model: str
    max_output_tokens: int = 2048
    temperature: Optional[float] = None
    _client: Optional[OpenAI] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        key = os.getenv("OPENAI_API_KEY")
        if OpenAI is None or not key:
            return

        try:
            self._client = OpenAI(api_key=key)
        except Exception as exc:  # pragma: no cover - defensive
            raise LanguageResponderError(str(exc)) from exc

    @property
    def available(self) -> bool:
        return self._client is not None

    def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        if not self._client:
            raise LanguageResponderError("OpenAI client is not available.")

        request_kwargs = {
            "model": self.model,
            "input": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_output_tokens": min(self.max_output_tokens, HARD_TOKEN_LIMIT),
            "reasoning": {"effort": "low"},
        }
        if self.temperature is not None:
            request_kwargs["temperature"] = self.temperature

        try:
            response = self._client.responses.create(**request_kwargs)
        except (APIStatusError, InternalServerError, TimeoutError) as exc:
            raise LanguageResponderError(str(exc)) from exc
        except Exception as exc:  # pragma: no cover - defensive
            raise LanguageResponderError(str(exc)) from exc

        output_text = getattr(response, "output_text", None)

        if not output_text:
            pieces: list[str] = []

            output_chunks = getattr(response, "output", None)
            if output_chunks:
                for chunk in output_chunks:
                    content_list = None
                    if hasattr(chunk, "content"):
                        content_list = chunk.content
                    elif isinstance(chunk, dict):
                        content_list = chunk.get("content")
                    if not content_list:
                        continue
                    for content in content_list:
                        content_type = getattr(content, "type", None)
                        if content_type is None and isinstance(content, dict):
                            content_type = content.get("type")
                        if content_type == "output_text":
                            text_value = getattr(content, "text", None)
                            if text_value is None and isinstance(content, dict):
                                text_value = content.get("text")
                            if text_value:
                                pieces.append(text_value)
            if not pieces and hasattr(response, "model_dump"):
                data = response.model_dump(mode="python")
                for chunk in data.get("output", []):
                    if not isinstance(chunk, dict):
                        continue
                    for content in chunk.get("content", []) or []:
                        if content.get("type") == "output_text" and content.get("text"):
                            pieces.append(content["text"])

            output_text = "".join(pieces).strip()

        if not output_text:
            payload = None
            if hasattr(response, "model_dump"):
                payload = response.model_dump(mode="python")
            raise LanguageResponderError(
                f"No content returned from OpenAI. payload={payload}"
            )

        return output_text.strip()
