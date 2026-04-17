"""Unit tests for Vectora Context, Watch, and KG engines."""

from __future__ import annotations

import time

import pytest

from pep.vectora import (
    ContextConfig,
    ContextTracker,
    Document,
    EdgeProvenance,
    RetrievalMode,
    VectoraKG,
    VectoraRetriever,
    VectoraWatch,
    WatchConfig,
)


# ── Context ──────────────────────────────────────────────────────────────
@pytest.fixture()
def small_corpus() -> VectoraRetriever:
    r = VectoraRetriever()
    r.add_documents(
        [
            Document(id="git-1", text="git merge strategies for branches"),
            Document(id="git-2", text="resolving merge conflicts"),
            Document(id="git-3", text="merge vs rebase comparison"),
            Document(id="sql-1", text="MERGE INTO SQL statement"),
            Document(id="sql-2", text="merge join performance in Spark"),
            Document(id="sql-3", text="deduplication after a merge"),
            Document(id="biz-1", text="corporate mergers and acquisitions"),
            Document(id="biz-2", text="failed merger retrospective"),
        ]
    )
    r.build_graph()
    return r


def test_context_tracker_records_views(small_corpus: VectoraRetriever) -> None:
    ct = ContextTracker(small_corpus)
    ct.record_view("user-1", "git-1")
    ct.record_view("user-1", "git-2")
    assert ct.session_size("user-1") == 2


def test_context_tracker_rejects_unknown_doc(small_corpus: VectoraRetriever) -> None:
    ct = ContextTracker(small_corpus)
    with pytest.raises(KeyError):
        ct.record_view("u1", "does-not-exist")


def test_context_tracker_clears_session(small_corpus: VectoraRetriever) -> None:
    ct = ContextTracker(small_corpus)
    ct.record_view("u1", "git-1")
    assert ct.clear_session("u1") is True
    assert ct.session_size("u1") == 0
    assert ct.clear_session("u1") is False


def test_context_vector_none_when_empty(small_corpus: VectoraRetriever) -> None:
    ct = ContextTracker(small_corpus)
    assert ct.context_vector("no-such-session") is None


def test_context_vector_is_unit_length(small_corpus: VectoraRetriever) -> None:
    ct = ContextTracker(small_corpus)
    ct.record_view("u1", "git-1")
    ct.record_view("u1", "git-2")
    vec = ct.context_vector("u1")
    assert vec is not None
    norm = sum(x * x for x in vec) ** 0.5
    assert abs(norm - 1.0) < 0.01


def test_contextual_retrieve_shifts_results(small_corpus: VectoraRetriever) -> None:
    """With no context, 'merge' returns mixed results. With a git
    context, git results should rank higher."""
    ct = ContextTracker(small_corpus, ContextConfig(context_weight=0.7))
    # Query with no context
    plain = small_corpus.retrieve("merge", k=8, mode=RetrievalMode.VECTORA)
    # Build git context
    ct.record_view("u1", "git-1")
    ct.record_view("u1", "git-2")
    ct.record_view("u1", "git-3")
    ctx = ct.contextual_retrieve("u1", "merge", k=8)
    # Top result with context should be a git doc
    assert ctx[0].doc.id.startswith("git-"), f"expected git on top, got {ctx[0].doc.id}"


def test_contextual_retrieve_adds_breakdown(small_corpus: VectoraRetriever) -> None:
    ct = ContextTracker(small_corpus)
    ct.record_view("u1", "sql-1")
    results = ct.contextual_retrieve("u1", "merge", k=3)
    assert results
    for r in results:
        assert "context_boost" in r.score_breakdown
        assert "blended_weight" in r.score_breakdown


def test_compare_returns_both(small_corpus: VectoraRetriever) -> None:
    ct = ContextTracker(small_corpus)
    ct.record_view("u1", "biz-1")
    cmp = ct.compare("u1", "merge", k=5)
    assert "plain" in cmp and "contextual" in cmp


