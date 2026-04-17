"""Atria Match — matchmaking that targets rematch rate, not win-probability balance.

Public API:
    from pep.atria.match import Player, AtriaMatcher, rematch_probability

    pool = [Player(id="p1", ...), ...]
    matcher = AtriaMatcher()
    results = matcher.rank(seed=pool[0], candidates=pool[1:], k=5)
    for r in results:
        print(r.candidate.id, r.overall_score, r.rematch_prob, r.dimension_scores)
"""

from .baseline import elo_score, rank_by_elo
from .eval import run_builtin_eval, EvalReport
from .matcher import AtriaMatcher, MatchResult, ObjectiveWeights
from .oracle import rematch_probability
from .player import (
    BehaviorFlag, CommStyle, Player, SessionGoal, make_player,
)
from .scorer import DimensionScores, compatibility

__all__ = [
    "AtriaMatcher",
    "BehaviorFlag",
    "CommStyle",
    "DimensionScores",
    "EvalReport",
    "MatchResult",
    "ObjectiveWeights",
    "Player",
    "SessionGoal",
    "compatibility",
    "elo_score",
    "make_player",
    "rank_by_elo",
    "rematch_probability",
    "run_builtin_eval",
]
