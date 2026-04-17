"""Tests for Strata market-primitive core + verticals."""

from pep.strata.core import Asset, MoveSignal, score_move


def test_score_normal_move() -> None:
    s = score_move(MoveSignal(asset_id="AAPL", price_change_pct=0.5, relative_volume=1.0))
    assert s.label == "normal"
    assert s.unusual_score < 50


def test_score_unusual_move() -> None:
    s = score_move(MoveSignal(asset_id="AAPL", price_change_pct=8.0, relative_volume=4.0, persistence=0.8))
    assert s.unusual_score > 60
    assert s.label in ("unusual", "extreme", "notable")


def test_score_extreme_move() -> None:
    s = score_move(MoveSignal(asset_id="BTC", price_change_pct=25.0, relative_volume=8.0, persistence=0.9))
    assert s.unusual_score > 75
    assert s.classification != "normal_move"


def test_score_components_bounded() -> None:
    s = score_move(MoveSignal(asset_id="X", price_change_pct=5.0, relative_volume=2.0))
    for v in s.components.values():
        assert 0 <= v <= 100


def test_classification_breakout() -> None:
    s = score_move(MoveSignal(asset_id="X", price_change_pct=12.0, relative_volume=6.0, persistence=0.85))
    assert "breakout" in s.classification.lower() or "momentum" in s.classification.lower()


def test_classification_negative() -> None:
    s = score_move(MoveSignal(asset_id="X", price_change_pct=-10.0, relative_volume=5.0, persistence=0.8))
    assert "breakdown" in s.classification.lower() or "momentum" in s.classification.lower()


def test_explanation_includes_direction() -> None:
    s = score_move(MoveSignal(asset_id="X", price_change_pct=-3.0, relative_volume=1.5))
    assert "down" in s.explanation.lower()


def test_catalyst_in_explanation() -> None:
    s = score_move(MoveSignal(asset_id="X", price_change_pct=5.0, relative_volume=2.0, catalyst="earnings beat"))
    assert "earnings beat" in s.explanation


def test_all_verticals_have_assets() -> None:
    from pep.strata import equities, crypto, fx, commodities, predict, bonds
    for mod in [equities, crypto, fx, commodities, predict, bonds]:
        assert len(mod.ASSETS) >= 10
        for a in mod.ASSETS:
            assert a.id
            assert a.name
