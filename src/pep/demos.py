"""Scripted demo scenarios — let an automated runner drive PEP through a
conversation so the user can press Start and watch what happens.

Each scenario tells one story about a thing PEP does that a raw AI can't.
The Demo Runner in the web UI fetches these scripts and replays them
turn-by-turn against /chat/compare, so the user sees the raw AI vs PEP+AI
comparison evolve in real time.

Adding a new scenario:
  1. Append a Scenario to SCENARIOS below.
  2. The web UI will pick it up automatically via GET /demos.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass
class DemoStep:
    """One turn the demo bot will send."""

    text: str
    note: str = ""  # human-readable description of what this turn is testing


@dataclass
class Scenario:
    id: str
    title: str
    summary: str
    moral: str  # the one-line takeaway, shown when the demo finishes
    steps: list[DemoStep] = field(default_factory=list)


SCENARIOS: list[Scenario] = [
    Scenario(
        id="memory_across_turns",
        title="Memory across turns",
        summary=(
            "PEP remembers what you told it earlier and feeds it back to the "
            "base AI on later turns. The raw AI is amnesiac."
        ),
        moral=(
            "Same base model, two answers. PEP's column knows about your "
            "project because it remembered turns 1 and 2 — the raw column "
            "has no memory at all."
        ),
        steps=[
            DemoStep(
                text="I'm working on a research project called PEP.",
                note="Establishes the project name. Both columns acknowledge.",
            ),
            DemoStep(
                text="PEP stands for Predictive Encoding and Preparation. "
                "It's a memory and context layer that sits on top of a base AI.",
                note="Drops a definition. PEP stores it as a new memory.",
            ),
            DemoStep(
                text="The three core ideas are prediction, reactivation, and residuals.",
                note="Adds related facts. Watch the link graph form.",
            ),
            DemoStep(
                text="What does my project do, and what are its three core ideas?",
                note="The reveal: raw AI says 'no idea', PEP cites earlier turns.",
            ),
        ],
    ),
    Scenario(
        id="long_horizon_recall",
        title="Long-horizon recall (with distractor turns)",
        summary=(
            "Drops three facts at the start, then four unrelated 'distractor' "
            "turns, then asks about the early facts. Tests whether PEP can "
            "still surface them after the conversation has wandered."
        ),
        moral=(
            "PEP cuts through the distractors and surfaces the early facts. "
            "The raw AI has no idea what you're referring to."
        ),
        steps=[
            DemoStep(
                text="My favorite color is purple.",
                note="Fact 1.",
            ),
            DemoStep(
                text="I have a cat named Mochi.",
                note="Fact 2.",
            ),
            DemoStep(
                text="I'm currently learning to play the cello.",
                note="Fact 3.",
            ),
            DemoStep(
                text="What's the difference between TCP and UDP?",
                note="Distractor — completely unrelated topic.",
            ),
            DemoStep(
                text="Can you explain how photosynthesis works?",
                note="Another distractor.",
            ),
            DemoStep(
                text="What are some good Italian restaurants in San Francisco?",
                note="Yet another distractor.",
            ),
            DemoStep(
                text="So tell me — what's my favorite color, what's my pet's "
                "name, and what instrument am I learning?",
                note="The reveal: PEP recalls all three facts; raw AI is lost.",
            ),
        ],
    ),
    Scenario(
        id="sense_disambiguation",
        title="Sense disambiguation (the 'power' problem)",
        summary=(
            "Uses the same word ('power') in two completely different senses "
            "across the conversation, then asks a question that should pull "
            "only one sense. PEP's Sense Mapper detects the ambiguity and "
            "picks the right cluster of memories."
        ),
        moral=(
            "PEP's Sense Mapper distinguishes the physics 'power' from the "
            "political 'power' and retrieves only the relevant memories. "
            "The raw AI doesn't even know the words mean different things."
        ),
        steps=[
            DemoStep(
                text="In physics, power is measured in watts. It equals work "
                "divided by time.",
                note="Establishes the physics sense of 'power'.",
            ),
            DemoStep(
                text="A 100-watt lightbulb uses energy at the rate of 100 "
                "joules per second.",
                note="Reinforces the physics sense.",
            ),
            DemoStep(
                text="In political theory, power is the ability to influence "
                "the behavior of others, often through institutions.",
                note="Now a totally different sense of 'power'.",
            ),
            DemoStep(
                text="Authoritarian regimes consolidate power by controlling "
                "the media and the courts.",
                note="Reinforces the political sense.",
            ),
            DemoStep(
                text="How is power measured in a laboratory experiment?",
                note="The reveal: should pull the physics memories, not the political ones.",
            ),
        ],
    ),
    Scenario(
        id="building_a_concept",
        title="Building a concept across turns",
        summary=(
            "Watches PEP build up a knowledge graph as you teach it about a "
            "topic over multiple turns. Each turn adds new facts that PEP "
            "links to existing memories. The Sky View tab will show the "
            "memories accumulating after the demo runs."
        ),
        moral=(
            "PEP doesn't just store facts — it links them. Click the Sky View "
            "tab after this demo runs to see the memory graph. Click the "
            "Categories tab and run consolidation to see emergent categories."
        ),
        steps=[
            DemoStep(
                text="A neural network is made of layers of artificial neurons.",
                note="Foundation fact.",
            ),
            DemoStep(
                text="Each neuron applies a weighted sum of its inputs followed by "
                "an activation function.",
                note="Adds a related concept.",
            ),
            DemoStep(
                text="During training, weights are updated by backpropagation, "
                "which computes the gradient of the loss with respect to each weight.",
                note="Adds a process. Should link to neurons + weights.",
            ),
            DemoStep(
                text="Common activation functions include ReLU, sigmoid, and tanh.",
                note="Adds detail to the activation function concept.",
            ),
            DemoStep(
                text="Now explain to me, using everything I just told you, "
                "how a neural network actually learns.",
                note="The reveal: PEP synthesizes from the constellation of memories.",
            ),
        ],
    ),
]


SCENARIOS_BY_ID: dict[str, Scenario] = {s.id: s for s in SCENARIOS}


def list_scenarios() -> list[dict]:
    """Return all scenarios as plain dicts (for the /demos JSON endpoint)."""
    return [
        {
            "id": s.id,
            "title": s.title,
            "summary": s.summary,
            "moral": s.moral,
            "step_count": len(s.steps),
        }
        for s in SCENARIOS
    ]


def get_scenario(scenario_id: str) -> dict | None:
    """Return one scenario as a plain dict, including the full step list."""
    s = SCENARIOS_BY_ID.get(scenario_id)
    if not s:
        return None
    return asdict(s)
