from __future__ import annotations

import litellm
from pydantic import BaseModel, ValidationError

from config.llm_config import LLMConfig
from orchestrator.errors import LLMTimeoutError, SchemaValidationError


class LLMClient:
    def __init__(self, config: LLMConfig) -> None:
        self._config = config

    def complete(self, system: str, user: str) -> tuple[str, int]:
        try:
            response = litellm.completion(
                model=self._config.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                api_base=self._config.base_url,
                timeout=self._config.timeout_seconds,
            )
        except litellm.exceptions.Timeout as exc:
            raise LLMTimeoutError(f"LLM call timed out after {self._config.timeout_seconds}s") from exc

        text: str = response.choices[0].message.content or ""
        tokens: int = response.usage.total_tokens if response.usage else 0
        return text, tokens

    def complete_json(self, system: str, user: str, schema: type[BaseModel]) -> BaseModel:
        text, _ = self.complete(system, user)
        try:
            return schema.model_validate_json(text)
        except ValidationError:
            text, _ = self.complete(system, user)
            try:
                return schema.model_validate_json(text)
            except ValidationError as exc:
                raise SchemaValidationError(
                    f"LLM response did not match {schema.__name__} after retry"
                ) from exc
