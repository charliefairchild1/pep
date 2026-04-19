"""Organizational Opacity Management — haze primitive at institutional scale.

Most enterprises have a long tail of documents, wikis, processes, and
decisions nobody reads anymore but nobody can confidently delete. This
module applies PEP's haze primitive (opacity + encoding time + half-life +
reinforcement) to that corpus and produces the kinds of signals a CKO /
platform ops / KM lead actually needs:

    - "What percent of the corpus is below reuse threshold?"
    - "What's load-bearing-but-stale?" (docs linked from other live content
       that haven't been touched in forever)
    - "Which docs should we archive next quarter?"
    - "What's our knowledge decay velocity?" (D_rec transition rate)

Everything is heuristic + deterministic. No API keys, no LLM calls.
A synthetic corpus generator is included so the UI can run without a
real customer corpus; real deployments swap in a corpus adapter.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Iterable


# ─── Node model ─────────────────────────────────────────────────────────

@dataclass
class OrgDoc:
    """An institutional document with opacity + access history.

    Parallel to `pep.vectora.Document` but carrying the org-specific
    attributes that the recommendations surface on: owning team, criticality
    marker, incoming reference count (how load-bearing is this doc).
    """
    id: str
    title: str
    team: str
    opacity: float = 1.0
    opacity_floor: float = 0.02
    encoded_days_ago: float = 0.0          # "elapsed since last reinforcement"
    half_life_days: float = 90.0           # org docs decay slower than episodic
    incoming_refs: int = 0                 # how many live docs link to this
    criticality: float = 0.5               # 0..1 flagged importance
    last_accessor: str = ""
    # Optional: a marker that the doc touches a regulated area.
    regulated: bool = False

    def effective_opacity(self, t_elapsed: float = 0.0) -> float:
        """Opacity after `t_elapsed` days beyond its current encoded-days-ago."""
        total = max(0.0, self.encoded_days_ago + t_elapsed)
        decayed = self.opacity * (0.5 ** (total / self.half_life_days))
        return max(self.opacity_floor, decayed)

    def reinforce(self, amount: float = 0.4) -> None:
        current = self.effective_opacity()
        self.opacity = min(1.0, current + amount)
        self.encoded_days_ago = 0.0

    def is_reusable(self, threshold: float = 0.12, t_elapsed: float = 0.0) -> bool:
        return self.effective_opacity(t_elapsed) < threshold

    def load_bearing(self) -> bool:
        """Heuristic: doc is load-bearing if other live docs reference it
        and/or it is flagged critical or regulated."""
        return self.incoming_refs >= 3 or self.criticality >= 0.7 or self.regulated


# ─── Synthetic corpus for UI + eval ─────────────────────────────────────

_TEAMS = ["platform", "eng", "product", "design", "ops", "hr", "legal", "finance"]
_TITLE_STEMS = [
    "Runbook: ", "RFC #", "Spec: ", "Memo — ", "Q-plan ", "Playbook: ",
    "Retro — ", "Design doc: ", "Proposal: ", "Policy: ", "Guide: ",
    "Strategy memo — ", "Onboarding: ", "Architecture — ", "Review: ",
]
_TOPICS = [
    "service migration", "deploy safety", "data retention",
    "compensation bands", "vendor onboarding", "incident response",
    "feature flags", "privacy review", "growth plan",
    "metrics dashboard", "hiring loop", "security audit",
    "design system", "customer interview", "tech debt",
    "content moderation", "api versioning", "capacity planning",
]


def simulate_corpus(n: int = 140, seed: int = 42) -> list[OrgDoc]:
    """Generate a representative org corpus: a long-tail of age distribution,
    a handful of load-bearing docs, most of the middle quietly decaying."""
    rng = random.Random(seed)
    docs: list[OrgDoc] = []
    for i in range(n):
        team = rng.choice(_TEAMS)
        title = f"{rng.choice(_TITLE_STEMS)}{rng.choice(_TOPICS)} ({team})"
        # Age distribution: heavy tail (most docs are old)
        age = rng.choice([
            rng.expovariate(1 / 40.0),      # short-lived (median ~30d)
            rng.expovariate(1 / 180.0),     # typical (median ~150d)
            rng.expovariate(1 / 720.0),     # long tail (median ~2y)
        ])
        age = min(age, 4 * 365.0)
        base = 0.6 + rng.random() * 0.4
        refs = 0
        # ~12% of docs are load-bearing: they accumulate refs
        if rng.random() < 0.12:
            refs = rng.randint(3, 15)
        criticality = 0.2 + rng.random() * 0.7
        regulated = rng.random() < 0.08
        docs.append(OrgDoc(
            id=f"doc-{i:04d}",
            title=title,
            team=team,
            opacity=base,
            encoded_days_ago=age,
            half_life_days=rng.choice([60.0, 90.0, 120.0, 180.0]),
            incoming_refs=refs,
            criticality=criticality,
            regulated=regulated,
        ))
    return docs


# ─── Signals the UI + a human reader actually care about ────────────────

@dataclass
class OpacityReport:
    total: int
    reusable: int                          # below threshold, safe to archive
    load_bearing_stale: list[OrgDoc]       # below threshold AND load-bearing
    archive_candidates: list[OrgDoc]       # below threshold AND not load-bearing
    by_team: dict[str, dict[str, int]]     # team → {total, reusable}
    histogram: list[int]                   # opacity histogram in 10 buckets
    decay_velocity: float                  # approx docs/week crossing threshold

    def reusable_pct(self) -> float:
        return 0.0 if self.total == 0 else 100.0 * self.reusable / self.total


def build_report(
    docs: Iterable[OrgDoc],
    *,
    t_elapsed: float = 0.0,
    threshold: float = 0.12,
    velocity_window_days: float = 14.0,
) -> OpacityReport:
    """Single-pass scan producing all the signals the UI surfaces."""
    docs = list(docs)
    histogram = [0] * 10
    reusable = 0
    load_bearing_stale: list[OrgDoc] = []
    archive_candidates: list[OrgDoc] = []
    by_team: dict[str, dict[str, int]] = {}

    for d in docs:
        op = d.effective_opacity(t_elapsed)
        bucket = min(9, int(op * 10))
        histogram[bucket] += 1
        team_entry = by_team.setdefault(d.team, {"total": 0, "reusable": 0})
        team_entry["total"] += 1
        if op < threshold:
            reusable += 1
            team_entry["reusable"] += 1
            if d.load_bearing():
                load_bearing_stale.append(d)
            else:
                archive_candidates.append(d)

    # Decay velocity: how many currently-above-threshold docs will cross it
    # in the next `velocity_window_days` days? Count only docs whose effective
    # opacity at t_elapsed is in (threshold, 2 * threshold) — these are the
    # ones about to cross under normal decay.
    will_cross = sum(
        1
        for d in docs
        if threshold <= d.effective_opacity(t_elapsed) < 2 * threshold
        and d.effective_opacity(t_elapsed + velocity_window_days) < threshold
    )
    decay_velocity = will_cross / max(1.0, velocity_window_days) * 7.0  # per week

    # Rank archive candidates by lowest opacity (least useful first)
    archive_candidates.sort(key=lambda d: d.effective_opacity(t_elapsed))
    load_bearing_stale.sort(key=lambda d: (-d.incoming_refs, d.effective_opacity(t_elapsed)))

    return OpacityReport(
        total=len(docs),
        reusable=reusable,
        load_bearing_stale=load_bearing_stale,
        archive_candidates=archive_candidates,
        by_team=by_team,
        histogram=histogram,
        decay_velocity=decay_velocity,
    )


def recommend_archive(
    docs: Iterable[OrgDoc],
    *,
    t_elapsed: float = 0.0,
    threshold: float = 0.12,
    limit: int = 20,
) -> list[OrgDoc]:
    """Ranked list of documents to archive: lowest opacity, not load-bearing,
    not regulated. Safe to delete / move to cold storage."""
    out: list[OrgDoc] = []
    for d in docs:
        if d.effective_opacity(t_elapsed) < threshold and not d.load_bearing():
            out.append(d)
    out.sort(key=lambda d: d.effective_opacity(t_elapsed))
    return out[:limit]
