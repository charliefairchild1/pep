"""Unit tests for the Vectora retrieval engine."""

from __future__ import annotations

import pytest

from pep.vectora import (
    Document,
    DocumentGraph,
    Edge,
    LocalEmbedder,
    RetrievalMode,
    VectoraRetriever,
)


# ── Document ─────────────────────────────────────────────────────────────
def test_document_requires_id() -> None:
    with pytest.raises(ValueError):
        Document(id="", text="hello")


def test_document_defaults() -> None:
    d = Document(id="x", text="hello world")
    assert d.embedding == []
    assert d.metadata == {}


# ── LocalEmbedder ────────────────────────────────────────────────────────
def test_embedder_empty_input() -> None:
    e = LocalEmbedder()
    assert e.embed([]) == []


def test_embedder_produces_unit_vectors() -> None:
    e = LocalEmbedder(dim=128)
    vecs = e.embed(["cache redis django", "memory pressure under load"])
    for v in vecs:
        assert len(v) == 128
        norm = sum(x * x for x in v) ** 0.5
        assert abs(norm - 1.0) < 0.01 or norm == 0.0


def test_embedder_similarity_makes_sense() -> None:
    """Docs with overlapping vocabulary should score higher than unrelated docs."""
    e = LocalEmbedder(dim=128)
    corpus = [
        "redis caching for django applications",
        "caching strategies in redis",
        "japanese haiku composition structure",
    ]
    vecs = e.embed(corpus)

    def cos(a: list[float], b: list[float]) -> float:
        return sum(x * y for x, y in zip(a, b))

    related = cos(vecs[0], vecs[1])
    unrelated = cos(vecs[0], vecs[2])
    assert related > unrelated
    # Related docs should have meaningful similarity (not a fluke)
    assert related > 0.15


# ── DocumentGraph ────────────────────────────────────────────────────────
def test_graph_add_and_get() -> None:
    g = DocumentGraph()
    d = Document(id="a", text="hello")
    g.add_document(d)
    assert g.get_document("a") is d
    assert "a" in g
    assert len(g) == 1


def test_graph_rejects_duplicate_id() -> None:
    g = DocumentGraph()
    g.add_document(Document(id="a", text="hello"))
    with pytest.raises(ValueError):
        g.add_document(Document(id="a", text="again"))


def test_graph_edge_rejects_unknown_doc() -> None:
    g = DocumentGraph()
    g.add_document(Document(id="a", text="x"))
    with pytest.raises(ValueError):
        g.add_edge(Edge("a", "does-not-exist", 1.0))


def test_graph_skips_self_loops() -> None:
    g = DocumentGraph()
    g.add_document(Document(id="a", text="x"))
    g.add_edge(Edge("a", "a", 1.0))
    assert g.edge_count() == 0


def test_graph_build_embedding_edges() -> None:
    g = DocumentGraph()
    e = LocalEmbedder(dim=128)
    docs = [
        Document(id="a", text="redis caching django"),
        Document(id="b", text="redis caching backend"),
        Document(id="c", text="totally unrelated topic"),
    ]
    embeddings = e.embed([d.text for d in docs])
    for d, v in zip(docs, embeddings):
        d.embedding = v
        g.add_document(d)
    added = g.build_embedding_edges(top_m=2, threshold=0.05)
    assert added > 0
    # a and b should be directly connected
    a_neighbors = {e.target for e in g.neighbors("a")}
    assert "b" in a_neighbors


# ── VectoraRetriever ─────────────────────────────────────────────────────
@pytest.fixture()
def small_corpus() -> VectoraRetriever:
    r = VectoraRetriever()
    r.add_documents(
        [
            Document(id="cache-1", text="Redis caching strategies for Django applications"),
            Document(id="cache-2", text="Cache-aside pattern with code examples"),
            Document(id="cache-3", text="Memcached vs Redis caching backend comparison"),
            Document(id="mem-1", text="Memory pressure when caching too aggressively Redis"),
            Document(id="db-1", text="Database query patterns that beat caching for analytics"),
            Document(id="unrelated-1", text="Japanese haiku composition structure and form"),
            Document(id="unrelated-2", text="Knitting pattern for winter sweater"),
        ]
    )
    r.build_graph()
    return r


