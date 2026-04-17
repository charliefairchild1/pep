"""Unit tests for the Atria Match engine."""

from __future__ import annotations

import pytest

from pep.atria.match import (
    AtriaMatcher,
    BehaviorFlag,
    CommStyle,
    ObjectiveWeights,
    Player,
    SessionGoal,
    compatibility,
    elo_score,
    make_player,
    rank_by_elo,
    rematch_probability,
    run_builtin_eval,
)
from pep.atria.match.oracle import overall_score


# ── Player ───────────────────────────────────────────────────────────────
def test_player_requires_id() -> None:
    with pytest.raises(ValueError):
        Player(id="")


def test_player_validates_bounds() -> None:
    with pytest.raises(ValueError):
        Player(id="p", tempo=1.5)
    with pytest.raises(ValueError):
        Player(id="p", tilt_tolerance=-0.1)
    with pytest.raises(ValueError):
        Player(id="p", uncertainty=-1)


def test_behavior_risk_scales() -> None:
    clean = Player(id="p", behavior_flags=[])
    flagged = Player(id="p2", behavior_flags=[BehaviorFlag.TOXIC])
    heavy = Player(id="p3", behavior_flags=[BehaviorFlag.TOXIC, BehaviorFlag.THROWING, BehaviorFlag.AFK])
    assert clean.behavior_risk == 0.0
    assert 0 < flagged.behavior_risk < heavy.behavior_risk
    assert heavy.behavior_risk <= 1.0


def test_new_player_flag() -> None:
    veteran = Player(id="v", uncertainty=80)
    newbie = Player(id="n", uncertainty=300)
    assert not veteran.is_new_player
    assert newbie.is_new_player


# ── Scoring dimensions ──────────────────────────────────────────────────
def test_skill_score_identical_ratings() -> None:
    a = make_player("a", rating=1500)
    b = make_player("b", rating=1500)
    assert compatibility(a, b).skill == 1.0


def test_skill_score_wide_delta() -> None:
    a = make_player("a", rating=1500)
    b = make_player("b", rating=3000)
    assert compatibility(a, b).skill < 0.1


def test_skill_score_uncertainty_widens_pool() -> None:
    """High uncertainty (new player) should get a more forgiving score."""
    vet = Player(id="v", rating=1500, uncertainty=80)
    new_delta = Player(id="n", rating=1800, uncertainty=400)
    reg_delta = Player(id="r", rating=1800, uncertainty=80)
    new_score = compatibility(vet, new_delta).skill
    reg_score = compatibility(vet, reg_delta).skill
    # Wider uncertainty → more forgiving → higher skill score for same delta
    assert new_score > reg_score


def test_tempo_score_close_vs_far() -> None:
    a = make_player("a", tempo=0.3)
    close = make_player("b", tempo=0.35)
    far = make_player("c", tempo=0.9)
    assert compatibility(a, close).tempo > compatibility(a, far).tempo


def test_communication_vocal_vocal_best() -> None:
    a = Player(id="a", comm_style=CommStyle.VOCAL)
    b = Player(id="b", comm_style=CommStyle.VOCAL)
    muted = Player(id="m", comm_style=CommStyle.MUTED)
    assert compatibility(a, b).communication > compatibility(a, muted).communication


def test_goal_alignment_casual_vs_tryhard() -> None:
    casual_a = Player(id="a", session_goal=SessionGoal.CASUAL)
    casual_b = Player(id="b", session_goal=SessionGoal.CASUAL)
    tryhard = Player(id="c", session_goal=SessionGoal.COMPETITIVE)
    assert compatibility(casual_a, casual_b).goal > compatibility(casual_a, tryhard).goal


def test_behavior_score_flagged_vs_clean() -> None:
    toxic = Player(id="t", behavior_flags=[BehaviorFlag.TOXIC, BehaviorFlag.THROWING])
    clean = Player(id="c")
    other_clean = Player(id="d")
    # Toxic + clean = bad; clean + clean = perfect
    assert compatibility(toxic, clean).behavior < compatibility(clean, other_clean).behavior


def test_behavior_score_two_flagged_contained() -> None:
    t1 = Player(id="t1", behavior_flags=[BehaviorFlag.TOXIC])
    t2 = Player(id="t2", behavior_flags=[BehaviorFlag.TOXIC])
    clean = Player(id="c")
    # Two toxic players matched together shouldn't drag as hard
    # as one toxic + one clean (different dynamic)
    score_tt = compatibility(t1, t2).behavior
    score_tc = compatibility(t1, clean).behavior
    assert score_tt > score_tc


def test_role_score_complementary_vs_conflict() -> None:
    tank = Player(id="t", role_pref="tank")
    support = Player(id="s", role_pref="support")
    other_tank = Player(id="t2", role_pref="tank")
    assert compatibility(tank, support).role > compatibility(tank, other_tank).role


# ── Oracle ──────────────────────────────────────────────────────────────
def test_rematch_probability_bounded() -> None:
    a = make_player("a")
    b = make_player("b")
    p = rematch_probability(compatibility(a, b))
    assert 0 <= p <= 1


