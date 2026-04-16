"""Benchmark runner — execute benchmark tasks against a policy, collect results.

Usage:
    from pep.runner import run_benchmark
    results = run_benchmark("ambiguity", policy=PEPFullPolicy(), llm=stub, embedder=emb)
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from pep.embed import Embedder
from pep.memory.store import MemoryStore
from pep.models.llm_client import LLMClient
from pep.policies.base import ContextPolicy
from pep.schemas.input_schema import UserInput
from pep.schemas.memory_schema import MemoryObject

BENCHMARKS_DIR = Path(__file__).resolve().parent.parent.parent / "benchmarks"


def _load_benchmark(name: str) -> dict:
    path = BENCHMARKS_DIR / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"Benchmark not found: {path}")
    return json.loads(path.read_text())


def run_benchmark(
    benchmark_name: str,
    *,
    policy: ContextPolicy,
    llm: LLMClient,
    embedder: Embedder,
    db_path: str = ":memory:",
) -> list[dict]:
    """Run all tasks in a benchmark against a single policy.

    Returns a list of result dicts, one per task, containing:
      - task_id, input, policy_name
      - selected_memory_ids, selected_tags (what the policy surfaced)
      - response (the base AI's text)
      - latency_s
      - the task's expected_* fields (for the evaluator)
    """
    bench = _load_benchmark(benchmark_name)
    store = MemoryStore(db_path)

    # Seed memories. Each seed is allowed to override id, brightness, and
    # state_modulation so benchmarks can target specific PEP features.
    for seed in bench.get("seed_memories", []):
        kwargs: dict = {
            "core": seed["core"],
            "faces": {"semantic": seed["core"][:300]},
            "fold_weights": {"semantic": 1.0},
            "tags": seed.get("tags", []),
            "brightness": float(seed.get("brightness", 0.5)),
            "source_type": seed.get("source_type", "document"),
        }
        if "id" in seed:
            kwargs["id"] = seed["id"]
        if "state_modulation" in seed:
            # Each entry: state_var name -> multiplier on brightness when state is high
            kwargs["state_modulation"] = {
                str(k): float(v) for k, v in seed["state_modulation"].items()
            }
        store.upsert_memory(MemoryObject(**kwargs))

    session_id = f"bench_{benchmark_name}_{policy.name}"
    results: list[dict] = []

    for task in bench.get("tasks", []):
        user_input = UserInput(text=task["input"], session_id=session_id)

        start = time.perf_counter()
        pr = policy.run_turn(
            user_input=user_input,
            store=store,
            embedder=embedder,
            llm=llm,
        )
        elapsed = time.perf_counter() - start

        selected_ids = [m.get("id", "") for m in pr.packet.selected_memories]
        selected_tags: set[str] = set()
        for m in pr.packet.selected_memories:
            selected_tags.update(t.lower() for t in m.get("tags", []))

        result = {
            "task_id": task["id"],
            "task_type": task.get("type", "test"),
            "input": task["input"],
            "policy": policy.name,
            "benchmark": benchmark_name,
            "response": pr.response[:500],
            "selected_memory_ids": selected_ids,
            "selected_tags": sorted(selected_tags),
            "memories_activated": len(pr.packet.activation_trace.activated),
            "constellations": len(pr.packet.activation_trace.constellations),
            "novelty": pr.packet.residual.novelty_score,
            "trajectory": pr.packet.residual.trajectory_score,
            "fallback": pr.packet.activation_trace.fallback_to_strategic_search,
            "latency_s": round(elapsed, 4),
        }
        # Carry forward the expected_* / wrong_* / distractor_* fields for the evaluator
        for key, val in task.items():
            if (
                key.startswith("expected_")
                or key.startswith("distractor_")
                or key.startswith("wrong_")
            ):
                result[key] = val

        # Capture the state_after vector so the evaluator can verify state-conditioned tests
        try:
            result["state_after"] = pr.state_after.model_dump()
        except Exception:
            pass

        results.append(result)

    store.close()
    return results
