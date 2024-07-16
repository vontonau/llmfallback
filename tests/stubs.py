"""Stub versions of dependencies."""

from typing import Any


class AsyncMockClient:
    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail

    async def create(self, model: str, prompt: str, **kwargs: dict[str, Any]) -> dict[str, Any]:
        if self.should_fail:
            raise Exception("Mock failure")
        return {"response": f"Mock response for prompt: {prompt}"}


class MockClient:
    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail

    def create(self, model: str, prompt: str, **kwargs: dict[str, Any]) -> dict[str, Any]:
        if self.should_fail:
            raise Exception("Mock failure")
        return {"response": f"Mock response for prompt: {prompt}"}
