"""Vectora Contradiction Surfacing — detect live docs that disagree.

Classic RAG failure mode: a query returns top-k similar documents, two of
which assert mutually incompatible things. The LLM picks one at random
(or hallucinates a reconciliation) and the user gets a wrong answer
without any flag. Legal, compliance, and enterprise-knowledge deployments
are most exposed.

This module applies PEP's residual-scorer primitive to *pairs of
retrieved documents*: if doc A and doc B both claim to answer the same
query but their assertions disagree, the gap between them is a residual
and should be surfaced.

Approach (LLM-free):

    1. Each doc carries a set of extracted assertions — typed claim
       patterns ("numerical value for X is N", "X is permitted",
       "X requires Y", "X is prohibited").

    2. `detect(docs)` scans pairs of docs, finds pairs that share a
       topic (overlapping keywords + high embedding proxy) and whose
       assertions conflict on direction or value.

    3. Returns scored contradictions with confidence + suggested
       resolution policy (newer wins, authority wins, human review).

The detector is heuristic. For real deployments swap in an LLM
adjudicator once you have one wired; the structure of contradictions
as "residuals on retrieval pairs" is stable regardless.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


# ─── Document model (lightweight, UI-shaped) ────────────────────────────

@dataclass
class PolicyDoc:
    id: str
    title: str
    body: str
    team: str = ""
    version_date: str = ""        # YYYY-MM-DD
    authority: float = 0.5        # 0..1 — formal policy weight
    scope: list[str] = field(default_factory=list)


# ─── Assertion extraction (regex heuristics) ────────────────────────────

# Returns list of (type, topic, polarity, value) tuples
_NUM_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*(%|percent|days?|weeks?|months?|years?|hours?)",
    re.IGNORECASE,
)
_PROHIB_PATTERN = re.compile(
    r"\b(?:not|no|prohibited|forbidden|never|cannot|may not|must not|don'?t)\b",
    re.IGNORECASE,
)
_PERMIT_PATTERN = re.compile(
    r"\b(?:allowed|permitted|may|can|eligible|includes?|will|shall)\b",
    re.IGNORECASE,
)
_REQUIRE_PATTERN = re.compile(
    r"\b(?:required|must|mandatory|need(?:s|ed)? to|obligated)\b",
    re.IGNORECASE,
)
_EXEMPT_PATTERN = re.compile(
    r"\b(?:exempt|excluded|waived|excepted|except for|skip(?:s|ped)?)\b",
    re.IGNORECASE,
)

_STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "to", "of", "and", "or", "but", "in", "on", "at", "for", "with",
    "from", "by", "this", "that", "these", "those", "it", "its", "as",
    "all", "any", "some", "every", "each", "other", "have", "has", "had",
    "will", "shall", "may", "can", "not", "no", "do", "does", "did",
}


def _tokens(text: str) -> list[str]:
    return [t.lower() for t in re.findall(r"[a-zA-Z][a-zA-Z\-]+", text)
            if len(t) > 3 and t.lower() not in _STOPWORDS]


def _topic_overlap(a: PolicyDoc, b: PolicyDoc) -> tuple[float, list[str]]:
    """Jaccard-style topic overlap + shared keywords."""
    ta, tb = set(_tokens(a.body + " " + a.title)), set(_tokens(b.body + " " + b.title))
    shared = ta & tb
    if not ta or not tb:
        return 0.0, []
    overlap = len(shared) / len(ta | tb)
    # Prioritize salient shared tokens (longer, rarer; we approximate rarity
    # by length as a cheap proxy without a corpus-wide IDF pass)
    ranked = sorted(shared, key=lambda w: -len(w))
    return overlap, ranked[:6]


def extract_values(doc: PolicyDoc) -> list[tuple[float, str]]:
    """Extract numerical value + unit pairs."""
    out = []
    for m in _NUM_PATTERN.finditer(doc.body):
        val = float(m.group(1))
        unit = m.group(2).lower().rstrip("s")       # days/day, weeks/week
        out.append((val, unit))
    return out


def polarity(doc: PolicyDoc) -> int:
    """Crude direction classifier: +1 permits/requires, -1 prohibits/exempts, 0 neutral."""
    body = doc.body.lower()
    pos = len(_PERMIT_PATTERN.findall(body)) + len(_REQUIRE_PATTERN.findall(body))
    neg = len(_PROHIB_PATTERN.findall(body)) + len(_EXEMPT_PATTERN.findall(body))
    if pos > neg + 1:
        return 1
    if neg > pos + 1:
        return -1
    return 0


# ─── Contradiction detection ───────────────────────────────────────────

@dataclass
class Contradiction:
    doc_a: PolicyDoc
    doc_b: PolicyDoc
    kind: str                         # "numerical" | "polarity" | "exemption"
    topic_overlap: float
    shared_keywords: list[str]
    confidence: float                 # 0..1
    details: str
    resolution_hint: str


def _numerical_conflict(a: PolicyDoc, b: PolicyDoc) -> tuple[bool, str]:
    va, vb = extract_values(a), extract_values(b)
    if not va or not vb:
        return False, ""
    # Look for same-unit pairs with different values
    for (va_val, va_unit) in va:
        for (vb_val, vb_unit) in vb:
            if va_unit == vb_unit and abs(va_val - vb_val) > 0.01:
                return True, f"value differs: {va_val}{va_unit} vs {vb_val}{vb_unit}"
    return False, ""


def _resolution_hint(a: PolicyDoc, b: PolicyDoc) -> str:
    if a.version_date and b.version_date:
        if a.version_date > b.version_date:
            return f"newer wins: '{a.title}' is more recent ({a.version_date} > {b.version_date})"
        if b.version_date > a.version_date:
            return f"newer wins: '{b.title}' is more recent ({b.version_date} > {a.version_date})"
    if abs(a.authority - b.authority) > 0.2:
        winner = a if a.authority > b.authority else b
        return f"authority wins: '{winner.title}' has higher formal weight"
    return "flag for human review: no clear precedence between the two"


def detect(docs: list[PolicyDoc], *, overlap_threshold: float = 0.08) -> list[Contradiction]:
    """Find contradiction candidates across all doc pairs."""
    out: list[Contradiction] = []
    for i in range(len(docs)):
        for j in range(i + 1, len(docs)):
            a, b = docs[i], docs[j]
            overlap, shared = _topic_overlap(a, b)
            if overlap < overlap_threshold:
                continue
            # Numerical conflict first (strongest signal)
            is_num, num_detail = _numerical_conflict(a, b)
            if is_num:
                out.append(Contradiction(
                    doc_a=a, doc_b=b, kind="numerical",
                    topic_overlap=round(overlap, 3),
                    shared_keywords=shared,
                    confidence=round(min(1.0, 0.55 + overlap * 2), 3),
                    details=num_detail,
                    resolution_hint=_resolution_hint(a, b),
                ))
                continue
            # Polarity conflict: same topic, opposite direction
            pa, pb = polarity(a), polarity(b)
            if pa != 0 and pb != 0 and pa != pb:
                out.append(Contradiction(
                    doc_a=a, doc_b=b, kind="polarity",
                    topic_overlap=round(overlap, 3),
                    shared_keywords=shared,
                    confidence=round(min(1.0, 0.4 + overlap * 3), 3),
                    details=f"opposite direction: A={'allows/requires' if pa > 0 else 'prohibits'}, B={'allows/requires' if pb > 0 else 'prohibits'}",
                    resolution_hint=_resolution_hint(a, b),
                ))
                continue
            # Exemption conflict: one requires, other exempts
            ea = bool(_EXEMPT_PATTERN.search(a.body))
            eb = bool(_EXEMPT_PATTERN.search(b.body))
            ra = bool(_REQUIRE_PATTERN.search(a.body))
            rb = bool(_REQUIRE_PATTERN.search(b.body))
            if (ea and rb) or (eb and ra):
                out.append(Contradiction(
                    doc_a=a, doc_b=b, kind="exemption",
                    topic_overlap=round(overlap, 3),
                    shared_keywords=shared,
                    confidence=round(min(1.0, 0.5 + overlap * 2), 3),
                    details="one doc states a requirement, the other carves an exemption",
                    resolution_hint=_resolution_hint(a, b),
                ))
    out.sort(key=lambda c: -c.confidence)
    return out


# ─── Curated demo corpus ───────────────────────────────────────────────

SAMPLE_CORPUS = [
    PolicyDoc(
        id="p-001", title="Remote Work Policy v2.3",
        body="All employees are permitted to work remotely up to 3 days per week. Teams may set tighter limits by mutual agreement.",
        team="hr", version_date="2025-11-12", authority=0.85,
    ),
    PolicyDoc(
        id="p-002", title="In-Office Expectations (Ops)",
        body="Ops staff must be in-office 4 days per week. This applies to the entire Ops organization.",
        team="ops", version_date="2024-06-01", authority=0.65,
    ),
    PolicyDoc(
        id="p-003", title="Vacation Policy",
        body="Employees may take up to 20 vacation days per year. Sabbaticals are permitted after 5 years of service.",
        team="hr", version_date="2025-01-15", authority=0.9,
    ),
    PolicyDoc(
        id="p-004", title="Leave Handbook (Finance)",
        body="Finance employees may take 15 vacation days per year. Sabbaticals are not offered at this time.",
        team="finance", version_date="2023-04-22", authority=0.55,
    ),
    PolicyDoc(
        id="p-005", title="Production Deploy Review",
        body="All production deploys must undergo security review before release. No exceptions for any team.",
        team="security", version_date="2025-08-30", authority=0.95,
    ),
    PolicyDoc(
        id="p-006", title="Hotfix Deployment Guide",
        body="Hotfix deploys are exempt from the standard security review gate to allow rapid remediation of critical issues.",
        team="platform", version_date="2024-03-18", authority=0.6,
    ),
    PolicyDoc(
        id="p-007", title="On-Call Rotation Policy",
        body="All engineers are required to participate in the on-call rotation. Rotation duration is 1 week.",
        team="platform", version_date="2025-09-01", authority=0.8,
    ),
    PolicyDoc(
        id="p-008", title="Platform Team On-Call",
        body="The Platform team is exempt from the standard on-call rotation and runs its own 2-week rotation.",
        team="platform", version_date="2025-09-02", authority=0.8,
    ),
    PolicyDoc(
        id="p-009", title="Fiscal Year (Legacy)",
        body="The fiscal year begins on April 1 and ends March 31 of the following year.",
        team="finance", version_date="2022-02-10", authority=0.5,
    ),
    PolicyDoc(
        id="p-010", title="Fiscal Year Change (Post-Reorg)",
        body="Effective January 2025, the fiscal year begins on January 1 and aligns with the calendar year.",
        team="finance", version_date="2024-11-01", authority=0.9,
    ),
    PolicyDoc(
        id="p-011", title="Code Review Requirements",
        body="All merges to main require at least 2 approvals from code owners. Direct commits are prohibited.",
        team="eng", version_date="2025-10-05", authority=0.85,
    ),
    PolicyDoc(
        id="p-012", title="Emergency Merge Procedure",
        body="During declared incidents, single-approval merges are permitted to accelerate remediation.",
        team="eng", version_date="2024-07-20", authority=0.6,
    ),
]
