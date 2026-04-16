"""Embedding client.

Voyage AI when VOYAGE_API_KEY is set; deterministic hash-based pseudo-vectors
otherwise. The pseudo-vectors are NOT good embeddings — they let Phase 1 run
end-to-end without any external API calls. Real semantic retrieval kicks in
once the key is set.
"""

from __future__ import annotations

import hashlib
import os
import struct
from typing import Sequence

EMBEDDING_DIM = 1024


def _hash_pseudo_embedding(text: str) -> list[float]:
    """Deterministic, dimension-stable, but semantically meaningless.

    Used as a fallback so the rest of PEP can run without VOYAGE_API_KEY.
    Replace with real embeddings as soon as a key is available.
    """
    h = hashlib.sha512(text.encode("utf-8")).digest()
    # repeat the hash until we have enough bytes for EMBEDDING_DIM floats
    needed = EMBEDDING_DIM * 4
    repeats = (needed // len(h)) + 1
    blob = (h * repeats)[:needed]
    floats = struct.unpack(f"{EMBEDDING_DIM}f", blob)
    # normalize so cosine similarity is well-behaved
    norm = sum(f * f for f in floats) ** 0.5 or 1.0
    return [f / norm for f in floats]


class Embedder:
    def __init__(self, model: str = "voyage-3"):
        self.model = model
        self._client = None
        self._using_voyage = bool(os.environ.get("VOYAGE_API_KEY"))
        if self._using_voyage:
            try:
                import voyageai

                self._client = voyageai.Client()
            except Exception:
                self._using_voyage = False

    @property
    def using_real_embeddings(self) -> bool:
        return self._using_voyage

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        if self._using_voyage and self._client:
            try:
                result = self._client.embed(list(texts), model=self.model, input_type="document")
                return result.embeddings
            except Exception:
                # fall through to pseudo-embeddings on transient API errors
                pass
        return [_hash_pseudo_embedding(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        if self._using_voyage and self._client:
            try:
                result = self._client.embed([text], model=self.model, input_type="query")
                return result.embeddings[0]
            except Exception:
                pass
        return _hash_pseudo_embedding(text)


def cosine(a: Sequence[float], b: Sequence[float]) -> float:
    if len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)
