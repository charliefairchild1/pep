"""Document data class — the node type in the Vectora graph."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Document:
    """A node in the Vectora document graph.

    `embedding` is populated by the retriever when added; callers do not need
    to provide one. `metadata` is free-form and surfaces in retrieval results
    so callers can attach IDs, URLs, source labels, anything.
    """

    id: str
    text: str
    embedding: list[float] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("Document.id cannot be empty")
        if not isinstance(self.text, str):
            raise TypeError("Document.text must be a string")
