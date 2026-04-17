"""Token estimation for prompts.

Approximates BPE tokenization without a real tokenizer dependency. The
ratio `ceil(len(text) / 4)` matches GPT-4's average chars-per-token on
English text to within ~5%. For code and heavily-punctuated text we add
a small correction. Good enough for cost forecasting and iteration; the
real production path swaps in `tiktoken` if installed.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass


# Word boundary + punctuation boundary
_WORD_RE = re.compile(r"\w+|[^\w\s]")
# Heuristic: code-like markers that increase token density
_CODE_MARKERS = re.compile(r"[{}\[\]()<>/\\=|;:]")


@dataclass(frozen=True)
class TokenEstimate:
    total: int
    words: int
    chars: int
    method: str  # "bpe-approx" or "tiktoken"


def _try_tiktoken(text: str, model: str = "gpt-4") -> int | None:
    """Use tiktoken if installed; otherwise return None."""
    try:
        import tiktoken  # type: ignore[import-untyped]
    except ImportError:
        return None
    try:
        enc = tiktoken.encoding_for_model(model)
    except Exception:
        try:
            enc = tiktoken.get_encoding("cl100k_base")
        except Exception:
            return None
    return len(enc.encode(text))


def estimate_tokens(text: str, *, prefer_real: bool = True) -> TokenEstimate:
    """Estimate token count.

    If `prefer_real` and tiktoken is installed, uses the real BPE encoding.
    Otherwise uses a chars/4 approximation adjusted for punctuation density.
    """
    chars = len(text)
    words = len(_WORD_RE.findall(text))
    if prefer_real:
        real = _try_tiktoken(text)
        if real is not None:
            return TokenEstimate(total=real, words=words, chars=chars, method="tiktoken")
    # Approximation: chars/4 with a small uplift for heavy punctuation / code.
    code_markers = len(_CODE_MARKERS.findall(text))
    base = math.ceil(chars / 4)
    bump = min(chars // 10, code_markers // 3)
    total = max(words, base + bump)
    return TokenEstimate(total=total, words=words, chars=chars, method="bpe-approx")


def tokenize(text: str) -> list[str]:
    """Return a word-level token list. Not the same granularity as BPE
    but useful for antipattern detection that works on words."""
    return _WORD_RE.findall(text.lower())
