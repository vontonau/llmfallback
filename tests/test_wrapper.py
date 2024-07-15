"""Test LLMFallback main functionality."""

from typing import Any

import pytest

from llmfallback import FailedRequestError, ModelConfig, ResilientLLM


class MockClient:
    """
    A mock version of LLM client.

    :param should_fail: If True, client will always raise an exception.
    """

    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail

    # pylint: disable-next = unused-argument
    def create(self, model: str, prompt: str, **kwargs: dict[str, Any]) -> dict[str, Any]:
        """
        Create mocked prompt.

        :param model: The name of the model to create prompt with
        :param prompt: Prompt for the model
        :param kwargs: additional arguments
        :return: Dictionary containing result of LLM call
        :raises Exception: If client is set to fail, exception will be raised.
        """
        if self.should_fail:
            raise OSError("API call failure")
        return {"response": f"Mock response for prompt: {prompt}"}


def test_resilient_llm_completion():
    """Test that checks that create completion method works correctly."""
    # Create mock clients
    successful_client = MockClient()
    failing_client = MockClient(should_fail=True)

    # Create model configs
    model1 = ModelConfig("model1", "openai", successful_client)
    model2 = ModelConfig("model2", "gemini", failing_client)
    model3 = ModelConfig("model3", "openai", successful_client)

    # Create ResilientLLM instance
    llm = ResilientLLM([model1, model2, model3])

    # Test successful completion
    response = llm.completion("Test prompt")
    assert response == {"response": "Mock response for prompt: Test prompt"}

    # Test fallback to next model
    model1.sync_client = failing_client
    response = llm.completion("Test prompt")
    assert response == {"response": "Mock response for prompt: Test prompt"}

    # Test all models failing
    model3.sync_client = failing_client
    with pytest.raises(FailedRequestError):
        llm.completion("Test prompt")


def test_switching():
    """Test that checks that create completion switches to the not-failing model."""
    successful_client = MockClient()
    failing_client = MockClient(should_fail=True)

    model1 = ModelConfig("model1", "openai", failing_client)
    model2 = ModelConfig("model2", "openai", successful_client)

    llm = ResilientLLM([model1, model2])

    response = llm.completion("Test prompt")
    assert response == {"response": "Mock response for prompt: Test prompt"}
    assert response == llm.completion("Test prompt")


def test_all_failed():
    """Test that checks that create completion raises an error if all models fail."""
    failing_client = MockClient(should_fail=True)

    model1 = ModelConfig("model1", "openai", failing_client)
    model2 = ModelConfig("model2", "openai", failing_client)
    llm = ResilientLLM([model1, model2])

    with pytest.raises(FailedRequestError):
        llm.completion("Test prompt")
