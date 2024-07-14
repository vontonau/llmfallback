"""A set of tests for ResilientLLM class."""

from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest
from hypothesis import given
from hypothesis import strategies as st

from llmfallback import FailedRequestError, ModelConfig, ResilientLLM


# Helper function to create a mock client
def create_mock_client(is_async: bool = False) -> Mock | AsyncMock:
    """Create a mock for LLM client."""
    client: Mock | AsyncMock = AsyncMock() if is_async else Mock()
    client.create = AsyncMock() if is_async else Mock()
    return client


# Test strategy for ModelConfig
model_config_st = st.builds(
    ModelConfig,
    name=st.text(min_size=1, max_size=50),
    provider=st.sampled_from(["openai", "gemini"]),
    sync_client=st.just(create_mock_client()),
    async_client=st.just(create_mock_client(is_async=True)),
)


@given(
    models=st.lists(model_config_st, min_size=1, max_size=5),
    failure_threshold=st.integers(min_value=1, max_value=10),
    failure_window=st.integers(min_value=1, max_value=3600),
    prompt=st.text(min_size=1, max_size=1000),
)
def test_completion_successful_request(
    models: list[ModelConfig], failure_threshold: int, failure_window: int, prompt: str
) -> None:
    """Test that a successful request returns the expected response."""
    llm = ResilientLLM(models, failure_threshold, failure_window)
    expected_response: dict[str, list[dict[str, str]]] = {"choices": [{"text": "Mock response"}]}

    for model in models:
        model.sync_client.create.return_value = expected_response

    response: dict[str, Any] = llm.completion(prompt)
    assert response == expected_response
    assert models[0].sync_client.create.called


@given(
    models=st.lists(model_config_st, min_size=1, max_size=5),
    failure_threshold=st.integers(min_value=1, max_value=10),
    failure_window=st.integers(min_value=1, max_value=3600),
    prompt=st.text(min_size=1, max_size=1000),
)
def test_completion_all_models_fail(
    models: list[ModelConfig], failure_threshold: int, failure_window: int, prompt: str
) -> None:
    """Test that an exception is raised when all models fail."""
    llm = ResilientLLM(models, failure_threshold, failure_window)

    for model in models:
        model.sync_client.create.side_effect = Exception("API error")

    with pytest.raises(FailedRequestError):
        llm.completion(prompt)

    assert all(model.sync_client.create.called for model in models)


@given(
    models=st.lists(model_config_st, min_size=2, max_size=5),
    failure_threshold=st.integers(min_value=1, max_value=10),
    failure_window=st.integers(min_value=1, max_value=3600),
    prompt=st.text(min_size=1, max_size=1000),
)
def test_completion_fallback_to_next_model(
    models: list[ModelConfig], failure_threshold: int, failure_window: int, prompt: str
) -> None:
    """Test that the system falls back to the next model when the first one fails."""
    llm = ResilientLLM(models, failure_threshold, failure_window)
    expected_response: dict[str, list[dict[str, str]]] = {"choices": [{"text": "Mock response"}]}

    # Make the first model fail, and the second model succeed
    models[0].sync_client.create.side_effect = Exception("API error")
    models[1].sync_client.create.return_value = expected_response

    response: dict[str, Any] = llm.completion(prompt)
    assert response == expected_response
    assert models[0].sync_client.create.called
    assert models[1].sync_client.create.called
