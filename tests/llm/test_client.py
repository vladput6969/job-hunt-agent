from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel

from config.llm_config import LLMConfig
from llm.client import LLMClient
from orchestrator.errors import LLMTimeoutError, SchemaValidationError


@pytest.fixture
def config() -> LLMConfig:
    return LLMConfig(
        model="ollama/llama3.1:8b",
        base_url="http://localhost:11434",
        timeout_seconds=30,
        token_budget_per_cycle=50000,
    )


@pytest.fixture
def client(config: LLMConfig) -> LLMClient:
    return LLMClient(config)


def _mock_response(text: str, total_tokens: int = 42) -> MagicMock:
    usage = MagicMock()
    usage.total_tokens = total_tokens
    choice = MagicMock()
    choice.message.content = text
    response = MagicMock()
    response.choices = [choice]
    response.usage = usage
    return response


class _Schema(BaseModel):
    name: str
    score: int


def test_complete_returns_text_and_token_count(client):
    with patch("litellm.completion", return_value=_mock_response("hello", 10)) as mock:
        text, tokens = client.complete("sys", "usr")
    assert text == "hello"
    assert tokens == 10
    mock.assert_called_once()


def test_complete_raises_llm_timeout_error_on_timeout(client):
    import litellm as _litellm
    timeout_exc = _litellm.exceptions.Timeout(
        message="timed out", model="ollama/llama3.1:8b", llm_provider="ollama"
    )
    with patch("litellm.completion", side_effect=timeout_exc):
        with pytest.raises(LLMTimeoutError):
            client.complete("sys", "usr")


def test_complete_json_parses_valid_response(client):
    payload = '{"name": "Alice", "score": 95}'
    with patch("litellm.completion", return_value=_mock_response(payload)):
        result = client.complete_json("sys", "usr", _Schema)
    assert isinstance(result, _Schema)
    assert result.name == "Alice"
    assert result.score == 95


def test_complete_json_retries_on_invalid_json(client):
    good = '{"name": "Bob", "score": 80}'
    responses = [_mock_response("not json"), _mock_response(good)]
    with patch("litellm.completion", side_effect=responses):
        result = client.complete_json("sys", "usr", _Schema)
    assert result.name == "Bob"


def test_complete_json_raises_schema_validation_error_after_retry(client):
    with patch("litellm.completion", return_value=_mock_response("still not json")):
        with pytest.raises(SchemaValidationError):
            client.complete_json("sys", "usr", _Schema)