def test_rematch_probability_high_for_great_match() -> None:
    a = Player(id="a", rating=1500, tempo=0.5, tilt_tolerance=0.8,
               comm_style=CommStyle.VOCAL, session_goal=SessionGoal.CASUAL)
    b = Player(id="b", rating=1510, tempo=0.52, tilt_tolerance=0.75,
               comm_style=CommStyle.VOCAL, session_goal=SessionGoal.CASUAL,
               role_pref="tank")
    a.role_pref = "support"
    assert rematch_probability(compatibility(a, b)) > 0.8


def test_rematch_probability_low_for_bad_match() -> None:
    a = Player(id="a", rating=1500, tempo=0.1, tilt_tolerance=0.2,
               comm_style=CommStyle.VOCAL, session_goal=SessionGoal.COMPETITIVE)
    b = Player(id="b", rating=1900, tempo=0.9, tilt_tolerance=0.1,
               comm_style=CommStyle.MUTED, session_goal=SessionGoal.CASUAL,
               behavior_flags=[BehaviorFlag.TOXIC, BehaviorFlag.THROWING])
    assert rematch_probability(compatibility(a, b)) < 0.3


# ── AtriaMatcher ────────────────────────────────────────────────────────
@pytest.fixture()
def simple_pool() -> list[Player]:
    return [
        Player(id="seed", rating=1500, tempo=0.5, tilt_tolerance=0.7,
               comm_style=CommStyle.VOCAL, session_goal=SessionGoal.CASUAL),
        Player(id="great", rating=1520, tempo=0.52, tilt_tolerance=0.7,
               comm_style=CommStyle.VOCAL, session_goal=SessionGoal.CASUAL),
        Player(id="good", rating=1600, tempo=0.55, tilt_tolerance=0.6,
               comm_style=CommStyle.TEXT, session_goal=SessionGoal.CASUAL),
        Player(id="meh", rating=1510, tempo=0.9, tilt_tolerance=0.2,
               comm_style=CommStyle.MUTED, session_goal=SessionGoal.COMPETITIVE),
        Player(id="bad", rating=1500, tempo=0.1, tilt_tolerance=0.1,
               comm_style=CommStyle.MUTED, session_goal=SessionGoal.COMPETITIVE,
               behavior_flags=[BehaviorFlag.TOXIC, BehaviorFlag.THROWING]),
    ]


def test_matcher_ranks_best_first(simple_pool: list[Player]) -> None:
    seed = simple_pool[0]
    candidates = simple_pool[1:]
    matcher = AtriaMatcher()
    results = matcher.rank(seed, candidates, k=4)
    assert results[0].candidate.id == "great"
    # "bad" should be ranked last (or filtered)
    last_ids = [r.candidate.id for r in results[-2:]]
    assert "bad" in last_ids or "meh" in last_ids


def test_matcher_skips_blocked() -> None:
    seed = Player(id="seed", blocked=["blocked"])
    candidates = [
        Player(id="blocked", rating=1500),
        Player(id="ok", rating=1500),
    ]
    results = AtriaMatcher().rank(seed, candidates, k=5)
    ids = [r.candidate.id for r in results]
    assert "blocked" not in ids
    assert "ok" in ids


def test_matcher_skips_recent_cooldown() -> None:
    seed = Player(id="seed", recent_matches=["recent"])
    candidates = [
        Player(id="recent", rating=1500),
        Player(id="ok", rating=1500),
    ]
    results = AtriaMatcher(cooldown_recent=True).rank(seed, candidates, k=5)
    ids = [r.candidate.id for r in results]
    assert "recent" not in ids


def test_matcher_result_has_breakdown(simple_pool: list[Player]) -> None:
    results = AtriaMatcher().rank(simple_pool[0], simple_pool[1:], k=3)
    r = results[0]
    assert 0 <= r.overall_score <= 1
    assert 0 <= r.rematch_prob <= 1
    assert r.strongest_dimension
    assert r.weakest_dimension
    assert r.elo_score >= 0


def test_objective_preset_ranked_prioritizes_skill() -> None:
    w = ObjectiveWeights.preset("ranked")
    assert w.skill > w.communication


def test_objective_preset_casual_prioritizes_social() -> None:
    w = ObjectiveWeights.preset("casual")
    assert w.communication > w.skill
    assert w.goal > w.skill


def test_compare_vs_elo(simple_pool: list[Player]) -> None:
    cmp = AtriaMatcher().compare_vs_elo(simple_pool[0], simple_pool[1:], k=3)
    assert "atria" in cmp and "elo" in cmp


# ── Elo baseline ────────────────────────────────────────────────────────
def test_elo_identical_ratings() -> None:
    a = make_player("a", rating=1500)
    b = make_player("b", rating=1500)
    assert elo_score(a, b) == 1.0


def test_elo_rank_order() -> None:
    seed = Player(id="s", rating=1500)
    pool = [Player(id=f"p{i}", rating=r) for i, r in enumerate([1505, 1700, 1502, 1800])]
    picks = rank_by_elo(seed, pool, k=2)
    # Closest ratings should win
    assert "p2" == picks[0].id and "p0" == picks[1].id


# ── Eval harness ────────────────────────────────────────────────────────
def test_builtin_eval_atria_beats_elo() -> None:
    result = run_builtin_eval(n_pairs=300)
    assert result["n_pairs"] == 300
    # Atria should outperform Elo on AUC — the whole point of the system
    assert result["atria_advantage"]["auc"] > 0.1
    assert result["atria"]["auc"] > result["elo"]["auc"]
