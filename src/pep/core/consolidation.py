"""Consolidation pass — merge duplicates, build summaries, reconsolidate
drifted memories, decay stale items.

Called by `pep consolidate` or on a schedule. This is the "sleep cycle" for
PEP's memory: it reorganizes, compresses, and cleans up without losing what
matters. PTO framing: reduce dissipation by eliminating redundancy and
promoting useful abstractions.
"""

from __future__ import annotations

from collections import Counter

from pep.core.categories import run_category_engine
from pep.memory.store import MemoryStore
from pep.models.llm_client import LLMClient
from pep.schemas.memory_schema import Link, MemoryObject

# Tunables
DUPLICATE_TAG_OVERLAP = 0.7   # Jaccard threshold to consider two memories near-duplicates
DUPLICATE_CORE_PREFIX = 100   # compare first N chars of core for duplicates
STALE_ACTIVATION_FLOOR = 0    # memories with 0 activations after decay rounds
STALE_BRIGHTNESS_FLOOR = 0.08 # brightness below this = candidate for pruning
SUMMARY_CLUSTER_SIZE = 5      # minimum memories in a category to generate a summary

# Drift threshold: a memory whose drift_score has crept above this gets its
# faces regenerated during the consolidation pass. The reactivator increments
# drift by 0.01 per activation (capped at 1.0), so 0.4 corresponds to roughly
# 40 reactivations — i.e. memories that are heavily used and likely have
# evolved meaning across many recall events.
RECONSOLIDATION_DRIFT_THRESHOLD = 0.4


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def merge_near_duplicates(store: MemoryStore) -> int:
    """Find memories with very similar tags + core prefix, merge into one.

    The surviving memory gets the higher brightness and union of tags/links.
    Returns the number of merges.
    """
    memories = store.all_memories()
    merged_ids: set[str] = set()
    merge_count = 0

    for i in range(len(memories)):
        if memories[i].id in merged_ids:
            continue
        m1 = memories[i]
        tags1 = {t.lower() for t in m1.tags}
        core1 = m1.core[:DUPLICATE_CORE_PREFIX].lower().strip()

        for j in range(i + 1, len(memories)):
            if memories[j].id in merged_ids:
                continue
            m2 = memories[j]
            tags2 = {t.lower() for t in m2.tags}
            core2 = m2.core[:DUPLICATE_CORE_PREFIX].lower().strip()

            if _jaccard(tags1, tags2) >= DUPLICATE_TAG_OVERLAP and core1 == core2:
                # Merge m2 into m1: keep the brighter one, union tags + links
                m1.brightness = max(m1.brightness, m2.brightness)
                m1.activation_count += m2.activation_count
                existing_link_targets = {l.to_id for l in m1.links}
                for link in m2.links:
                    if link.to_id not in existing_link_targets and link.to_id != m1.id:
                        m1.links.append(link)
                new_tags = list(dict.fromkeys(m1.tags + [t for t in m2.tags if t not in tags1]))
                m1.tags = new_tags[:20]
                # Keep the richer faces
                for face_name, face_text in m2.faces.items():
                    if face_name not in m1.faces:
                        m1.faces[face_name] = face_text

                store.upsert_memory(m1)
                # Remove the duplicate
                store._conn.execute("DELETE FROM memories WHERE id = ?", (m2.id,))
                store._conn.execute("DELETE FROM links WHERE from_id = ? OR to_id = ?", (m2.id, m2.id))
                store._conn.commit()
                merged_ids.add(m2.id)
                merge_count += 1

    return merge_count


def prune_stale_memories(store: MemoryStore) -> int:
    """Remove memories that have faded to near-zero brightness and were never
    reactivated. Returns count removed."""
    removed = 0
    for m in store.all_memories():
        if m.brightness <= STALE_BRIGHTNESS_FLOOR and m.activation_count <= STALE_ACTIVATION_FLOOR:
            store._conn.execute("DELETE FROM memories WHERE id = ?", (m.id,))
            store._conn.execute("DELETE FROM links WHERE from_id = ? OR to_id = ?", (m.id, m.id))
            store._conn.execute("DELETE FROM memory_categories WHERE memory_id = ?", (m.id,))
            removed += 1
    if removed:
        store._conn.commit()
    return removed


def generate_summary_memories(store: MemoryStore) -> int:
    """For each category with enough members, create a summary memory that
    captures the gist. The summary links to its source memories.

    Returns the number of summaries created.
    """
    created = 0
    for cat in store.list_categories():
        members = store.category_members(cat["id"])
        if len(members) < SUMMARY_CLUSTER_SIZE:
            continue

        # Check if a summary already exists for this category
        existing = [m for m in members if m.source_type == "summary"]
        if existing:
            continue

        # Build a summary from the top tags and brightest member cores
        top_tags = cat.get("top_tags") or []
        brightest = sorted(members, key=lambda m: m.brightness, reverse=True)[:3]
        core_snippets = [m.core[:120] for m in brightest]

        summary_core = (
            f"Summary of category '{cat['name']}' ({len(members)} memories).\n"
            f"Key themes: {', '.join(top_tags)}.\n"
            f"Representative content:\n" + "\n".join(f"- {s}" for s in core_snippets)
        )

        summary = MemoryObject(
            core=summary_core,
            faces={"semantic": summary_core[:300]},
            fold_weights={"semantic": 1.0},
            tags=list(top_tags)[:12],
            brightness=cat.get("avg_brightness", 0.5),
            source_type="summary",
        )
        # Link the summary to its source memories
        for m in brightest:
            summary.links.append(Link(to_id=m.id, relation="semantic", weight=0.7))

        store.upsert_memory(summary)
        store.assign_memory_to_category(summary.id, cat["id"], strength=1.0)
        created += 1

    return created


