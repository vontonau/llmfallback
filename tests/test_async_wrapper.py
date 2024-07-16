"""Test LLMFallback main functionality."""

import pytest
from typing import Any
from llmfallback import FailedRequestError, ModelConfig, AsyncResilientLLM


class AsyncMockClient:
    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail

    async def create(self, model: str, prompt: str, **kwargs: dict[str, Any]) -> dict[str, Any]:
        if self.should_fail:
            raise Exception("Mock failure")
        return {"response": f"Mock response for prompt: {prompt}"}

@pytest.mark.asyncio
async def test_async_resilient_llm_completion():
    """Test that checks that async_completion method works correctly."""
    # Create mock clients
    successful_client = AsyncMockClient()
    failing_client = AsyncMockClient(should_fail=True)

    # Create model configs
    model1 = ModelConfig("model1", "openai", successful_client)
    model2 = ModelConfig("model2", "gemini", failing_client)
    model3 = ModelConfig("model3", "openai", successful_client)

    # Create AsyncResilientLLM instance
    llm = AsyncResilientLLM([model1, model2, model3])

    # Test successful completion
    response = await llm.async_completion("Test prompt")
    assert response == {"response": "Mock response for prompt: Test prompt"}

    # Test fallback to next model
    model1.client = failing_client
    response = await llm.async_completion("Test prompt")
    assert response == {"response": "Mock response for prompt: Test prompt"}

    # Test all models failing
    model3.client = failing_client
    with pytest.raises(FailedRequestError):
        await llm.async_completion("Test prompt")

@pytest.mark.asyncio
async def test_async_switching():
    """Test that checks that async_completion switches to the not-failing model."""
    successful_client = AsyncMockClient()
    failing_client = AsyncMockClient(should_fail=True)

    model1 = ModelConfig("model1", "openai", failing_client)
    model2 = ModelConfig("model2", "openai", successful_client)

    llm = AsyncResilientLLM([model1, model2])

    response = await llm.async_completion("Test prompt")
    assert response == {"response": "Mock response for prompt: Test prompt"}
    assert response == await llm.async_completion("Test prompt")

@pytest.mark.asyncio
async def test_async_all_failed():
    """Test that checks that async_completion raises an error if all models fail."""
    failing_client = AsyncMockClient(should_fail=True)

    model1 = ModelConfig("model1", "openai", failing_client)
    model2 = ModelConfig("model2", "openai", failing_client)
    llm = AsyncResilientLLM([model1, model2])

    with pytest.raises(FailedRequestError):
        await llm.async_completion("Test prompt")
