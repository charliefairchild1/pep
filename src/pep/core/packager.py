"""Packager — assembles the structured envelope handed to the base AI."""

from __future__ import annotations

from pep.schemas.input_schema import InterpretedInput, Prediction, UserInput
from pep.schemas.memory_schema import MemoryObject
from pep.schemas.pep_packet import (
    ActivationTrace,
    PEPPacket,
    ResidualReport,
)
from pep.schemas.state_schema import State


def _unfold_memory(memory: MemoryObject, face: str) -> dict:
    """Render one memory as a dict, exposing only the requested face."""
    content = memory.faces.get(face) or memory.core  # type: ignore[arg-type]
    return {
        "id": memory.id,
        "face": face,
        "content": content,
        "brightness": round(memory.brightness, 3),
        "tags": memory.tags,
    }


def package(
    *,
    user_input: UserInput,
    interpreted: InterpretedInput,
    prediction: Prediction,
    state: State,
    activated: list[MemoryObject],
    activation_trace: ActivationTrace,
    residual: ResidualReport,
) -> PEPPacket:
    """Assemble a PEPPacket. The base AI sees only what we put in here."""
    # Use the trace to figure out which face to expose for each memory
    face_by_id = {entry.memory_id: entry.face_used for entry in activation_trace.activated}
    selected = [
        _unfold_memory(m, face_by_id.get(m.id, "semantic"))
        for m in activated
    ]

    # Response goal: a one-line directive derived from the interpretation
    goal = _response_goal_for(interpreted)
    constraints: list[str] = []
    if state.urgency > 0.6:
        constraints.append("be concise; user signaled urgency")
    if state.uncertainty > 0.6:
        constraints.append("flag uncertainty explicitly; do not over-commit")
    if state.exploration > 0.7:
        constraints.append("offer alternatives, not just one path")

    return PEPPacket(
        session_id=user_input.session_id,
        raw_input=user_input.text,
        interpreted=interpreted,
        prediction=prediction,
        state=state,
        selected_memories=selected,
        residual=residual,
        activation_trace=activation_trace,
        response_goal=goal,
        constraints=constraints,
    )


def _response_goal_for(interpreted: InterpretedInput) -> str:
    return {
        "implement": "produce or modify code as requested",
        "plan": "lay out a clear, scoped plan of action",
        "explain": "explain clearly, no fluff",
        "explore": "open the question; consider multiple angles",
        "ask_question": "answer the question directly",
        "command": "confirm or execute the requested action",
        "small_talk": "respond naturally and briefly",
        "unknown": "respond helpfully and ask for clarification if needed",
    }.get(interpreted.task_type, "respond helpfully")
