"""Evaluation harness — measure Vectora vs top-k on labeled datasets.

Produces standard retrieval metrics (recall@k, precision@k, MRR, NDCG@k)
for both modes and reports the delta. Includes a built-in labeled
dataset so the measurement is reproducible without any external data.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Iterable

from .document import Document
from .retrieval import RetrievalMode, VectoraRetriever


@dataclass
class LabeledQuery:
    """A query with known-relevant document IDs (ground truth)."""

    query: str
    relevant: set[str]
    description: str = ""


@dataclass
class QueryMetrics:
    """Retrieval metrics for one (query, mode) combination."""

    query: str
    mode: str
    hits: list[str]
    relevant: set[str]
    recall_at_k: float
    precision_at_k: float
    reciprocal_rank: float
    ndcg_at_k: float
    k: int


@dataclass
class EvalReport:
    """Aggregate results across an eval run."""

    mode: str
    k: int
    per_query: list[QueryMetrics]
    mean_recall: float
    mean_precision: float
    mean_mrr: float
    mean_ndcg: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "k": self.k,
            "n_queries": len(self.per_query),
            "mean_recall": round(self.mean_recall, 4),
            "mean_precision": round(self.mean_precision, 4),
            "mean_mrr": round(self.mean_mrr, 4),
            "mean_ndcg": round(self.mean_ndcg, 4),
            "per_query": [
                {
                    "query": q.query,
                    "hits": q.hits,
                    "relevant": sorted(q.relevant),
                    "recall": round(q.recall_at_k, 4),
                    "precision": round(q.precision_at_k, 4),
                    "mrr": round(q.reciprocal_rank, 4),
                    "ndcg": round(q.ndcg_at_k, 4),
                }
                for q in self.per_query
            ],
        }


def _metrics_for_query(
    query: str,
    hits: list[str],
    relevant: set[str],
    k: int,
) -> QueryMetrics:
    """Compute the standard four metrics for one query's retrieval output."""
    truncated = hits[:k]
    # Recall: fraction of relevant docs found in top-k
    n_found = sum(1 for h in truncated if h in relevant)
    recall = n_found / len(relevant) if relevant else 0.0
    # Precision: fraction of top-k that are relevant
    precision = n_found / k if k > 0 else 0.0
    # Reciprocal rank of first relevant hit
    mrr = 0.0
    for i, h in enumerate(truncated, start=1):
        if h in relevant:
            mrr = 1.0 / i
            break
    # NDCG: Discounted Cumulative Gain normalized by ideal DCG
    dcg = 0.0
    for i, h in enumerate(truncated, start=1):
        if h in relevant:
            dcg += 1.0 / math.log2(i + 1)
    ideal_dcg = sum(1.0 / math.log2(i + 1) for i in range(1, min(len(relevant), k) + 1))
    ndcg = dcg / ideal_dcg if ideal_dcg > 0 else 0.0
    return QueryMetrics(
        query=query, mode="",
        hits=truncated, relevant=relevant,
        recall_at_k=recall, precision_at_k=precision,
        reciprocal_rank=mrr, ndcg_at_k=ndcg, k=k,
    )


def evaluate(
    retriever: VectoraRetriever,
    queries: Iterable[LabeledQuery],
    mode: RetrievalMode,
    k: int = 10,
    decay: float = 0.4,
) -> EvalReport:
    """Run all queries in the given mode and aggregate metrics."""
    per_query: list[QueryMetrics] = []
    for q in queries:
        results = retriever.retrieve(q.query, k=k, mode=mode, decay=decay)
        hits = [r.doc.id for r in results]
        m = _metrics_for_query(q.query, hits, q.relevant, k)
        m.mode = mode.value
        per_query.append(m)
    n = len(per_query) or 1
    mean_recall = sum(m.recall_at_k for m in per_query) / n
    mean_precision = sum(m.precision_at_k for m in per_query) / n
    mean_mrr = sum(m.reciprocal_rank for m in per_query) / n
    mean_ndcg = sum(m.ndcg_at_k for m in per_query) / n
    return EvalReport(
        mode=mode.value, k=k, per_query=per_query,
        mean_recall=mean_recall, mean_precision=mean_precision,
        mean_mrr=mean_mrr, mean_ndcg=mean_ndcg,
    )


