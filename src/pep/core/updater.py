"""Memory Updater — encode the exchange into memory after the base AI responds.

Two paths, like Interpreter / State / Predictor:

1. **LLM path** (preferred when a real client is available): one haiku call
   produces ALL the structured fields for the new memory in a single shot —
   the canonical core, smarter tags, AND the five non-semantic faces
   (episodic, value, action, predictive, user). The fold_weights record how
   confident the model was in each face.

2. **Heuristic fallback**: the original Phase 1 logic. Truncated text core,
   character-stripped tags, semantic-face-only.

This is the heart of Slice 2B: turning each stored exchange into a real
multi-face memory object instead of a flat blob.
"""

from __future__ import annotations

from pep.core._llm_helpers import call_for_json
from pep.core.interpreter import _STOPWORDS  # type: ignore[attr-defined]
from pep.memory.store import MemoryStore
from pep.models.llm_client import LLMClient
from pep.schemas.input_schema import InterpretedInput, UserInput
from pep.schemas.memory_schema import FaceName, Link, MemoryObject
from pep.schemas.pep_packet import ResidualReport


VALID_FACES: tuple[FaceName, ...] = (
    "semantic", "episodic", "value", "action", "predictive", "user",
)


# Trajectory storage tunables (PTO Slice 2G).
# Combined gate: 0.5 * novelty + 0.5 * trajectory must clear this floor for
# the memory to actually be persisted. Lower than the residual's local
# threshold because trajectory is doing additional work.
TRAJECTORY_GATE = 0.40


# ----- Heuristic fallback -----

def _is_filler_exchange(user_text: str) -> bool:
    """Detect filler exchanges (greetings, acknowledgements) that aren't
    worth storing as memories."""
    t = user_text.strip().lower()
    if len(t) < 12:
        return True
    if any(t.startswith(p.replace("user: ", "")) for p in FILLER_PREFIXES):
        return True
    return False


def _heuristic_distill(user_text: str, assistant_text: str) -> str:
    """Heuristic distillation: pick the most substance-dense sentence from
    the assistant's response, fall back to the user message if needed.

    This is the no-LLM path. It can't actually understand semantics, so it
    just picks the longest content sentence (a rough proxy for "the part
    with actual information"). The LLM path is much smarter but expensive.
    """
    if _is_filler_exchange(user_text):
        return ""

    # Split assistant response into sentences and pick the longest one
    # that isn't filler. Crude but works as a baseline.
    assistant_clean = assistant_text.strip().replace("\n", " ")
    # Strip stub-llm and ollama markers
    for marker in ("[stub-llm]", "[ollama"):
        if marker in assistant_clean:
            assistant_clean = assistant_clean.split(marker)[0].strip()

    if not assistant_clean:
        # Fall back to the user's question, distilled
        return user_text.strip().replace("\n", " ")[:200]

    # Sentence split (rough)
    import re
    sentences = re.split(r"(?<=[.!?])\s+", assistant_clean)
    # Filter filler openings
    filler_openings = (
        "that's a great", "that's interesting", "i agree", "good question",
        "great point", "thank you", "thanks for", "i appreciate",
    )
    substantive = [
        s for s in sentences
        if len(s) >= 20
        and not any(s.lower().startswith(f) for f in filler_openings)
    ]
    if substantive:
        # Pick the longest substantive sentence
        best = max(substantive, key=len)
        return best[:280]
    # No good sentence found — return a truncated fallback
    return assistant_clean[:200]


def _heuristic_tag_extract(*texts: str) -> list[str]:
    tags: list[str] = []
    for text in texts:
        for word in text.split():
            cleaned = "".join(c for c in word.lower() if c.isalnum())
            if cleaned and cleaned not in _STOPWORDS and len(cleaned) > 3:
                tags.append(cleaned)
    out: list[str] = []
    seen: set[str] = set()
    for t in tags:
        if t not in seen:
            seen.add(t)
            out.append(t)
        if len(out) >= 12:
            break
    return out


