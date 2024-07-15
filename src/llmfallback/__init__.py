"""Handles LLM outages and redirects traffic to next-preferred LLM."""

# The version of this package. There's no comprehensive, official list of other
# magic constants, so we stick with this one only for now. See also this conversation:
# https://stackoverflow.com/questions/38344848/is-there-a-comprehensive-table-of-pythons-magic-constants
__version__ = "0.1"

from .exceptions import FailedRequestError
from .wrapper import ModelConfig, ResilientLLM, SyncClientProtocol

__all__ = ["FailedRequestError", "ModelConfig", "ResilientLLM", "SyncClientProtocol"]
