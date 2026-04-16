"""Read-only debug routes. The trace is the whole point — make it inspectable."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

router = APIRouter()


@router.get("/memories")
async def list_memories(request: Request, session_id: str | None = None) -> list[dict]:
    store = request.app.state.store
    memories = store.all_memories(session_id=session_id)
    return [m.model_dump() for m in memories]


@router.get("/memories/{memory_id}")
async def get_memory(memory_id: str, request: Request) -> dict:
    store = request.app.state.store
    m = store.get_memory(memory_id)
    if not m:
        raise HTTPException(status_code=404, detail="memory not found")
    return m.model_dump()


@router.get("/runs")
async def list_runs(request: Request, session_id: str | None = None, limit: int = 50) -> list[dict]:
    store = request.app.state.store
    return store.list_runs(session_id=session_id, limit=limit)


@router.get("/runs/{run_id}")
async def get_run(run_id: str, request: Request) -> dict:
    store = request.app.state.store
    run = store.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="run not found")
    return run


@router.get("/demos")
async def list_demos() -> list[dict]:
    """List all scripted demo scenarios available to the Demo Runner."""
    from pep.demos import list_scenarios

    return list_scenarios()


@router.get("/demos/{scenario_id}")
async def get_demo(scenario_id: str) -> dict:
    """Return one demo scenario including its full step list."""
    from pep.demos import get_scenario

    scenario = get_scenario(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="scenario not found")
    return scenario


@router.post("/sessions/{session_id}/clear")
async def clear_session(session_id: str, request: Request) -> dict:
    """Wipe all memories, state, and runs for a session. Used by the Demo
    Runner so a scenario can be re-run cleanly."""
    store = request.app.state.store
    return store.clear_session(session_id)


@router.get("/state/{session_id}")
async def get_state(session_id: str, request: Request) -> dict:
    store = request.app.state.store
    return {
        "session_id": session_id,
        "state": store.latest_state(session_id).model_dump(),
        "turn_count": store.turn_count(session_id),
    }


@router.get("/categories")
async def list_categories(request: Request) -> list[dict]:
    store = request.app.state.store
    return store.list_categories()


@router.get("/categories/{category_id}")
async def get_category(category_id: str, request: Request) -> dict:
    store = request.app.state.store
    cat = store.get_category(category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="category not found")
    members = store.category_members(category_id)
    cat["members"] = [m.model_dump() for m in members]
    return cat


@router.post("/consolidate")
async def trigger_consolidation(request: Request) -> dict:
    from pep.core.consolidation import run_consolidation

    store = request.app.state.store
    llm = request.app.state.llm
    return run_consolidation(store, llm=llm)


def _serialize_trajectory_report(report) -> dict:
    return {
        "n_memories_total": report.n_memories_total,
        "n_memories_with_trajectory": report.n_memories_with_trajectory,
        "correlation": report.correlation,
        "correlation_n": report.correlation_n,
        "mean_trajectory": report.mean_trajectory,
        "mean_activation_count": report.mean_activation_count,
        "source_filter": getattr(report, "source_filter", None),
        "top_predicted": report.top_predicted,
        "top_actually_used": report.top_actually_used,
        "notes": report.notes,
    }


@router.get("/trajectory-validate")
async def trajectory_validate(request: Request, source: str | None = None) -> dict:
    """Run the trajectory validation experiment against the live store.

    Optional `source` query param: "llm" or "heuristic" to filter to
    memories scored by that path only. Returns a dict with the Spearman ρ
    between each memory's stored trajectory_at_storage value and its
    actual activation_count. Read-only.
    """
    from pep.analysis.trajectory_validation import (
        format_report,
        validate_trajectory_predictions,
    )

    store = request.app.state.store
    report = validate_trajectory_predictions(store, source=source)
    out = _serialize_trajectory_report(report)
    out["text"] = format_report(report)
    return out


@router.get("/trajectory-compare")
async def trajectory_compare(request: Request) -> dict:
    """§8.1 follow-up: compare LLM-scored memories against heuristic-scored
    memories side by side. Returns three sub-reports: all, llm-only,
    heuristic-only. The hypothesis is that LLM-driven scoring should
    correlate with reactivation better than the heuristic does.
    """
    from pep.analysis.trajectory_validation import compare_trajectory_sources

    store = request.app.state.store
    reports = compare_trajectory_sources(store)
    return {
        "all": _serialize_trajectory_report(reports["all"]),
        "llm": _serialize_trajectory_report(reports["llm"]),
        "heuristic": _serialize_trajectory_report(reports["heuristic"]),
    }


@router.get("/dialogue/coherence")
async def dialogue_coherence(request: Request, query: str = "") -> dict:
    """Per-agent + combined coherence on whatever dialogue agents exist.

    Picks up every session whose id starts with `dialogue:` from the live
    store, runs the multi-scale coherence experiment per session, then
    once more across the union. Works for any agent count (2..N).
    """
    if not query:
        raise HTTPException(status_code=400, detail="query parameter is required")

    from pep.analysis.coherence import compare_per_agent_coherence

    store = request.app.state.store
    embedder = request.app.state.embedder

    # Pull all dialogue session ids that have at least one memory
    all_mems = store.all_memories()
    sessions = sorted({
        m.session_id for m in all_mems
        if m.session_id and m.session_id.startswith("dialogue:")
    })
    if not sessions:
        return {"_combined": {"n_memories": 0, "n_categories": 0,
                              "n_memories_in_categories": 0,
                              "coherence_mean": 0.0, "coherence_max": 0.0,
                              "notes": "no dialogue sessions found"}}

    return compare_per_agent_coherence(store, embedder, query, sessions=sessions)


@router.get("/coherence")
async def coherence(request: Request, query: str = "", top: int = 8) -> dict:
    """Run the multi-scale coherence experiment against the live store.

    Read-only — does not mutate the store. Returns the full report as JSON
    plus a pre-rendered text version that the UI can paste into a <pre>.
    """
    if not query:
        raise HTTPException(status_code=400, detail="query parameter is required")

    from pep.analysis.coherence import format_report, measure_coherence

    store = request.app.state.store
    embedder = request.app.state.embedder
    report = measure_coherence(store, embedder, query)
    return {
        "query": report.query,
        "n_memories": report.n_memories,
        "n_categories": report.n_categories,
        "n_memories_in_categories": report.n_memories_in_categories,
        "coherence_mean": report.coherence_mean,
        "coherence_max": report.coherence_max,
        "memory_scores": report.memory_scores,
        "category_mean_scores": report.category_mean_scores,
        "category_max_scores": report.category_max_scores,
        "notes": report.notes,
        "text": format_report(report, top_n=top),
    }


@router.post("/bench")
async def run_benchmark_endpoint(request: Request) -> dict:
    """Run a benchmark. POST body: {"benchmark": "ambiguity", "policy": "all"}"""
    from pep.evaluator import compare_policies
    from pep.policies.pep_full import PEPFullPolicy
    from pep.policies.recent_window import RecentWindowPolicy
    from pep.policies.semantic_topk import SemanticTopKPolicy
    from pep.runner import run_benchmark

    body = await request.json()
    benchmark_name = body.get("benchmark", "ambiguity")
    policy_name = body.get("policy", "all")

    POLICIES = {
        "recent_window": RecentWindowPolicy(),
        "semantic_topk": SemanticTopKPolicy(),
        "pep_full": PEPFullPolicy(),
    }
    if policy_name == "all":
        chosen = list(POLICIES.values())
    elif policy_name in POLICIES:
        chosen = [POLICIES[policy_name]]
    else:
        raise HTTPException(status_code=400, detail=f"unknown policy: {policy_name}")

    embedder = request.app.state.embedder
    llm = request.app.state.llm

    all_results = {}
    for p in chosen:
        results = run_benchmark(benchmark_name, policy=p, llm=llm, embedder=embedder)
        all_results[p.name] = results

    comparison = compare_policies(all_results)
    return {"comparison": comparison, "raw_results": all_results}


@router.post("/dictionary/ingest")
async def dictionary_ingest(request: Request) -> dict:
    """Ingest a dictionary into a named session.

    POST body: {"text": "...", "language": "english", "session_id": "dictionary:english"}
    The text format is `word: definition` per line. Each headword becomes a
    memory; words appearing in each other's definitions become linked.
    """
    from pep.dictionary import ingest_dictionary

    body = await request.json()
    text = body.get("text", "")
    language = body.get("language", "english")
    session_id = body.get("session_id", f"dictionary:{language}")

    store = request.app.state.store
    return ingest_dictionary(
        store, text=text, session_id=session_id, language=language,
    )


@router.get("/dictionary/compare")
async def dictionary_compare(
    request: Request,
    session_a: str = "dictionary:english",
    session_b: str = "dictionary:spanish",
) -> dict:
    """Compare two ingested dictionaries.

    Returns shared headwords, structural divergence on the shared ones,
    and cross-definition tag matches between non-shared words.
    """
    from pep.dictionary import compare_dictionaries

    store = request.app.state.store
    return compare_dictionaries(
        store, session_a=session_a, session_b=session_b,
    )


@router.post("/ingest")
async def ingest_text(request: Request) -> dict:
    """Ingest raw text as memory paragraphs. POST body: {"text": "...", "session_id": "..."}"""
    from pep.schemas.memory_schema import MemoryObject

    body = await request.json()
    text = body.get("text", "")
    session_id = body.get("session_id", "default")
    store = request.app.state.store

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    count = 0
    for para in paragraphs:
        tags: list[str] = []
        seen: set[str] = set()
        for word in para.split():
            cleaned = "".join(c for c in word.lower() if c.isalnum())
            if len(cleaned) > 3 and cleaned not in seen:
                seen.add(cleaned)
                tags.append(cleaned)
            if len(tags) >= 12:
                break
        m = MemoryObject(
            core=para,
            faces={"semantic": para[:300]},
            fold_weights={"semantic": 1.0},
            tags=tags,
            brightness=0.5,
            session_id=session_id,
            source_type="document",
        )
        store.upsert_memory(m)
        count += 1

    return {"ingested": count, "session_id": session_id}