def _heuristic_faces(core: str) -> tuple[dict[FaceName, str], dict[FaceName, float]]:
    return ({"semantic": core[:300]}, {"semantic": 1.0})


# ----- Trajectory scoring (Slice 2G option (b)) -----

_TRAJECTORY_SYSTEM = """\
You are PEP's Trajectory Scorer. Given one exchange between a user and a
base AI, decide how likely it is that the substance of this exchange will
be USEFUL in future similar conversations with this user.

Useful means: it would be a good thing for the system to remember and
retrieve next time, because doing so would improve a future response.
Not useful means: it's a one-shot answer, small talk, throwaway, or
already implicit in well-known knowledge.

Return a single JSON object with exactly these keys:
- "trajectory_score": float in [0, 1]. 0.0 = will never matter again,
  1.0 = highly likely to matter for many future questions.
- "reason": string. One short sentence explaining your score.

Output ONLY the JSON object. No prose.
"""


def _llm_trajectory_score(
    *,
    user_input: UserInput,
    interpreted: InterpretedInput,
    assistant_response: str,
    llm: LLMClient,
) -> tuple[float, str] | None:
    user_block = (
        f"User intent: {interpreted.intent} ({interpreted.task_type})\n\n"
        f"USER:\n{user_input.text.strip()[:1500]}\n\n"
        f"ASSISTANT:\n{assistant_response.strip()[:1500]}"
    )
    parsed = call_for_json(
        llm, system=_TRAJECTORY_SYSTEM, user=user_block, model_tier="cheap"
    )
    if not parsed:
        return None
    try:
        score = max(0.0, min(1.0, float(parsed.get("trajectory_score", 0.5))))
        reason = str(parsed.get("reason", ""))[:240]
        return score, reason
    except (TypeError, ValueError):
        return None


def _heuristic_trajectory_score(
    *,
    user_input: UserInput,
    interpreted: InterpretedInput,
    assistant_response: str,
) -> tuple[float, str]:
    """Fallback trajectory score when no real LLM is available.

    Heuristic signals (correlate, weakly, with future usefulness):
    - User input length (longer = more substance)
    - Number of distinct content entities
    - Task type (implement/plan/explore tend to matter for future turns;
      small_talk and command don't)
    - Response length (very short = less likely to be reusable)
    """
    text = user_input.text.strip()
    response = assistant_response.strip()

    length_signal = min(1.0, len(text) / 400.0)
    entity_signal = min(1.0, len(interpreted.entities) / 5.0)
    response_signal = min(1.0, len(response) / 600.0)

    task_bonus = {
        "implement": 0.20,
        "plan": 0.20,
        "explain": 0.10,
        "explore": 0.20,
        "ask_question": 0.05,
        "command": -0.20,
        "small_talk": -0.30,
        "unknown": 0.0,
    }.get(interpreted.task_type, 0.0)

    raw = 0.4 * length_signal + 0.3 * entity_signal + 0.3 * response_signal + task_bonus
    score = max(0.0, min(1.0, raw))
    reason = (
        f"heuristic; len={len(text)}; entities={len(interpreted.entities)}; "
        f"task={interpreted.task_type}; bonus={task_bonus:+.2f}"
    )
    return score, reason


# ----- LLM path -----

