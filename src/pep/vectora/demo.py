"""Sample corpora + a runnable demo for the Vectora retrieval engine.

    python -m pep.vectora.demo

prints the top-k baseline vs Vectora's spreading-activation results for a
handful of queries against a small synthetic corpus.
"""

from __future__ import annotations

from .document import Document
from .retrieval import RetrievalMode, VectoraRetriever


# ── A small corpus designed to expose the second-hop advantage ──────────
# The "caching" question is best answered by docs about memory pressure and
# query patterns (NOT directly about caching) — but those docs are linked to
# the caching docs via the document graph. Top-k won't find them; Vectora
# will.
SAMPLE_CORPUS: list[Document] = [
    Document(id="cache-1", text="Redis caching strategies for Django web applications"),
    Document(id="cache-2", text="The cache-aside pattern explained with code examples"),
    Document(id="cache-3", text="Memcached vs Redis: choosing a caching backend"),
    Document(id="cache-4", text="Cache invalidation problems in distributed systems"),
    Document(id="memory-1", text="Memory pressure when caching too aggressively in Redis"),
    Document(id="memory-2", text="JVM heap tuning under heavy cache load"),
    Document(id="db-1", text="Database query patterns that beat caching for analytics workloads"),
    Document(id="db-2", text="When read replicas are better than caching"),
    Document(id="db-3", text="Materialized views as an alternative to caching"),
    Document(id="arch-1", text="When to split a monolith for cache locality and team boundaries"),
    Document(id="arch-2", text="Microservices and the distributed cache problem"),
    Document(id="rate-1", text="HTTP 429 rate limit responses and client retry strategy"),
    Document(id="rate-2", text="Token bucket rate limiting implementation in Go"),
    Document(id="rate-3", text="Rate limit headers spec and best practices"),
    Document(id="backpres-1", text="Backpressure patterns in cascading distributed systems"),
    Document(id="backpres-2", text="Queue depth as a load signal for autoscaling"),
    Document(id="backpres-3", text="Why naive retries amplify outages and what to do instead"),
    Document(id="embed-1", text="Sentence transformers tutorial for semantic search"),
    Document(id="embed-2", text="OpenAI ada-002 embedding dimensions and pricing"),
    Document(id="embed-3", text="Vector database comparison: Pinecone vs Weaviate vs Qdrant"),
    Document(id="embed-4", text="Curse of dimensionality in high-dimensional embedding spaces"),
    Document(id="embed-5", text="Hybrid search combining BM25 sparse vectors and dense embeddings"),
    Document(id="embed-6", text="When semantic search hurts more than helps for exact-match queries"),
    Document(id="rag-1", text="RAG pipeline architecture for production LLM applications"),
    Document(id="rag-2", text="Reranking strategies for retrieval augmented generation"),
    Document(id="rag-3", text="Chunking strategies for long documents in RAG systems"),
    Document(id="llm-1", text="Prompt engineering patterns for chain of thought reasoning"),
    Document(id="llm-2", text="Token cost optimization across OpenAI Anthropic and Google"),
    Document(id="llm-3", text="LLM hallucination detection and mitigation techniques"),
    Document(id="ops-1", text="Observability for LLM applications: metrics traces and logs"),
]


def _format_results(label: str, results, max_show: int = 8) -> str:
    lines = [f"\n=== {label} ==="]
    for i, r in enumerate(results[:max_show], start=1):
        hop_marker = "" if r.hop_distance == 0 else f" [hop {r.hop_distance}]"
        lines.append(f"  {i}. {r.doc.id:<14} score={r.score:.3f}{hop_marker}  {r.doc.text[:64]}")
    return "\n".join(lines)


def run_demo() -> None:
    queries = [
        "caching strategies for a monolith",
        "rate limiting and load shedding",
        "embedding-based document search",
    ]

    retriever = VectoraRetriever()
    retriever.add_documents(SAMPLE_CORPUS)
    stats = retriever.build_graph()
    print(f"Vectora demo corpus: {stats}")

    for q in queries:
        print(f"\n\n{'=' * 70}\nQUERY: {q!r}\n{'=' * 70}")
        topk = retriever.retrieve(q, k=8, mode=RetrievalMode.TOPK)
        vec = retriever.retrieve(q, k=8, mode=RetrievalMode.VECTORA)
        print(_format_results("TOP-K (baseline)", topk))
        print(_format_results("VECTORA (spreading activation)", vec))
        # Highlight what Vectora added
        topk_ids = {res.doc.id for res in topk}
        added = [res for res in vec if res.doc.id not in topk_ids]
        if added:
            print(f"\nVectora surfaced {len(added)} document(s) top-k missed:")
            for res in added:
                print(f"  + {res.doc.id} [hop {res.hop_distance}] — {res.doc.text[:60]}")


if __name__ == "__main__":
    run_demo()
