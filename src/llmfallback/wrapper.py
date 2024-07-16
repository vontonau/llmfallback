"""Contains wrapper over LLM clients that handles outages by switching to the next-preferred model."""

import time
import inspect
from dataclasses import dataclass
from typing import Any, Protocol, TypeVar, Generic

from .exceptions import FailedRequestError


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


class AsyncClientProtocol(Protocol):
    """Protocol for calling models using async clients."""

    async def create(self, model: str, prompt: str, **kwargs: dict[str, Any]) -> dict[str, Any]:
        """
        Call model using async method.

        :param model: The name of the model to use.
        :param prompt: The input prompt for the model.
        :param kwargs: Additional keyword arguments for the model.
        :return: The response from the model.
        """


# Define a type variable for the client
ClientType = TypeVar('ClientType', SyncClientProtocol, AsyncClientProtocol)


@dataclass
class ModelConfig(Generic[ClientType]):
    """
    Configuration class for language models.

    :param name: The name of the model.
    :param client: The client for this model, either SyncClientProtocol or AsyncClientProtocol.
    """

    name: str
    client: ClientType


class _ResilientLLM(Generic[ClientType]):
    """
    A base wrapper class for language model APIs with built-in resilience.

    This class provides a fault-tolerant interface for making completion
    requests to language models from different providers.

    :param models: A list of ModelConfig objects containing model information and clients.
    :param failure_window: The time window (in seconds) for tracking failures.
    """

    def __init__(self, models: list[ModelConfig[ClientType]], failure_window: int = 3600):
        self.models: list[ModelConfig] = models
        self.failure_window: int = failure_window
        self.model_failures: dict[str, float] = {model.name: 0.0 for model in models}

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


class ResilientLLM(_ResilientLLM[SyncClientProtocol]):
    """
    A  wrapper class for language model APIs with built-in resilience.

    This class provides a fault-tolerant interface for making completion
    requests to language models from different providers.

    :param models: A list of ModelConfig objects containing model information and clients.
    :param failure_window: The time window (in seconds) for tracking failures.
    """

    def completion(self, prompt: str, **kwargs: dict[str, Any]) -> dict[str, Any]:
        """
        Make a completion request to the language model.

        :param prompt: The input prompt for the completion request.
        :param kwargs: Additional keyword arguments to pass to the API.
        :return: The response from the language model.
        :rtype: dict[str, Any]
        :raises FailedRequestError: If all models have recently failed and no completion could be made.
        :raises ValueError: If one of the models uses async API.
        """
        for model in self.models:
            if not self._has_recently_failed(model.name):
                client = model.client
                if inspect.isawaitable(client.create):
                    raise ValueError("Use async_completion method for calling async clients.")

                try:
                    response = client.create(model=model.name, prompt=prompt, **kwargs)
                    return response
                except Exception:
                    self._record_failure(model.name)

        raise FailedRequestError("All models have recently failed. No available models to process the request.")


class AsyncResilientLLM(_ResilientLLM[AsyncClientProtocol]):
    """
    A wrapper class for language model async APIs with built-in resilience.

    This class provides a fault-tolerant interface for making completion
    requests to language models from different providers.

    :param models: A list of ModelConfig objects containing model information and clients.
    :param failure_window: The time window (in seconds) for tracking failures.
    """

    async def async_completion(self, prompt: str, **kwargs: dict[str, Any]) -> dict[str, Any]:
        """
        Make an async completion request to the language model.

        :param prompt: The input prompt for the completion request.
        :param kwargs: Additional keyword arguments to pass to the API.
        :return: The response from the language model.
        :rtype: dict[str, Any]
        :raises FailedRequestError: If all models have recently failed and no completion could be made.
        raises ValueError: If one of the models uses sync API.
        """
        for model in self.models:
            if not self._has_recently_failed(model.name):
                client = model.client
                if not inspect.isawaitable(client.create):
                    raise ValueError("Use completion method for calling sync clients.")

                try:
                    response = client.create(model=model.name, prompt=prompt, **kwargs)
                    return response
                except Exception:
                    self._record_failure(model.name)

        raise FailedRequestError("All models have recently failed. No available models to process the request.")