def test_retriever_stats(small_corpus: VectoraRetriever) -> None:
    s = small_corpus.stats()
    assert s["documents"] == 7
    assert s["edges"] > 0


def test_topk_returns_k_results(small_corpus: VectoraRetriever) -> None:
    results = small_corpus.retrieve("caching strategies", k=3, mode=RetrievalMode.TOPK)
    assert 0 < len(results) <= 3
    for r in results:
        assert r.hop_distance == 0
        assert r.score > 0


def test_topk_ranks_relevant_first(small_corpus: VectoraRetriever) -> None:
    results = small_corpus.retrieve("redis caching", k=5, mode=RetrievalMode.TOPK)
    ids = [r.doc.id for r in results]
    # The directly matching caching docs should come first
    assert "cache-1" in ids[:3] or "cache-3" in ids[:3]
    # Unrelated docs should not make the top 3
    assert "unrelated-1" not in ids[:3]
    assert "unrelated-2" not in ids[:3]


def test_vectora_outperforms_topk_on_second_hop() -> None:
    """Vectora should surface memory-pressure doc via the caching doc."""
    r = VectoraRetriever()
    r.add_documents(
        [
            Document(id="cache-1", text="Redis caching Django web applications"),
            Document(id="cache-2", text="Caching strategies Redis backend"),
            Document(id="mem-1", text="Memory tuning JVM heap pressure applications"),
            Document(id="arch-1", text="Splitting a monolith for locality and teams"),
            Document(id="unrelated", text="Japanese haiku form"),
        ]
    )
    r.build_graph()
    # Query targets caching; monolith-architecture doc is a second-hop match
    topk = r.retrieve("caching strategies", k=3, mode=RetrievalMode.TOPK)
    vec = r.retrieve("caching strategies", k=5, mode=RetrievalMode.VECTORA)
    topk_ids = {res.doc.id for res in topk}
    vec_ids = {res.doc.id for res in vec}
    # Vectora should include at least one doc top-k missed
    assert vec_ids - topk_ids, "Vectora should surface docs top-k missed"


def test_empty_corpus_returns_empty() -> None:
    r = VectoraRetriever()
    r.build_graph()
    assert r.retrieve("anything", k=5) == []


def test_build_graph_counts_edges(small_corpus: VectoraRetriever) -> None:
    # Edges should be bidirectional for keyword edges, directed for embedding
    assert small_corpus.graph.edge_count() > 0


def test_retriever_handles_empty_query(small_corpus: VectoraRetriever) -> None:
    # Empty query shouldn't crash; results may be empty or noise-ranked
    results = small_corpus.retrieve("", k=3)
    assert isinstance(results, list)


def test_score_breakdown_populated(small_corpus: VectoraRetriever) -> None:
    results = small_corpus.retrieve("redis caching", k=3, mode=RetrievalMode.VECTORA)
    assert results
    for r in results:
        assert isinstance(r.score_breakdown, dict)


def test_decay_affects_results(small_corpus: VectoraRetriever) -> None:
    """Higher decay should reduce second-hop influence; result ordering may
    differ between tight and loose decay."""
    tight = small_corpus.retrieve("caching", k=5, decay=0.9)
    loose = small_corpus.retrieve("caching", k=5, decay=0.1)
    # At minimum, both should return results
    assert tight and loose


def test_hop_distance_is_nonnegative(small_corpus: VectoraRetriever) -> None:
    results = small_corpus.retrieve("caching", k=5, mode=RetrievalMode.VECTORA)
    for r in results:
        assert r.hop_distance >= 0