def redistill_legacy_memories(store: MemoryStore) -> int:
    """Find memories whose core is in the legacy verbose `USER: ... ASSISTANT: ...`
    transcript format and re-distill them into single substantive sentences.

    The Updater used to store entire conversation paragraphs as the core.
    This function finds those memories (cores starting with `USER:` or
    containing `\\nASSISTANT:`) and replaces the core with the result of
    the new heuristic distiller. The faces dict is preserved as-is, but
    `semantic` face is updated to match the new core.

    Returns the number of memories rewritten.
    """
    from pep.core.updater import _heuristic_distill

    rewritten = 0
    for m in store.all_memories():
        # Detect the legacy verbose pattern
        is_legacy = (
            m.core.startswith("USER:")
            or m.core.startswith("USER ")
            or "\nASSISTANT:" in m.core
        )
        if not is_legacy:
            continue

        # Try to extract user_text and assistant_text from the verbose core
        user_text = ""
        assistant_text = ""
        if "ASSISTANT:" in m.core:
            parts = m.core.split("ASSISTANT:", 1)
            user_text = parts[0].replace("USER:", "").strip()
            assistant_text = parts[1].strip()
        else:
            user_text = m.core.replace("USER:", "").strip()

        new_core = _heuristic_distill(user_text, assistant_text)
        if not new_core or new_core == m.core:
            continue

        m.core = new_core
        if "semantic" in m.faces:
            m.faces["semantic"] = new_core[:300]
        store.upsert_memory(m)
        rewritten += 1

    return rewritten


def reconsolidate_drifted_memories(
    store: MemoryStore,
    *,
    llm: LLMClient | None = None,
    drift_threshold: float = RECONSOLIDATION_DRIFT_THRESHOLD,
) -> int:
    """Regenerate faces for memories whose drift_score has exceeded the threshold.

    Drift is incremented every time a memory is reactivated — it represents
    how much the memory has been "touched" across recall events. The brain
    analogy: every time you recall a memory, you reconsolidate it, and the
    new version may differ from the old. PEP's drift_score tracks that.

    This function picks up the drifted memories and rebuilds their faces from
    the current core text. With a real LLM, faces are regenerated via the
    same multi-face encoder used at storage time. Without an LLM, the
    function falls back to a heuristic that just rebuilds the semantic face.
    Either way, drift_score is reset to 0 after reconsolidation.

    Returns the number of memories reconsolidated.
    """
    from pep.core.updater import _llm_encode, VALID_FACES

    reconsolidated = 0
    for m in store.all_memories():
        if (m.drift_score or 0.0) < drift_threshold:
            continue

        # Try the LLM path first if a real client is available
        new_core = m.core
        new_faces = dict(m.faces)
        new_fold_weights = dict(m.fold_weights)
        new_tags = list(m.tags)

        if llm is not None and getattr(llm, "is_real", False):
            # Synthesize a fake user_input/interpreted/response trio so we can
            # reuse the existing _llm_encode helper. The "exchange" we hand it
            # is the memory's own core text, framed as a self-summary so the
            # encoder treats it as content to re-encode.
            from pep.schemas.input_schema import InterpretedInput, UserInput
            fake_input = UserInput(
                text=f"reconsolidate this memory: {m.core[:300]}",
                session_id=m.session_id,
            )
            fake_interpreted = InterpretedInput(
                intent="reconsolidate",
                topic=m.core[:60],
                entities=m.tags[:5],
                task_type="explain",
            )
            encoded = _llm_encode(
                user_input=fake_input,
                interpreted=fake_interpreted,
                assistant_response=m.core,
                llm=llm,
            )
            if encoded is not None:
                new_core, new_tags_llm, new_faces, new_fold_weights = encoded
                # Keep at least the original tags as a floor — don't lose them
                # if the LLM forgets to re-emit them.
                merged_tags: list[str] = []
                seen: set[str] = set()
                for t in (new_tags_llm or []) + new_tags:
                    tl = t.lower()
                    if tl and tl not in seen:
                        seen.add(tl)
                        merged_tags.append(tl)
                new_tags = merged_tags[:16]

        # Apply the changes (heuristic path: just resets drift; LLM path:
        # also rewrites core/faces/tags). Either way, drift goes to 0 and
        # confidence is bumped slightly because we just refreshed.
        m.core = new_core
        m.faces = new_faces
        m.fold_weights = new_fold_weights
        m.tags = new_tags
        m.drift_score = 0.0
        m.confidence = min(1.0, (m.confidence or 1.0) + 0.05)

        store.upsert_memory(m)
        reconsolidated += 1

    return reconsolidated


def run_consolidation(
    store: MemoryStore,
    *,
    llm: LLMClient | None = None,
) -> dict[str, int]:
    """Run the full consolidation pass: dedup, prune, summarize, reconsolidate, categories.

    Returns a summary of what happened.
    """
    legacy_rewritten = redistill_legacy_memories(store)
    dupes = merge_near_duplicates(store)
    pruned = prune_stale_memories(store)
    summaries = generate_summary_memories(store)
    reconsolidated = reconsolidate_drifted_memories(store, llm=llm)
    cat_results = run_category_engine(store)

    return {
        "legacy_redistilled": legacy_rewritten,
        "duplicates_merged": dupes,
        "stale_pruned": pruned,
        "summaries_created": summaries,
        "reconsolidated_drifted": reconsolidated,
        **cat_results,
    }