_UPDATER_SYSTEM = """\
You are PEP's Memory Updater. You have just observed one turn of conversation.
Your job is to DISTILL the substance into a compressed memory object that
PEP can retrieve later.

CRUCIAL: do NOT store the conversation verbatim. Do NOT echo the user's
words. Do NOT include filler like "they said that" or "the assistant
explained". Extract the MEANING, not the transcript. If nothing new or
substantive was said, you may return an empty core (the system will skip
storage). The bar for storage is high — only durable, reusable facts.

Return JSON with exactly these keys:

- "core": string. ONE distilled sentence (15-35 words). Must be a
  standalone fact or claim that would be useful to know in a future turn,
  with no reference to "the user" or "the conversation". Examples:
    GOOD: "Predictive overlays can lower base-model latency by pre-fetching
           the most likely context before a query lands."
    BAD:  "The user asked about prediction and the assistant explained
           that prediction is when..."
    BAD:  "We talked about how prediction reduces storage."
  If the exchange was filler (greetings, acknowledgements, "ok thanks"),
  return an EMPTY string for core. The system will skip storage.

- "tags": array of 3-8 short lowercase strings. Concrete, retrievable
  keywords drawn from the substance, not from the wording. Avoid
  generic verbs like "said", "explained", "discussed".

- "faces": object with up to six keys, each a string ≤120 chars. ONLY
  include faces that genuinely add a different angle on the core fact.
    * "semantic":   what it means in plain terms
    * "episodic":   the situation it came up in (1 short clause)
    * "value":      why it's worth keeping (1 short clause)
    * "action":     what to do with it
    * "predictive": what this fact is likely to connect with later
    * "user":       what this reveals about the user's intent or style
  An empty faces object is fine if the core alone says it all.

- "fold_weights": object mapping each filled face to a float in [0,1] —
  how confident you are that the face is genuinely informative.

Output ONLY the JSON object, no prose, no fences.
"""

# A core shorter than this won't be considered "substantive" and the
# memory will be skipped (filler heuristic).
MIN_CORE_LENGTH = 16

# Filler phrases that signal a vacuous exchange. If the heuristic core
# starts with one of these, skip storage.
FILLER_PREFIXES = (
    "user: hi", "user: hello", "user: thanks", "user: thank you",
    "user: ok", "user: okay", "user: cool", "user: nice", "user: great",
    "user: yes", "user: no", "user: sure",
)


def _llm_encode(
    *,
    user_input: UserInput,
    interpreted: InterpretedInput,
    assistant_response: str,
    llm: LLMClient,
) -> tuple[str, list[str], dict[FaceName, str], dict[FaceName, float]] | None:
    user_block = (
        f"User intent: {interpreted.intent} ({interpreted.task_type})\n"
        f"User entities: {interpreted.entities}\n\n"
        f"USER:\n{user_input.text.strip()[:1500]}\n\n"
        f"ASSISTANT:\n{assistant_response.strip()[:1500]}\n\n"
        f"Distill this into ONE standalone fact. If there's nothing "
        f"substantive to remember, return an empty core."
    )
    parsed = call_for_json(llm, system=_UPDATER_SYSTEM, user=user_block, model_tier="cheap")
    if not parsed:
        return None

    try:
        core = str(parsed.get("core", "")).strip()
        # Empty / too-short cores signal "filler exchange — don't store"
        if not core or len(core) < MIN_CORE_LENGTH:
            return None
        # Hard cap so the LLM can't sneak a paragraph through
        if len(core) > 320:
            core = core[:320].rsplit(" ", 1)[0] + "..."

        raw_tags = parsed.get("tags") or []
        if not isinstance(raw_tags, list):
            raw_tags = []
        tags: list[str] = []
        seen: set[str] = set()
        for t in raw_tags:
            t_clean = str(t).lower().strip()[:40]
            if t_clean and t_clean not in seen and len(t_clean) > 1:
                seen.add(t_clean)
                tags.append(t_clean)
            if len(tags) >= 16:
                break

        raw_faces = parsed.get("faces") or {}
        if not isinstance(raw_faces, dict):
            raw_faces = {}
        faces: dict[FaceName, str] = {}
        for name in VALID_FACES:
            value = raw_faces.get(name)
            if isinstance(value, str) and value.strip():
                faces[name] = value.strip()[:400]
        if "semantic" not in faces:
            faces["semantic"] = core[:300]

        raw_weights = parsed.get("fold_weights") or {}
        if not isinstance(raw_weights, dict):
            raw_weights = {}
        weights: dict[FaceName, float] = {}
        for name in faces:
            try:
                w = float(raw_weights.get(name, 0.5))
            except (TypeError, ValueError):
                w = 0.5
            weights[name] = max(0.0, min(1.0, w))

        return core, tags, faces, weights
    except (TypeError, ValueError, AttributeError):
        return None


