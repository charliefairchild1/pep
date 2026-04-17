"""Vectora — graph-based retrieval engine.

The actual Python implementation of Vectora's retrieval primitive. Builds a
weighted document graph from embeddings (and optional keyword/typed edges),
then runs spreading activation from query-matching seeds outward to surface
second-hop documents that top-k vector search would miss.

Public API:
    from pep.vectora import VectoraRetriever, Document
    r = VectoraRetriever()
    r.add_documents([Document(id="a", text="..."), ...])
    r.build_graph()
    results = r.retrieve("query text", k=10, decay=0.4)
"""

from .context import ContextConfig, ContextEvent, ContextTracker
from .document import Document
from .embeddings import LocalEmbedder, EmbedderProtocol
from .graph import DocumentGraph, Edge
from .kg import EdgeProvenance, TraversalResult, TypedEdge, VectoraKG
from .retrieval import VectoraRetriever, RetrievalResult, RetrievalMode
from .watch import VectoraWatch, WatchConfig, WatchResult

__all__ = [
    "ContextConfig",
    "ContextEvent",
    "ContextTracker",
    "Document",
    "DocumentGraph",
    "Edge",
    "EdgeProvenance",
    "EmbedderProtocol",
    "LocalEmbedder",
    "RetrievalMode",
    "RetrievalResult",
    "TraversalResult",
    "TypedEdge",
    "VectoraKG",
    "VectoraRetriever",
    "VectoraWatch",
    "WatchConfig",
    "WatchResult",
]
