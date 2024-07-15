"""Contains wrapper over LLM clients that handles outages by switching to the next-preferred model."""

import time
from typing import Any, Literal, Protocol

from .exceptions import FailedRequestError

ProviderType = Literal["openai", "gemini"]


class SyncClientProtocol(Protocol):
    """Protocol for calling models using sync clients."""

    def create(self, model: str, prompt: str, **kwargs: dict[str, Any]) -> dict[str, Any]:
        """
        Call model using sync method.

        :param model: The name of the model to use.
        :param prompt: The input prompt for the model.
        :param kwargs: Additional keyword arguments for the model.
        :return: The response from the model.
        """


class ModelConfig:
    """
    Configuration class for language models.

    :param name: The name of the model.
    :param provider: The provider of the model (either "openai" or "gemini").
    :param sync_client: The synchronous client for this model.
    """

    def __init__(self, name: str, provider: ProviderType, sync_client: SyncClientProtocol):
        self.name: str = name
        self.provider: ProviderType = provider
        self.sync_client: SyncClientProtocol = sync_client


class ResilientLLM:
    """
    A wrapper class for language model APIs with built-in resilience.

    This class provides a fault-tolerant interface for making completion
    requests to language models from different providers.

    :param models: A list of ModelConfig objects containing model information and clients.
    :param failure_window: The time window (in seconds) for tracking failures.
    """

    def __init__(self, models: list[ModelConfig], failure_window: int = 3600):
        self.models: list[ModelConfig] = models
        self.failure_window: int = failure_window
        self.model_failures: dict[str, float] = {model.name: 0.0 for model in models}

    def completion(self, prompt: str, **kwargs: dict[str, str]) -> dict[str, str]:
        """
        Make a completion request to the language model.

        :param prompt: The input prompt for the completion request.
        :param kwargs: Additional keyword arguments to pass to the API.
        :return: The response from the language model.
        :rtype: dict[str, Any]
        :raises FailedRequestError: If all models have recently failed and no completion could be made.
        """
        for model in self.models:
            if not self._has_recently_failed(model.name):
                try:
                    response = model.sync_client.create(model=model.name, prompt=prompt, **kwargs)
                    return response
                except Exception:
                    self._record_failure(model.name)

        raise FailedRequestError("All models have recently failed. No available models to process the request.")

    def _has_recently_failed(self, model: str) -> bool:
        """
        Check if a model has failed in the recent time window.

        :param model: The name of the model to check.
        :return: True if the model has failed recently, False otherwise.
        """
        current_time = time.time()
        return current_time - self.model_failures[model] < self.failure_window

    def _record_failure(self, model: str) -> None:
        """
        Record a failure for a specific model.

        :param model: The name of the model that failed.
        """
        self.model_failures[model] = time.time()