def test_recent_views_window(small_corpus: VectoraRetriever) -> None:
    ct = ContextTracker(small_corpus, ContextConfig(max_window=3))
    for doc_id in ["git-1", "git-2", "git-3", "sql-1", "sql-2"]:
        ct.record_view("u1", doc_id)
    assert ct.session_size("u1") == 3  # deque capped
    recent = ct.recent_views("u1", limit=5)
    assert recent[-1].doc_id == "sql-2"


# ── Watch ────────────────────────────────────────────────────────────────
@pytest.fixture()
def watch_corpus() -> VectoraRetriever:
    r = VectoraRetriever()
    r.add_documents(
        [
            Document(id="n1", text="user login from office network regular activity"),
            Document(id="n2", text="file access internal drive standard hours"),
            Document(id="n3", text="password change scheduled rotation"),
            Document(id="n4", text="email sent internal team daily briefing"),
            Document(id="n5", text="meeting scheduled conference room booking"),
            Document(id="n6", text="code commit feature branch pull request"),
            Document(id="n7", text="project status update weekly cadence"),
            Document(id="n8", text="document review approval workflow"),
        ]
    )
    r.build_graph()
    return r


def test_watch_normal_item_low_residual(watch_corpus: VectoraRetriever) -> None:
    w = VectoraWatch(watch_corpus)
    # An item semantically similar to the corpus should score low
    r = w.score_item("user login from office weekly regular", item_id="t1")
    assert r.residual < 75


def test_watch_anomaly_high_residual(watch_corpus: VectoraRetriever) -> None:
    w = VectoraWatch(watch_corpus)
    # Prime with some normal items
    w.score_item("routine login schedule approval")
    w.score_item("weekly briefing email standard")
    # Now an anomaly: totally unrelated content
    r = w.score_item("volcanic eruption hawaiian basalt lava flow", item_id="anom")
    assert r.residual > 40  # real anomaly should clearly exceed normal


def test_watch_labels_match_thresholds(watch_corpus: VectoraRetriever) -> None:
    w = VectoraWatch(watch_corpus, WatchConfig(notable_threshold=30, unusual_threshold=60, extreme_threshold=85))
    r_low = w.score_item("office login internal regular activity")
    r_high = w.score_item("tyrannosaurus rex fossil jurassic paleontology")
    assert r_low.label in ("normal", "notable")
    assert r_high.label in ("unusual", "extreme", "notable")


def test_watch_result_components_bounded(watch_corpus: VectoraRetriever) -> None:
    w = VectoraWatch(watch_corpus)
    r = w.score_item("arbitrary text")
    assert 0 <= r.distance_component <= 100
    assert 0 <= r.neighbor_component <= 100
    assert 0 <= r.novelty_component <= 100
    assert 0 <= r.residual <= 100


def test_watch_adaptive_threshold_falls_back(watch_corpus: VectoraRetriever) -> None:
    w = VectoraWatch(watch_corpus)
    # With too few items, should return the config unusual_threshold
    assert w.adaptive_threshold() == w.config.unusual_threshold


def test_watch_stats_after_items(watch_corpus: VectoraRetriever) -> None:
    w = VectoraWatch(watch_corpus)
    for i in range(25):
        w.score_item(f"item {i} text sample")
    s = w.stats()
    assert s["n"] == 25


# ── KG ───────────────────────────────────────────────────────────────────
@pytest.fixture()
def kg_corpus() -> VectoraRetriever:
    r = VectoraRetriever()
    r.add_documents(
        [
            Document(id="einstein", text="Albert Einstein physicist"),
            Document(id="ulm", text="Ulm city in Germany"),
            Document(id="relativity", text="theory of relativity physics"),
            Document(id="nobel", text="Nobel Prize in Physics award"),
            Document(id="patent-office", text="Swiss patent office Bern"),
            Document(id="physics", text="physics natural science field"),
        ]
    )
    r.build_graph()
    return r


