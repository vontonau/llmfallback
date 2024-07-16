"""Test LLMFallback main functionality."""

from typing import Any

import pytest

from llmfallback import FailedRequestError, ModelConfig, ResilientLLM
from stubs import MockClient, AsyncMockClient


def test_resilient_llm_completion():
    """Test that checks that create completion method works correctly."""
    # Create mock clients
    successful_client = MockClient()
    failing_client = MockClient(should_fail=True)

    # Create model configs
    model1 = ModelConfig("model1", successful_client)
    model2 = ModelConfig("model2", failing_client)
    model3 = ModelConfig("model3", successful_client)

    # Create ResilientLLM instance
    llm = ResilientLLM([model1, model2, model3])

    # Test successful completion
    response = llm.completion("Test prompt")
    assert response == {"response": "Mock response for prompt: Test prompt"}

    # Test fallback to next model
    model1.client = failing_client
    response = llm.completion("Test prompt")
    assert response == {"response": "Mock response for prompt: Test prompt"}

    # Test all models failing
    model3.client = failing_client
    with pytest.raises(FailedRequestError):
        llm.completion("Test prompt")


def test_switching():
    """Test that checks that create completion switches to the not-failing model."""
    successful_client = MockClient()
    failing_client = MockClient(should_fail=True)

    model1 = ModelConfig("model1", failing_client)
    model2 = ModelConfig("model2", successful_client)

    llm = ResilientLLM([model1, model2])

    response = llm.completion("Test prompt")
    assert response == {"response": "Mock response for prompt: Test prompt"}
    assert response == llm.completion("Test prompt")


def test_all_failed():
    """Test that checks that create completion raises an error if all models fail."""
    failing_client = MockClient(should_fail=True)

    model1 = ModelConfig("model1", failing_client)
    model2 = ModelConfig("model2", failing_client)
    llm = ResilientLLM([model1, model2])

    with pytest.raises(FailedRequestError):
        llm.completion("Test prompt")


def test_only_sync_clients():
    """Test that async resilientllm only allows regular callable clients."""
    client = AsyncMockClient()
    model1 = ModelConfig("model1", client)
    llm = ResilientLLM([model1])

    with pytest.raises(TypeError):
        llm.completion("Test prompt")