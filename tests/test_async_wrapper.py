"""Test LLMFallback main functionality."""

import pytest
from llmfallback import FailedRequestError, ModelConfig, AsyncResilientLLM
from stubs import AsyncMockClient, MockClient

@pytest.mark.asyncio
async def test_async_resilient_llm_completion():
    """Test that checks that async_completion method works correctly."""
    # Create mock clients
    successful_client = AsyncMockClient()
    failing_client = AsyncMockClient(should_fail=True)

    # Create model configs
    model1 = ModelConfig("model1", successful_client)
    model2 = ModelConfig("model2", failing_client)
    model3 = ModelConfig("model3", successful_client)

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

    model1 = ModelConfig("model1", failing_client)
    model2 = ModelConfig("model2", successful_client)

    llm = AsyncResilientLLM([model1, model2])

    response = await llm.async_completion("Test prompt")
    assert response == {"response": "Mock response for prompt: Test prompt"}
    assert response == await llm.async_completion("Test prompt")

@pytest.mark.asyncio
async def test_async_all_failed():
    """Test that checks that async_completion raises an error if all models fail."""
    failing_client = AsyncMockClient(should_fail=True)

    model1 = ModelConfig("model1", failing_client)
    model2 = ModelConfig("model2", failing_client)
    llm = AsyncResilientLLM([model1, model2])

    with pytest.raises(FailedRequestError):
        await llm.async_completion("Test prompt")


@pytest.mark.asyncio
async def test_only_awaitable_clients():
    """Test that async resilientllm only allows awaitable clients."""
    client = MockClient()
    model1 = ModelConfig("model1", client)
    llm = AsyncResilientLLM([model1])

    with pytest.raises(TypeError):
        await llm.async_completion("Test prompt")