def test_kg_add_triple(kg_corpus: VectoraRetriever) -> None:
    kg = VectoraKG(kg_corpus)
    e = kg.add_triple("einstein", "born_in", "ulm")
    assert e.source == "einstein" and e.target == "ulm"
    assert e.provenance == EdgeProvenance.MANUAL


def test_kg_rejects_unknown_docs(kg_corpus: VectoraRetriever) -> None:
    kg = VectoraKG(kg_corpus)
    with pytest.raises(KeyError):
        kg.add_triple("einstein", "born_in", "does-not-exist")


def test_kg_bulk_add_triples(kg_corpus: VectoraRetriever) -> None:
    kg = VectoraKG(kg_corpus)
    n = kg.add_triples([
        ("einstein", "born_in", "ulm"),
        ("einstein", "developed", "relativity"),
        ("einstein", "won", "nobel"),
        ("einstein", "worked_at", "patent-office"),
    ])
    assert n == 4
    assert kg.stats()["typed_edges"] == 4


def test_kg_typed_neighbors_filters_by_relation(kg_corpus: VectoraRetriever) -> None:
    kg = VectoraKG(kg_corpus)
    kg.add_triple("einstein", "born_in", "ulm")
    kg.add_triple("einstein", "won", "nobel")
    kg.add_triple("einstein", "developed", "relativity")
    only_born = kg.typed_neighbors("einstein", relations=["born_in"])
    assert len(only_born) == 1
    assert only_born[0].target == "ulm"


def test_kg_typed_neighbors_confidence_filter(kg_corpus: VectoraRetriever) -> None:
    kg = VectoraKG(kg_corpus)
    kg.add_triple("einstein", "born_in", "ulm", confidence=0.9)
    kg.add_triple("einstein", "worked_at", "patent-office", confidence=0.3)
    high = kg.typed_neighbors("einstein", min_confidence=0.5)
    assert len(high) == 1
    assert high[0].target == "ulm"


def test_kg_traverse_multi_hop(kg_corpus: VectoraRetriever) -> None:
    kg = VectoraKG(kg_corpus)
    kg.add_triple("einstein", "developed", "relativity")
    kg.add_triple("relativity", "part_of", "physics")
    results = kg.traverse("einstein", max_hops=2)
    reached = {r.doc_id for r in results}
    assert "relativity" in reached
    assert "physics" in reached


def test_kg_edit_edge(kg_corpus: VectoraRetriever) -> None:
    kg = VectoraKG(kg_corpus)
    kg.add_triple("einstein", "born_in", "ulm", confidence=0.8)
    updated = kg.edit_edge("einstein", "born_in", "ulm", new_confidence=0.95)
    assert updated is not None
    assert updated.confidence == 0.95


def test_kg_remove_edge(kg_corpus: VectoraRetriever) -> None:
    kg = VectoraKG(kg_corpus)
    kg.add_triple("einstein", "born_in", "ulm")
    kg.add_triple("einstein", "won", "nobel")
    assert kg.remove_edge("einstein", "born_in", "ulm") is True
    assert kg.stats()["typed_edges"] == 1
    assert kg.remove_edge("einstein", "born_in", "ulm") is False


def test_kg_to_viz_data(kg_corpus: VectoraRetriever) -> None:
    kg = VectoraKG(kg_corpus)
    kg.add_triple("einstein", "born_in", "ulm")
    viz = kg.to_viz_data()
    assert "nodes" in viz and "edges" in viz
    assert len(viz["edges"]) == 1
    assert viz["edges"][0]["relation"] == "born_in"


def test_kg_stats_by_relation(kg_corpus: VectoraRetriever) -> None:
    kg = VectoraKG(kg_corpus)
    kg.add_triple("einstein", "born_in", "ulm")
    kg.add_triple("einstein", "developed", "relativity")
    kg.add_triple("einstein", "worked_at", "patent-office")
    s = kg.stats()
    assert s["typed_edges"] == 3
    assert s["unique_relations"] == 3
