"""AtriaMatcher — the real engine.

Given a seed player and a candidate pool, returns the top-k matches
ranked by multi-objective compatibility. Each result carries its
dimension-level score breakdown, an overall score, and a predicted
rematch probability. Configurable objective weights let studios tune
for competitive modes (skill-heavy) vs casual modes (social-heavy).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .oracle import overall_score, rematch_probability
from .player import Player
from .scorer import DimensionScores, compatibility


@dataclass
class ObjectiveWeights:
    """Configurable per-studio / per-mode weighting."""

    skill: float = 0.18
    tempo: float = 0.15
    communication: float = 0.12
    role: float = 0.08
    tilt: float = 0.12
    goal: float = 0.15
    behavior: float = 0.20

    def as_dict(self) -> dict[str, float]:
        return {
            "skill": self.skill, "tempo": self.tempo,
            "communication": self.communication, "role": self.role,
            "tilt": self.tilt, "goal": self.goal,
            "behavior": self.behavior,
        }

    @classmethod
    def preset(cls, name: str) -> "ObjectiveWeights":
        """Named presets for common game modes."""
        presets = {
            "ranked":  cls(skill=0.35, tempo=0.15, communication=0.12, role=0.10, tilt=0.08, goal=0.08, behavior=0.12),
            "casual":  cls(skill=0.08, tempo=0.12, communication=0.18, role=0.05, tilt=0.15, goal=0.22, behavior=0.20),
            "learning": cls(skill=0.05, tempo=0.10, communication=0.20, role=0.05, tilt=0.25, goal=0.15, behavior=0.20),
            "esports": cls(skill=0.40, tempo=0.20, communication=0.15, role=0.15, tilt=0.05, goal=0.02, behavior=0.03),
        }
        if name not in presets:
            raise KeyError(f"unknown preset: {name!r} (available: {list(presets)})")
        return presets[name]


@dataclass
class MatchResult:
    """One ranked candidate with full explanation."""

    candidate: Player
    dimension_scores: DimensionScores
    overall_score: float
    rematch_prob: float
    weakest_dimension: str
    strongest_dimension: str
    # Counterfactual — what a pure-Elo matcher would have scored
    elo_score: float = 0.0
    # Any hard-exclusion reason the candidate had (empty = passed all filters)
    rejection_reason: str = ""


@dataclass
class AtriaMatcher:
    """The matchmaker. Keeps the objective weights and team-mode config.

    Usage:
        matcher = AtriaMatcher(weights=ObjectiveWeights.preset("ranked"))
        results = matcher.rank(seed=p0, candidates=pool, k=5)
    """

    weights: ObjectiveWeights = field(default_factory=ObjectiveWeights)
    team_mode: bool = True
    cooldown_recent: bool = True  # skip candidates in seed's recent_matches
    allow_blocked: bool = False   # True = include blocked candidates (for debug)

    def rank(
        self,
        seed: Player,
        candidates: list[Player],
        k: int = 10,
    ) -> list[MatchResult]:
        """Rank candidates by overall compatibility with the seed."""
        w = self.weights.as_dict()
        results: list[MatchResult] = []
        for c in candidates:
            if c.id == seed.id:
                continue
            rejection = self._rejection_reason(seed, c)
            if rejection:
                continue
            scores = compatibility(seed, c, team_mode=self.team_mode)
            overall = overall_score(scores, w)
            rematch = rematch_probability(scores, w)
            # Identify strongest + weakest dimensions for explainability
            dim_values = {
                "skill": scores.skill, "tempo": scores.tempo,
                "communication": scores.communication, "role": scores.role,
                "tilt": scores.tilt, "goal": scores.goal,
                "behavior": scores.behavior,
            }
            strongest = max(dim_values, key=dim_values.get)
            weakest = min(dim_values, key=dim_values.get)
            # Elo counterfactual
            from .baseline import elo_score as _elo
            elo = _elo(seed, c)
            results.append(MatchResult(
                candidate=c, dimension_scores=scores,
                overall_score=overall, rematch_prob=rematch,
                weakest_dimension=weakest, strongest_dimension=strongest,
                elo_score=round(elo, 4),
            ))
        results.sort(key=lambda r: r.overall_score, reverse=True)
        return results[:k]

    def _rejection_reason(self, seed: Player, c: Player) -> str:
        """Hard filters: blocked, recent cooldown, etc."""
        if not self.allow_blocked and c.id in seed.blocked:
            return "blocked"
        if not self.allow_blocked and seed.id in c.blocked:
            return "blocked by candidate"
        if self.cooldown_recent and c.id in seed.recent_matches:
            return "recent match cooldown"
        return ""

    def compare_vs_elo(
        self, seed: Player, candidates: list[Player], k: int = 10,
    ) -> dict[str, list[MatchResult] | list[Player]]:
        """Return both Atria's ranking and the Elo-baseline's ranking
        for the same seed + pool. Playground uses this to show the delta."""
        from .baseline import rank_by_elo
        atria_results = self.rank(seed, candidates, k=k)
        elo_picks = rank_by_elo(seed, candidates, k=k)
        return {"atria": atria_results, "elo": elo_picks}
