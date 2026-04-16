"""Memory Updater tests — heuristic and LLM-path encoding, plus trajectory gate."""

from __future__ import annotations

from pep.core.updater import update_memory
from pep.memory.store import MemoryStore
from pep.schemas.input_schema import InterpretedInput, UserInput
from pep.schemas.pep_packet import PEPPacket, ResidualReport


def _residual_storeable(novelty: float = 0.7) -> ResidualReport:
    return ResidualReport(novelty_score=novelty, should_store=True, reason="test")


class _FakeLLM:
    """A fake LLM that simulates structured supporting-call responses.

    Dispatches on the system prompt: trajectory scoring vs. multi-face encoding.
    """

    name = "fake"
    is_real = True

    def __init__(self, trajectory_score: float = 0.8) -> None:
        self.support_calls = 0
        self.trajectory_score = trajectory_score
        self.encode_calls = 0
        self.trajectory_calls = 0

    def complete(self, packet: PEPPacket) -> str:
        return "ok"

    def support(self, *, system: str, user: str, model_tier: str = "cheap") -> str:
        self.support_calls += 1
        if "Trajectory Scorer" in system:
            self.trajectory_calls += 1
            return (
                f'{{"trajectory_score": {self.trajectory_score}, '
                f'"reason": "fake-trajectory"}}'
            )
        if "Memory Updater" in system:
            self.encode_calls += 1
            return (
                '{"core":"Talked about predictive memory architectures.",'
                ' "tags":["prediction","memory","architecture","pep"],'
                ' "faces":{"semantic":"Prediction reduces storage and reaction cost.",'
                '          "action":"Use prediction to gate storage.",'
                '          "predictive":"This will connect to spreading activation."},'
                ' "fold_weights":{"semantic":0.9,"action":0.7,"predictive":0.6}}'
            )
        return ""


def test_updater_heuristic_path_stores_single_face() -> None:
    store = MemoryStore(":memory:")
    interpreted = InterpretedInput(
        intent="explain", topic="prediction", entities=["prediction"], task_type="explain"
    )
    new = update_memory(
        store=store,
        user_input=UserInput(
            text="Explain prediction in PEP. How does it reduce storage cost?"
        ),
        interpreted=interpreted,
        assistant_response=(
            "Prediction reduces storage by encoding only the residual error. "
            "Anything that matches the prediction is implicit and can be discarded."
        ),
        residual=_residual_storeable(),
        activated_ids=[],
        llm=None,  # heuristic path
    )
    assert new is not None
    assert "semantic" in new.faces
    assert set(new.faces.keys()) == {"semantic"}
    # Trajectory score should have been recorded on the new memory's future_use
    assert "trajectory_at_storage" in new.future_use
    assert 0.0 <= new.future_use["trajectory_at_storage"] <= 1.0


def test_updater_llm_path_stores_multiple_faces_and_calls_trajectory() -> None:
    store = MemoryStore(":memory:")
    fake = _FakeLLM(trajectory_score=0.9)
    interpreted = InterpretedInput(
        intent="explain", topic="prediction", entities=["prediction"], task_type="explain"
    )
    new = update_memory(
        store=store,
        user_input=UserInput(text="Tell me about predictive memory."),
        interpreted=interpreted,
        assistant_response="Prediction reduces storage and reaction cost.",
        residual=_residual_storeable(),
        activated_ids=["mem_prior"],
        llm=fake,  # type: ignore[arg-type]
    )
    assert new is not None
    # The fake LLM provided three faces
    assert set(new.faces.keys()) == {"semantic", "action", "predictive"}
    assert new.fold_weights["semantic"] == 0.9
    # Co-activation link still created
    assert any(link.to_id == "mem_prior" for link in new.links)
    # Both supporting calls were made: one for trajectory, one for encoding
    assert fake.trajectory_calls == 1
    assert fake.encode_calls == 1
    # The LLM trajectory score should have been recorded on the new memory
    assert new.future_use["trajectory_at_storage"] == 0.9


def test_updater_skips_when_residual_says_not_to_store() -> None:
    store = MemoryStore(":memory:")
    no_store = ResidualReport(novelty_score=0.1, should_store=False, reason="boring")
    new = update_memory(
        store=store,
        user_input=UserInput(text="hi"),
        interpreted=InterpretedInput(intent="small_talk", topic="hi", task_type="small_talk"),
        assistant_response="hello",
        residual=no_store,
        activated_ids=[],
        llm=None,
    )
    assert new is None
    assert len(store.all_memories()) == 0


def test_updater_skips_when_trajectory_score_is_low() -> None:
    """High novelty alone is not enough — if trajectory is low, don't store.

    PTO: a surprising one-shot input that won't matter again is dissipative.
    """
    store = MemoryStore(":memory:")
    fake = _FakeLLM(trajectory_score=0.0)
    # Even with high novelty, the combined gate (0.5*0.7 + 0.5*0.0 = 0.35) is
    # below TRAJECTORY_GATE = 0.40, so storage should be skipped.
    new = update_memory(
        store=store,
        user_input=UserInput(text="A novel surprising message."),
        interpreted=InterpretedInput(
            intent="ask_question", topic="surprise", entities=["surprise"], task_type="ask_question"
        ),
        assistant_response="ack",
        residual=_residual_storeable(novelty=0.7),
        activated_ids=[],
        llm=fake,  # type: ignore[arg-type]
    )
    assert new is None
    # Trajectory call still happened (we needed it to make the decision)
    assert fake.trajectory_calls == 1
    # But encoding was NOT called because storage was rejected
    assert fake.encode_calls == 0


