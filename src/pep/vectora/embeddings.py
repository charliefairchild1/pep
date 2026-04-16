"""Embedding clients for Vectora.

Two embedders:
- LocalEmbedder: TF-IDF-style bag-of-token embedding. Free, deterministic,
  produces semantically meaningful similarity (overlap-based) without an
  external API. Good enough for demos, dev, and tests.
- A Voyage-backed embedder is wired through PEP's existing pep.embed.Embedder
  when VOYAGE_API_KEY is set. The protocol below lets the retriever accept
  either.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from typing import Protocol, Sequence


_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


class EmbedderProtocol(Protocol):
    """Anything that turns a list of texts into a list of vectors."""

    def embed(self, texts: Sequence[str]) -> list[list[float]]: ...


class LocalEmbedder:
    """TF-IDF embedder fitted on the corpus you embed with it.

    The first call to embed() builds the IDF vocabulary; subsequent calls
    project new text into the same space. Vectors are L2-normalized so cosine
    similarity is just a dot product.

    Not as good as a real embedding model but produces real semantic-ish
    similarity — documents with overlapping vocabulary score high, unrelated
    documents score near zero. Sufficient to demonstrate the spreading-
    activation advantage on real text.
    """

    def __init__(self, dim: int = 256) -> None:
        self.dim = dim
        self.vocab: dict[str, int] = {}  # token → index in [0, dim)
        self.idf: dict[str, float] = {}
        self._fitted = False

    def _fit(self, texts: Sequence[str]) -> None:
        # Collect document frequencies
        df: Counter[str] = Counter()
        for t in texts:
            tokens = set(_tokenize(t))
            df.update(tokens)
        # Pick the top `dim` tokens by document frequency × log-inverse
        # (skip tokens that appear in >80% of docs — too generic)
        n = max(1, len(texts))
        scored: list[tuple[float, str]] = []
        for tok, c in df.items():
            if c / n > 0.8:
                continue
            idf = math.log((n + 1) / (c + 1)) + 1
            # priority for vocab inclusion: balance frequency and discriminativeness
            scored.append((c * idf, tok))
        scored.sort(reverse=True)
        for i, (_, tok) in enumerate(scored[: self.dim]):
            self.vocab[tok] = i
            self.idf[tok] = math.log((n + 1) / (df[tok] + 1)) + 1
        self._fitted = True

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        if not self._fitted:
            self._fit(texts)
        out: list[list[float]] = []
        for t in texts:
            vec = [0.0] * self.dim
            tokens = _tokenize(t)
            tf = Counter(tokens)
            for tok, count in tf.items():
                idx = self.vocab.get(tok)
                if idx is None:
                    continue
                vec[idx] = count * self.idf.get(tok, 1.0)
            # L2 normalize
            norm = math.sqrt(sum(v * v for v in vec)) or 1.0
            out.append([v / norm for v in vec])
        return out


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    """Cosine similarity. Assumes vectors are already L2-normalized; if not,
    returns the unnormalized dot product (still usable for ranking)."""
    if len(a) != len(b):
        raise ValueError(f"vector dimension mismatch: {len(a)} vs {len(b)}")
    return sum(x * y for x, y in zip(a, b))
