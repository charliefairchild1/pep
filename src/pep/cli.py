"""PEP CLI: `pep serve`, `pep ingest`, `pep replay`."""

from __future__ import annotations

import json
from pathlib import Path

import click

from pep.embed import Embedder
from pep.memory.store import MemoryStore
from pep.schemas.memory_schema import MemoryObject


@click.group()
def main() -> None:
    """PEP — Predictive Encoding and Preparation."""


@main.command()
@click.option("--host", default="127.0.0.1")
@click.option("--port", default=8000, type=int)
@click.option("--reload", is_flag=True, default=False)
def serve(host: str, port: int, reload: bool) -> None:
    """Run the FastAPI server."""
    import uvicorn

    uvicorn.run("pep.main:app", host=host, port=port, reload=reload)


@main.command()
@click.argument("path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--session-id", default="default")
@click.option("--db", default=None, help="Path to PEP db (default: data/pep.db)")
def ingest(path: Path, session_id: str, db: str | None) -> None:
    """Ingest a text/markdown file as a set of memory objects (one per paragraph)."""
    store = MemoryStore(db or str(Path("data") / "pep.db"))
    text = path.read_text(encoding="utf-8")
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    count = 0
    for para in paragraphs:
        snippet = para[:300]
        m = MemoryObject(
            core=para,
            faces={"semantic": snippet},
            fold_weights={"semantic": 1.0},
            tags=_extract_tags(para),
            brightness=0.5,
            session_id=session_id,
            source_type="document",
        )
        store.upsert_memory(m)
        count += 1
    click.echo(f"ingested {count} memories from {path} into session={session_id}")


@main.command()
@click.option("--benchmark", "-b", required=True, help="Benchmark name (e.g. ambiguity)")
@click.option("--policy", "-p", default="all",
              help="Policy: recent_window | semantic_topk | pep_full | all")
def bench(benchmark: str, policy: str) -> None:
    """Run a benchmark and print the comparison table."""
    from pep.embed import Embedder
    from pep.evaluator import compare_policies, format_comparison
    from pep.models.llm_client import get_llm_client
    from pep.policies.pep_full import PEPFullPolicy
    from pep.policies.recent_window import RecentWindowPolicy
    from pep.policies.semantic_topk import SemanticTopKPolicy
    from pep.runner import run_benchmark

    POLICIES = {
        "recent_window": RecentWindowPolicy(),
        "semantic_topk": SemanticTopKPolicy(),
        "pep_full": PEPFullPolicy(),
    }
    if policy == "all":
        chosen = list(POLICIES.values())
    else:
        if policy not in POLICIES:
            click.echo(f"unknown policy: {policy}")
            raise SystemExit(1)
        chosen = [POLICIES[policy]]

    llm = get_llm_client()
    embedder = Embedder()
    click.echo(f"Running benchmark '{benchmark}' with {len(chosen)} polic{'y' if len(chosen)==1 else 'ies'}...")
    click.echo(f"  llm={llm.name} embeddings={'voyage' if embedder.using_real_embeddings else 'pseudo'}")
    click.echo()

    all_results = {}
    for p in chosen:
        click.echo(f"  → {p.name}...")
        results = run_benchmark(benchmark, policy=p, llm=llm, embedder=embedder)
        all_results[p.name] = results

    click.echo()
    comparison = compare_policies(all_results)
    click.echo(format_comparison(comparison))


@main.command()
@click.option("--turns", "-n", default=6, type=int, help="Number of agent turns")
@click.option("--opening", "-o", default="Hello — what's on your mind?", help="The first message")
@click.option("--personas", "-p", default="curious_and_expert",
              help="Persona pair: curious_and_expert | skeptic_and_advocate | builder_and_critic | two_researchers")
@click.option("--db", default=None, help="Path to PEP db (default: data/pep.db)")
def dialogue(turns: int, opening: str, personas: str, db: str | None) -> None:
    """Run two PEP agents in a dialogue. Each one has its own memory + state.

    Use a separate db file (the agents share one store with different session_ids).
    Each turn prints the speaker, the message, and a brief stat line.
    """
    from pep.dialogue import DEFAULT_PERSONAS, Agent, run_dialogue
    from pep.embed import Embedder
    from pep.models.llm_client import get_llm_client

    if personas not in DEFAULT_PERSONAS:
        click.echo(f"unknown persona pair: {personas}")
        click.echo(f"available: {', '.join(DEFAULT_PERSONAS.keys())}")
        raise SystemExit(1)

    persona_a, persona_b = DEFAULT_PERSONAS[personas]
    store = MemoryStore(db or str(Path("data") / "pep_dialogue.db"))
    embedder = Embedder()
    llm = get_llm_client()

    click.echo(f"Dialogue: {personas}  |  {turns} turns  |  llm={llm.name}")
    click.echo(f"Opening: {opening}")
    click.echo("-" * 70)

    a = Agent(name="Alice", persona=persona_a, store=store, embedder=embedder, llm=llm)
    b = Agent(name="Bob", persona=persona_b, store=store, embedder=embedder, llm=llm)

    transcript = run_dialogue(a, b, opening=opening, turns=turns)
    for record in transcript:
        click.echo(f"[{record.speaker}] (mem={record.memories_after})")
        click.echo(f"  {record.message}")
        click.echo()


