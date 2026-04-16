"""Context policies for benchmarking and side-by-side comparison.

A policy defines HOW context is selected for the base AI. The benchmark
runner and the /chat/compare endpoint swap policies while holding the model
and task constant — that's the whole experiment.
"""

from pep.policies.pep_full import PEPFullPolicy
from pep.policies.raw_ai import RawAIPolicy
from pep.policies.recent_window import RecentWindowPolicy
from pep.policies.semantic_topk import SemanticTopKPolicy

__all__ = [
    "PEPFullPolicy",
    "RawAIPolicy",
    "RecentWindowPolicy",
    "SemanticTopKPolicy",
]