def compare(
    retriever: VectoraRetriever,
    queries: Iterable[LabeledQuery],
    k: int = 10,
    decay: float = 0.4,
) -> dict[str, Any]:
    """Run top-k AND Vectora; return both reports + the deltas."""
    query_list = list(queries)  # materialize so we can iterate twice
    topk = evaluate(retriever, query_list, mode=RetrievalMode.TOPK, k=k, decay=decay)
    vec = evaluate(retriever, query_list, mode=RetrievalMode.VECTORA, k=k, decay=decay)
    delta = {
        "recall": round(vec.mean_recall - topk.mean_recall, 4),
        "precision": round(vec.mean_precision - topk.mean_precision, 4),
        "mrr": round(vec.mean_mrr - topk.mean_mrr, 4),
        "ndcg": round(vec.mean_ndcg - topk.mean_ndcg, 4),
    }
    return {"topk": topk.as_dict(), "vectora": vec.as_dict(), "delta": delta}


# ═══════════════════════════════════════════════════════════════════════
# Built-in eval dataset — 12 queries with hand-labeled relevance
# ═══════════════════════════════════════════════════════════════════════

EVAL_CORPUS: list[Document] = [
    # caching cluster
    Document(id="cache-redis",   text="Redis caching strategies for Django applications"),
    Document(id="cache-aside",   text="Cache-aside pattern with code examples"),
    Document(id="cache-compare", text="Memcached vs Redis: choosing a backend"),
    Document(id="cache-invalid", text="Cache invalidation problems in distributed systems"),
    Document(id="memory-pressure",  text="Memory pressure when caching aggressively in Redis"),
    Document(id="memory-heap",      text="JVM heap tuning under heavy cache load"),
    Document(id="db-patterns",      text="Database query patterns that beat caching for analytics"),
    Document(id="db-replicas",      text="When read replicas are better than caching"),
    Document(id="db-materialized",  text="Materialized views as an alternative to caching"),
    # architecture cluster
    Document(id="arch-monolith",    text="When to split a monolith for cache locality and team boundaries"),
    Document(id="arch-microservice", text="Microservices and the distributed cache problem"),
    # rate-limiting cluster
    Document(id="rl-429",     text="HTTP 429 rate limit responses and client retry strategy"),
    Document(id="rl-bucket",  text="Token bucket rate limiting implementation"),
    Document(id="rl-headers", text="Rate limit headers spec and best practices"),
    Document(id="bp-cascading", text="Backpressure patterns in cascading distributed systems"),
    Document(id="bp-queue",     text="Queue depth as a load signal for autoscaling"),
    Document(id="bp-retries",   text="Why naive retries amplify outages and what to do instead"),
    # embeddings / retrieval cluster
    Document(id="emb-sentence", text="Sentence transformers tutorial for semantic search"),
    Document(id="emb-openai",   text="OpenAI ada-002 embedding dimensions and pricing"),
    Document(id="emb-vdbs",     text="Vector database comparison: Pinecone vs Weaviate vs Qdrant"),
    Document(id="emb-curse",    text="Curse of dimensionality in high-dimensional embedding spaces"),
    Document(id="emb-hybrid",   text="Hybrid search combining BM25 sparse vectors and dense embeddings"),
    Document(id="emb-limits",   text="When semantic search hurts more than helps for exact-match queries"),
    # RAG cluster
    Document(id="rag-arch",   text="RAG pipeline architecture for production LLM applications"),
    Document(id="rag-rerank", text="Reranking strategies for retrieval augmented generation"),
    Document(id="rag-chunk",  text="Chunking strategies for long documents in RAG systems"),
    # LLM prompt cluster
    Document(id="llm-cot",        text="Prompt engineering patterns for chain of thought reasoning"),
    Document(id="llm-tokencost",  text="Token cost optimization across OpenAI Anthropic and Google"),
    Document(id="llm-halluc",     text="LLM hallucination detection and mitigation techniques"),
    Document(id="ops-obs",        text="Observability for LLM applications: metrics traces and logs"),
]


