"""Base AI client adapters. PEP doesn't reason — it hands a packet here."""

from pep.models.llm_client import (
    AnthropicLLMClient,
    LLMClient,
    StubLLMClient,
    get_llm_client,
)
from pep.models.ollama_client import OllamaLLMClient

__all__ = [
    "AnthropicLLMClient",
    "LLMClient",
    "OllamaLLMClient",
    "StubLLMClient",
    "get_llm_client",
]