# ----- Public entry point -----

def update_memory(
    *,
    store: MemoryStore,
    user_input: UserInput,
    interpreted: InterpretedInput,
    assistant_response: str,
    residual: ResidualReport,
    activated_ids: list[str],
    llm: LLMClient | None = None,
) -> MemoryObject | None:
    """Store the exchange as a multi-face memory if novelty + trajectory clear the gate.

    PTO Slice 2G: storage is gated by the *combined* signal of local novelty
    (Residual Scorer) and forward-looking trajectory score (this function).
    Either alone is insufficient. The intent is to store things that are both
    new AND likely to matter in the future, not just things that are surprising
    in the moment.
    """
    # Trajectory score (PTO option (b)). LLM path if available AND the LLM
    # actually returns a usable result; otherwise fall back to heuristic.
    # We track which path produced the value so the §8.1 follow-up
    # experiment can compare predictive power of the two approaches.
    trajectory: tuple[float, str] | None = None
    trajectory_source: str = "heuristic"
    if llm is not None and llm.is_real:
        trajectory = _llm_trajectory_score(
            user_input=user_input,
            interpreted=interpreted,
            assistant_response=assistant_response,
            llm=llm,
        )
        if trajectory is not None:
            trajectory_source = "llm"
    if trajectory is None:
        trajectory = _heuristic_trajectory_score(
            user_input=user_input,
            interpreted=interpreted,
            assistant_response=assistant_response,
        )
    trajectory_score, trajectory_reason = trajectory
    # Mutate the residual report so the run trace records what we computed
    residual.trajectory_score = round(trajectory_score, 4)
    residual.reason = (residual.reason + " | trajectory: " + trajectory_reason)[:480]

    # Combined gate: both halves matter, neither alone is enough.
    combined = 0.5 * residual.novelty_score + 0.5 * trajectory_score
    if not residual.should_store or combined < TRAJECTORY_GATE:
        return None

    # Encoding path (Slice 2B)
    encoded = None
    if llm is not None and llm.is_real:
        encoded = _llm_encode(
            user_input=user_input,
            interpreted=interpreted,
            assistant_response=assistant_response,
            llm=llm,
        )

    if encoded is not None:
        core, tags, faces, fold_weights = encoded
    else:
        # Heuristic path: distill rather than transcribe. If the exchange is
        # filler (greetings, acknowledgements, or substance-free), the
        # distiller returns an empty string and we skip storage entirely.
        core = _heuristic_distill(user_input.text, assistant_response)
        if not core:
            return None  # filler exchange — nothing worth keeping
        tags = _heuristic_tag_extract(user_input.text, " ".join(interpreted.entities))
        faces, fold_weights = _heuristic_faces(core)

    # Brightness scales with the COMBINED signal, not just novelty.
    # Surprising-AND-future-relevant things stick the most.
    brightness = min(1.0, 0.3 + 0.7 * combined)

    new = MemoryObject(
        core=core,
        faces=faces,
        fold_weights=fold_weights,
        tags=tags,
        brightness=brightness,
        session_id=user_input.session_id,
        source_type="conversation",
        future_use={"trajectory_at_storage": round(trajectory_score, 4)},
        trajectory_source=trajectory_source,
    )
    # Co-activation links: every memory we just retrieved gets a light link
    # from the new memory back to it, recording that they appeared together.
    for prior_id in activated_ids:
        new.links.append(Link(to_id=prior_id, relation="co_activated", weight=0.3))

    store.upsert_memory(new)
    return new