@main.command()
@click.argument("question", nargs=-1, required=True)
@click.option("--session-id", "-s", default="cli", help="Session id (memory persists per session)")
@click.option("--db", default=None, help="Path to PEP db (default: data/pep.db)")
@click.option("--trace", is_flag=True, default=False, help="Print the PEP trace after the response")
def ask(question: tuple[str, ...], session_id: str, db: str | None, trace: bool) -> None:
    """One-shot question with full PEP overlay. Memory persists across calls.

    Example:
      pep ask "What is the capital of France?"
      pep ask "Tell me more about that"   # remembers the previous turn

    Use the same --session-id across calls to maintain memory continuity.
    Different session-ids give independent memory streams.
    """
    from pep.core.loop import run_turn
    from pep.embed import Embedder
    from pep.models.llm_client import get_llm_client
    from pep.schemas.input_schema import UserInput

    text = " ".join(question)
    store = MemoryStore(db or str(Path("data") / "pep.db"))
    embedder = Embedder()
    llm = get_llm_client()

    user_input = UserInput(text=text, session_id=session_id)
    packet, response, _, state_after = run_turn(
        user_input=user_input, store=store, embedder=embedder, llm=llm,
    )
    click.echo(response)

    if trace:
        click.echo()
        click.echo("─" * 60)
        click.echo(f"session: {session_id}  |  llm: {llm.name}")
        click.echo(f"intent: {packet.interpreted.task_type}  |  topic: {packet.interpreted.topic}")
        click.echo(f"memories activated: {len(packet.selected_memories)}  |  "
                   f"novelty: {packet.residual.novelty_score:.2f}  |  "
                   f"trajectory: {packet.residual.trajectory_score:.2f}")
        if packet.selected_memories:
            click.echo("activated:")
            for m in packet.selected_memories:
                click.echo(f"  {m['id']} ({m['face']}): {m['content'][:80]}")


@main.command(name="trajectory-validate")
@click.option("--db", default=None, help="Path to PEP db (default: data/pep.db)")
def trajectory_validate(db: str | None) -> None:
    """Validate the trajectory score against actual reactivation counts.

    Closes §8.1 of the research note: does the system's prediction of
    'will this matter for future turns?' actually correlate with which
    memories the Reactivator pulls in subsequent turns?
    """
    from pep.analysis.trajectory_validation import (
        format_report,
        validate_trajectory_predictions,
    )

    store = MemoryStore(db or str(Path("data") / "pep.db"))
    report = validate_trajectory_predictions(store)
    click.echo(format_report(report))


@main.command()
@click.option("--query", "-q", required=True, help="Query to score memories against")
@click.option("--db", default=None, help="Path to PEP db (default: data/pep.db)")
@click.option("--top", default=8, type=int, help="How many top memories/categories to print")
def coherence(query: str, db: str | None, top: int) -> None:
    """Run the multi-scale coherence experiment against the live store.

    Scores every memory against the query, aggregates per category, and
    reports the Spearman rank correlation between fine-scale (per-memory)
    and coarse-scale (per-category) relevance. High correlation means PEP's
    categories preserve meaningful structure across scales.
    """
    from pep.analysis.coherence import format_report, measure_coherence
    from pep.embed import Embedder

    store = MemoryStore(db or str(Path("data") / "pep.db"))
    embedder = Embedder()
    report = measure_coherence(store, embedder, query)
    click.echo(format_report(report, top_n=top))


@main.command()
@click.option("--db", default=None, help="Path to PEP db (default: data/pep.db)")
def consolidate(db: str | None) -> None:
    """Run the consolidation pass: dedup, prune, summarize, reconsolidate drifted memories, discover categories."""
    from pep.core.consolidation import run_consolidation
    from pep.models.llm_client import get_llm_client

    store = MemoryStore(db or str(Path("data") / "pep.db"))
    llm = get_llm_client()
    results = run_consolidation(store, llm=llm)
    click.echo("Consolidation complete:")
    for key, value in results.items():
        click.echo(f"  {key}: {value}")


@main.command()
@click.argument("run_id")
@click.option("--db", default=None)
def replay(run_id: str, db: str | None) -> None:
    """Show a previous run's full PEPPacket and response."""
    store = MemoryStore(db or str(Path("data") / "pep.db"))
    run = store.get_run(run_id)
    if not run:
        click.echo(f"run {run_id} not found")
        raise SystemExit(1)
    click.echo(json.dumps(run, indent=2, default=str))


def _extract_tags(text: str) -> list[str]:
    """Cheap tag extraction: lowercase content words >3 chars, capped at 12."""
    seen: set[str] = set()
    out: list[str] = []
    for word in text.split():
        cleaned = "".join(c for c in word.lower() if c.isalnum())
        if len(cleaned) > 3 and cleaned not in seen:
            seen.add(cleaned)
            out.append(cleaned)
        if len(out) >= 12:
            break
    return out


if __name__ == "__main__":
    main()
