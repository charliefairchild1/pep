"""PEP Streamlit Dashboard — three views into PEP's internal state.

Run with: `uv run streamlit run src/pep/dashboard.py`

Views:
  1. **Run Inspector** — pick a run, see the PEPPacket, activation trace,
     state before/after, residual, metrics.
  2. **Sky View** — memory graph for a session. Brightness, links,
     activation counts, drift. The "stars" metaphor made visual.
  3. **Sense Map** — for detected ambiguous terms, show the candidate senses
     and which one was chosen.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import streamlit as st

from pep.memory.store import MemoryStore


def _get_store() -> MemoryStore:
    db_path = os.environ.get("PEP_DB_PATH", str(Path("data") / "pep.db"))
    return MemoryStore(db_path)


def _run_inspector(store: MemoryStore) -> None:
    st.header("Run Inspector")
    runs = store.list_runs(limit=100)
    if not runs:
        st.info("No runs yet. Send a message to POST /chat first.")
        return

    labels = [f"{r['id'][:16]}… | {r['user_input'][:60]}" for r in runs]
    idx = st.selectbox("Pick a run", range(len(labels)), format_func=lambda i: labels[i])
    run = store.get_run(runs[idx]["id"])  # type: ignore[index]
    if not run:
        st.error("Run not found.")
        return

    packet = run["packet"]
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Interpreted")
        st.json(packet.get("interpreted", {}))
        st.subheader("Prediction")
        st.json(packet.get("prediction", {}))

    with col2:
        st.subheader("State before → after")
        st.json({"before": run["state_before"], "after": run["state_after"]})
        st.subheader("Residual")
        st.json(packet.get("residual", {}))

    st.subheader("Activated memories")
    trace = packet.get("activation_trace", {})
    for entry in trace.get("activated", []):
        with st.expander(f"{entry['memory_id']} (score={entry['score']:.3f}, face={entry['face_used']})"):
            st.json(entry["components"])
            if entry.get("constellation_id") is not None:
                st.caption(f"Constellation #{entry['constellation_id']}")

    if trace.get("constellations"):
        st.subheader("Constellations")
        for c in trace["constellations"]:
            st.markdown(
                f"**#{c['id']}** — {len(c['member_ids'])} members, "
                f"cohesion={c['cohesion']:.2f}, collective={c['collective_score']:.2f}"
            )
            st.caption(", ".join(c["member_ids"]))

    if trace.get("resolved_terms"):
        st.subheader("Sense disambiguation")
        for rt in trace["resolved_terms"]:
            st.markdown(f"**{rt['term']}** — ambiguity={rt['ambiguity_score']:.2f}, margin={rt['margin']:.2f}")
            if rt.get("chosen_sense"):
                st.caption(f"Chosen: {rt['chosen_sense']['sense_label']} (conf={rt['chosen_sense']['confidence']:.2f})")
            for alt in rt.get("alternatives", []):
                st.caption(f"  Alt: {alt['sense_label']} (conf={alt['confidence']:.2f})")

    if trace.get("fallback_to_strategic_search"):
        st.warning(f"Strategic fallback triggered: {trace.get('fallback_reason', '')}")

    st.subheader("Metrics (seconds)")
    st.json(packet.get("metrics", {}))

    st.subheader("Selected memories (what the base AI saw)")
    for m in packet.get("selected_memories", []):
        st.markdown(f"**[{m['id']}]** ({m['face']}) — brightness={m['brightness']:.2f}")
        st.text(m["content"][:300])

    st.subheader("Response")
    st.text(run["response"][:2000] if run.get("response") else "(no response)")


def _sky_view(store: MemoryStore) -> None:
    st.header("Sky View — Memory Field")
    memories = store.all_memories()
    if not memories:
        st.info("No memories yet.")
        return

    st.metric("Total memories", len(memories))

    # Sort by brightness (brightest first = most important star)
    memories.sort(key=lambda m: m.brightness, reverse=True)

    for m in memories[:50]:
        brightness_bar = "█" * int(m.brightness * 20)
        drift_bar = "░" * int(m.drift_score * 20)
        label = (
            f"**{m.id}** — "
            f"★ {m.brightness:.2f} `{brightness_bar}` | "
            f"drift {m.drift_score:.2f} `{drift_bar}` | "
            f"activated {m.activation_count}x | "
            f"links {len(m.links)} | "
            f"faces {list(m.faces.keys())}"
        )
        with st.expander(label):
            st.text(m.core[:300])
            st.caption(f"tags: {', '.join(m.tags)}")
            if m.links:
                st.caption("links → " + ", ".join(f"{l.to_id} ({l.relation}, w={l.weight:.1f})" for l in m.links[:8]))
            if m.future_use:
                st.caption(f"future_use: {m.future_use}")
            if m.sense_profile:
                st.caption(f"sense_profile: {json.dumps({k: v.model_dump() for k, v in m.sense_profile.items()}, indent=2)}")


def _sense_map(store: MemoryStore) -> None:
    st.header("Sense Map")
    st.caption("Shows terms that PEP detected as ambiguous in past runs, with the chosen sense and alternatives.")

    runs = store.list_runs(limit=100)
    found_any = False
    for r in runs:
        full = store.get_run(r["id"])
        if not full:
            continue
        packet = full["packet"]
        trace = packet.get("activation_trace", {})
        for rt in trace.get("resolved_terms", []):
            found_any = True
            st.markdown(f"### `{rt['term']}` (run {r['id'][:12]}…)")
            st.metric("Ambiguity score", f"{rt['ambiguity_score']:.2f}")
            st.metric("Margin", f"{rt['margin']:.2f}")
            if rt.get("chosen_sense"):
                cs = rt["chosen_sense"]
                st.success(f"Chosen: **{cs['sense_label']}** (confidence={cs['confidence']:.2f})")
                st.caption(f"Context tags: {', '.join(cs.get('context_tags', []))}")
            for alt in rt.get("alternatives", []):
                st.info(f"Alternative: {alt['sense_label']} (confidence={alt['confidence']:.2f})")
                st.caption(f"Context tags: {', '.join(alt.get('context_tags', []))}")
            st.divider()

    if not found_any:
        st.info("No ambiguous terms detected in any past runs yet.")


def main() -> None:
    st.set_page_config(
        page_title="PEP Dashboard",
        page_icon="🧠",
        layout="wide",
    )
    st.title("PEP — Predictive Encoding and Preparation")
    st.caption("PEP shapes cognition; the base AI does cognition.")

    store = _get_store()

    tab1, tab2, tab3 = st.tabs(["Run Inspector", "Sky View", "Sense Map"])
    with tab1:
        _run_inspector(store)
    with tab2:
        _sky_view(store)
    with tab3:
        _sense_map(store)


if __name__ == "__main__":
    main()
