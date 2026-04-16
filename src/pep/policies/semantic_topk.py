"""Baseline B: flat semantic top-k retrieval.

Embeds the query, retrieves the K most similar memories by cosine, stuffs
them into the prompt. No state modulation, no spreading, no faces, no
trajectory gating. This is standard RAG.
"""

from __future__ import annotations

from pep.embed import Embedder, cosine
from pep.memory.store import MemoryStore
from pep.models.llm_client import LLMClient
from pep.policies.base import PolicyResult
from pep.schemas.input_schema import InterpretedInput, Prediction, UserInput
from pep.schemas.memory_schema import MemoryObject
from pep.schemas.pep_packet import (
    ActivationEntry,
    ActivationTrace,
    PEPPacket,
    ResidualReport,
)
from pep.schemas.state_schema import State

TOP_K = 5


class SemanticTopKPolicy:
    name = "semantic_topk"

    def run_turn(
        self,
        *,
        user_input: UserInput,
        store: MemoryStore,
        embedder: Embedder,
        llm: LLMClient,
    ) -> PolicyResult:
        state_before = store.latest_state(user_input.session_id)

        # Embed query
        query_vec = embedder.embed_query(user_input.text)

        # Score all memories by cosine similarity
        candidates = store.all_memories()
        scored: list[tuple[float, MemoryObject]] = []
        for m in candidates:
            if not m.core:
                continue
            mem_vec = embedder.embed_query(m.core)
            sim = max(0.0, cosine(query_vec, mem_vec))
            scored.append((sim, m))

        scored.sort(key=lambda t: t[0], reverse=True)
        top = scored[:TOP_K]

        interpreted = InterpretedInput(
            intent="unknown", topic=user_input.text[:40], task_type="unknown",
            notes="semantic_topk baseline — no interpretation",
        )
        prediction = Prediction(notes="semantic_topk baseline — no prediction")
        state_after = state_before

        selected = [
            {"id": m.id, "face": "semantic", "content": m.core[:300],
             "brightness": m.brightness, "tags": m.tags}
            for _, m in top
        ]
        activated = [
            ActivationEntry(
                memory_id=m.id, score=round(sim, 4),
                components={"semantic": round(sim, 4)}, face_used="semantic",
            )
            for sim, m in top
        ]

        packet = PEPPacket(
            session_id=user_input.session_id,
            raw_input=user_input.text,
            interpreted=interpreted,
            prediction=prediction,
            state=state_after,
            selected_memories=selected,
            residual=ResidualReport(reason="semantic_topk — no residual scoring"),
            activation_trace=ActivationTrace(
                candidates_considered=len(candidates),
                activated=activated,
                notes="semantic_topk — cosine only",
            ),
            response_goal="answer the user",
        )

        response = llm.complete(packet)

        # Store (always, no gating)
        core = f"USER: {user_input.text[:200]}\nASSISTANT: {response[:200]}"
        store.upsert_memory(MemoryObject(
            core=core,
            faces={"semantic": core[:300]},
            fold_weights={"semantic": 1.0},
            tags=[w.lower() for w in user_input.text.split()[:8]],
            brightness=0.5,
            session_id=user_input.session_id,
            source_type="conversation",
        ))

        turn = store.turn_count(user_input.session_id) + 1
        store.log_state(user_input.session_id, turn, state_after)
        store.log_run(packet, response, state_before, state_after)

        return PolicyResult(packet, response, state_before, state_after)