EVAL_QUERIES: list[LabeledQuery] = [
    # Q1: Direct caching query — top-k should nail the caching cluster
    LabeledQuery(
        query="caching strategies for web applications",
        relevant={"cache-redis", "cache-aside", "cache-compare", "cache-invalid"},
        description="Direct retrieval — top-k and Vectora both should do well.",
    ),
    # Q2: Second-hop query — the useful docs (memory pressure, db alternatives)
    # do not share surface tokens with 'caching tradeoffs'
    LabeledQuery(
        query="caching tradeoffs for a monolith",
        relevant={"cache-redis", "cache-invalid", "memory-pressure", "arch-monolith",
                  "db-patterns", "db-replicas"},
        description="Second-hop query — Vectora should outperform via graph walk.",
    ),
    # Q3: Alternative patterns — should reach the materialized-view and replicas docs
    LabeledQuery(
        query="when NOT to cache data",
        relevant={"db-patterns", "db-replicas", "db-materialized", "cache-invalid"},
        description="Alternatives query — requires reasoning beyond surface tokens.",
    ),
    # Q4: Rate limiting direct
    LabeledQuery(
        query="API rate limiting implementation",
        relevant={"rl-429", "rl-bucket", "rl-headers"},
        description="Direct rate-limiting query.",
    ),
    # Q5: Rate limiting with second-hop (backpressure)
    LabeledQuery(
        query="preventing server overload from too many requests",
        relevant={"rl-429", "rl-bucket", "bp-cascading", "bp-queue", "bp-retries"},
        description="Rate-limit-adjacent — backpressure is the second hop.",
    ),
    # Q6: Retry behavior — requires pulling from multiple clusters
    LabeledQuery(
        query="retry strategies and cascading failures",
        relevant={"rl-429", "bp-retries", "bp-cascading"},
        description="Cross-cluster query.",
    ),
    # Q7: Embeddings direct
    LabeledQuery(
        query="sentence embedding models",
        relevant={"emb-sentence", "emb-openai", "emb-hybrid"},
        description="Direct embedding query.",
    ),
    # Q8: Limits of semantic search — requires emb-curse, emb-limits, emb-hybrid
    LabeledQuery(
        query="when embedding-based search fails",
        relevant={"emb-curse", "emb-limits", "emb-hybrid"},
        description="Subtle embedding query needing second-hop for emb-hybrid.",
    ),
    # Q9: Vector DB comparison
    LabeledQuery(
        query="choosing a vector database",
        relevant={"emb-vdbs", "emb-openai", "emb-hybrid"},
        description="Vector DB query.",
    ),
    # Q10: RAG pipeline
    LabeledQuery(
        query="building a RAG pipeline",
        relevant={"rag-arch", "rag-rerank", "rag-chunk", "emb-vdbs", "emb-hybrid"},
        description="RAG-centric query pulling from RAG + embedding clusters.",
    ),
    # Q11: LLM prompt engineering
    LabeledQuery(
        query="chain of thought prompting",
        relevant={"llm-cot", "llm-halluc", "llm-tokencost"},
        description="LLM prompting query.",
    ),
    # Q12: Observability / ops
    LabeledQuery(
        query="monitoring a production LLM app",
        relevant={"ops-obs", "llm-halluc", "llm-tokencost"},
        description="Ops-focused LLM query.",
    ),
]


def run_builtin_eval(k: int = 10, decay: float = 0.4) -> dict[str, Any]:
    """Run the full built-in eval dataset and return the comparison."""
    r = VectoraRetriever()
    r.add_documents(EVAL_CORPUS)
    r.build_graph()
    return compare(r, EVAL_QUERIES, k=k, decay=decay)


if __name__ == "__main__":
    import json

    result = run_builtin_eval()
    d = result["delta"]
    topk = result["topk"]
    vec = result["vectora"]
    print("Built-in Vectora eval — 30 docs, 12 queries\n")
    print(f"{'metric':<12} {'top-k':>10} {'Vectora':>10} {'delta':>10}")
    print("-" * 46)
    for m in ("recall", "precision", "mrr", "ndcg"):
        tk = topk[f"mean_{m}"]
        v = vec[f"mean_{m}"]
        dv = d[m]
        print(f"{m:<12} {tk:>10.4f} {v:>10.4f} {dv:>+10.4f}")
    print(f"\nk={topk['k']}, n_queries={topk['n_queries']}")