def test_updater_distills_assistant_response_into_short_core() -> None:
    """Heuristic path: stored core should be a SHORT distilled sentence,
    not a verbatim USER:/ASSISTANT: paragraph."""
    store = MemoryStore(":memory:")
    interpreted = InterpretedInput(
        intent="explain", topic="prediction", entities=["prediction"], task_type="explain"
    )
    long_response = (
        "Sure, that's a great question. Prediction in PEP is a mechanism "
        "by which the system anticipates likely user intent before the "
        "full input is processed, allowing memory to be pre-loaded and "
        "context to be staged in advance of the actual query."
    )
    new = update_memory(
        store=store,
        user_input=UserInput(
            text="Tell me what prediction is in PEP and why it's useful."
        ),
        interpreted=interpreted,
        assistant_response=long_response,
        residual=_residual_storeable(),
        activated_ids=[],
        llm=None,
    )
    assert new is not None
    # Core should NOT contain the USER:/ASSISTANT: framing
    assert "USER:" not in new.core
    assert "ASSISTANT:" not in new.core
    # Core should NOT start with the filler "Sure, that's a great question"
    assert not new.core.lower().startswith("sure, that's a great")
    # Core should be reasonably short
    assert len(new.core) <= 280
    # Should still contain the substantive content
    assert "prediction" in new.core.lower() or "PEP" in new.core


def test_updater_skips_filler_exchange_entirely() -> None:
    """A 'hi' or 'thanks' style exchange should produce NO stored memory."""
    store = MemoryStore(":memory:")
    interpreted = InterpretedInput(
        intent="small_talk", topic="hi", task_type="small_talk"
    )
    new = update_memory(
        store=store,
        user_input=UserInput(text="hi"),
        interpreted=interpreted,
        assistant_response="Hello! How can I help?",
        residual=_residual_storeable(),
        activated_ids=[],
        llm=None,
    )
    assert new is None
    assert len(store.all_memories()) == 0


def test_updater_skips_thanks_exchange() -> None:
    store = MemoryStore(":memory:")
    interpreted = InterpretedInput(
        intent="small_talk", topic="thanks", task_type="small_talk"
    )
    new = update_memory(
        store=store,
        user_input=UserInput(text="thanks"),
        interpreted=interpreted,
        assistant_response="You're welcome.",
        residual=_residual_storeable(),
        activated_ids=[],
        llm=None,
    )
    assert new is None


def test_updater_picks_substantive_sentence_skipping_filler_openings() -> None:
    """If the assistant response opens with filler then has a substantive
    sentence, the distiller should pick the substantive one."""
    store = MemoryStore(":memory:")
    interpreted = InterpretedInput(
        intent="explain", topic="memory", entities=["memory"], task_type="explain"
    )
    response = (
        "That's interesting! I think you're asking about memory consolidation. "
        "Memory consolidation is the process by which short-term memories "
        "are stabilized into long-term memories through repeated reactivation."
    )
    new = update_memory(
        store=store,
        user_input=UserInput(text="What is memory consolidation in the brain?"),
        interpreted=interpreted,
        assistant_response=response,
        residual=_residual_storeable(),
        activated_ids=[],
        llm=None,
    )
    assert new is not None
    # The core should be the substantive sentence, not the "that's interesting" opener
    assert "consolidation" in new.core.lower()
    assert not new.core.lower().startswith("that's interesting")
    assert not new.core.lower().startswith("i think you're asking")


def test_updater_llm_path_rejects_too_short_core() -> None:
    """If the LLM returns a core shorter than MIN_CORE_LENGTH, the encoder
    should fall back to the heuristic path (because the short core signals
    'this exchange is filler — don't store')."""
    from pep.core.updater import MIN_CORE_LENGTH

    class _ShortCoreLLM:
        name = "fake"
        is_real = True
        def complete(self, packet): return "ok"
        def stream_complete(self, packet): yield "ok"
        def complete_raw(self, *, system, user): return "ok"
        def support(self, *, system, user, model_tier="cheap"):
            if "Trajectory Scorer" in system:
                return '{"trajectory_score": 0.8, "reason": "test"}'
            # The encode response has an empty core
            return '{"core": "", "tags": [], "faces": {}, "fold_weights": {}}'

    store = MemoryStore(":memory:")
    new = update_memory(
        store=store,
        user_input=UserInput(text="Tell me about predictive memory architectures."),
        interpreted=InterpretedInput(
            intent="explain", topic="prediction", entities=["prediction"], task_type="explain"
        ),
        assistant_response="A long substantive response about prediction architectures.",
        residual=_residual_storeable(),
        activated_ids=[],
        llm=_ShortCoreLLM(),  # type: ignore[arg-type]
    )
    # Empty LLM core → fall back to heuristic distillation, which CAN
    # produce a valid distilled memory from the substantive response
    assert new is not None
    # Whatever it stored should not be empty
    assert len(new.core) >= MIN_CORE_LENGTH


def test_updater_stores_when_both_novelty_and_trajectory_are_high() -> None:
    store = MemoryStore(":memory:")
    fake = _FakeLLM(trajectory_score=0.8)
    new = update_memory(
        store=store,
        user_input=UserInput(text="Substantive new message about prediction architecture."),
        interpreted=InterpretedInput(
            intent="explain",
            topic="prediction",
            entities=["prediction", "architecture"],
            task_type="explain",
        ),
        assistant_response="A long, substantive answer about prediction architecture.",
        residual=_residual_storeable(novelty=0.7),
        activated_ids=[],
        llm=fake,  # type: ignore[arg-type]
    )
    assert new is not None
    assert new.future_use["trajectory_at_storage"] == 0.8
