"""§8.1 of the research note: does the trajectory score predict reactivation?

Every memory the Updater stores has a `trajectory_at_storage` value in its
`future_use` dict — the system's prediction of "will this matter for future
turns?". Every memory ALSO has an `activation_count` that increments every
time the Reactivator pulls it. We've never compared the two.

This module loads all memories that have a stored trajectory score, computes
the Spearman rank correlation between trajectory_at_storage and activation_count,
and returns a report. If the correlation is high, the trajectory scoring is
doing real predictive work. If it's near zero, it's just adding noise to the
storage gate.

Read-only — does not mutate the store.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from pep.analysis.coherence import spearman
from pep.memory.store import MemoryStore
from pep.schemas.memory_schema import MemoryObject


@dataclass
class TrajectoryValidationReport:
    n_memories_total: int
    n_memories_with_trajectory: int
    correlation: float          # Spearman ρ between trajectory and activation_count
    correlation_n: int          # number of (trajectory, count) pairs used
    mean_trajectory: float
    mean_activation_count: float
    source_filter: str | None = None  # "llm" / "heuristic" / None for all
    top_predicted: list[dict] = field(default_factory=list)
    top_actually_used: list[dict] = field(default_factory=list)
    notes: str = ""


def _trajectory_of(m: MemoryObject) -> float | None:
    """Pull the trajectory score from a memory's future_use field, or None."""
    fu = m.future_use or {}
    val = fu.get("trajectory_at_storage")
    if val is None:
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def validate_trajectory_predictions(
    store: MemoryStore,
    *,
    session_id: str | None = None,
    source: str | None = None,
    min_age_turns: int = 0,
) -> TrajectoryValidationReport:
    """Compute the correlation between predicted trajectory and actual reactivation.

    `source` filters to memories scored by a specific scorer ("llm" or
    "heuristic"). When set, only memories where `trajectory_source == source`
    are included in the calculation. Used by the §8.1 follow-up experiment
    to compare LLM-driven scoring against the heuristic.

    `min_age_turns` is a placeholder hook — currently every memory is
    included, but a richer version could filter to memories that have had
    "enough time" to be reactivated.

    Returns a TrajectoryValidationReport with the headline ρ and supporting
    detail (top-N memories by predicted vs actual usefulness).
    """
    memories = store.all_memories(session_id=session_id) if session_id else store.all_memories()
    n_total = len(memories)

    pairs: list[tuple[MemoryObject, float, int]] = []
    for m in memories:
        traj = _trajectory_of(m)
        if traj is None:
            continue
        if source is not None and m.trajectory_source != source:
            continue
        pairs.append((m, traj, m.activation_count or 0))

    n_with_traj = len(pairs)
    if n_with_traj < 2:
        return TrajectoryValidationReport(
            n_memories_total=n_total,
            n_memories_with_trajectory=n_with_traj,
            correlation=0.0,
            correlation_n=n_with_traj,
            mean_trajectory=0.0,
            mean_activation_count=0.0,
            notes=(
                f"need at least 2 memories with stored trajectory scores; "
                f"have {n_with_traj}. Run more turns and try again."
            ),
        )

    trajectories = [t for _, t, _ in pairs]
    counts = [c for _, _, c in pairs]
    correlation = spearman(trajectories, counts)

    # Top-5 by predicted trajectory
    pairs_by_traj = sorted(pairs, key=lambda p: p[1], reverse=True)[:5]
    top_predicted = [
        {
            "id": m.id,
            "predicted_trajectory": round(t, 4),
            "actual_count": c,
            "core": m.core[:80],
        }
        for m, t, c in pairs_by_traj
    ]

    # Top-5 by actual reactivation count
    pairs_by_count = sorted(pairs, key=lambda p: p[2], reverse=True)[:5]
    top_actually_used = [
        {
            "id": m.id,
            "predicted_trajectory": round(t, 4),
            "actual_count": c,
            "core": m.core[:80],
        }
        for m, t, c in pairs_by_count
    ]

    return TrajectoryValidationReport(
        n_memories_total=n_total,
        n_memories_with_trajectory=n_with_traj,
        correlation=correlation,
        correlation_n=n_with_traj,
        mean_trajectory=round(sum(trajectories) / n_with_traj, 4),
        mean_activation_count=round(sum(counts) / n_with_traj, 4),
        source_filter=source,
        top_predicted=top_predicted,
        top_actually_used=top_actually_used,
    )


def compare_trajectory_sources(
    store: MemoryStore,
    *,
    session_id: str | None = None,
) -> dict:
    """Run the validation experiment three times: LLM-only, heuristic-only,
    and combined. Used to answer §8.1's follow-up question:

      "Does the LLM-driven trajectory scorer correlate better with actual
      reactivation than the heuristic?"

    Returns a dict with three sub-reports the UI can render side by side.
    """
    return {
        "all": validate_trajectory_predictions(store, session_id=session_id),
        "llm": validate_trajectory_predictions(store, session_id=session_id, source="llm"),
        "heuristic": validate_trajectory_predictions(store, session_id=session_id, source="heuristic"),
    }


def format_report(report: TrajectoryValidationReport) -> str:
    """Render a TrajectoryValidationReport as a human-readable text block."""
    lines: list[str] = []
    lines.append("Trajectory score validation (research note §8.1)")
    lines.append("-" * 60)
    lines.append(f"Total memories in store: {report.n_memories_total}")
    lines.append(f"Memories with stored trajectory score: {report.n_memories_with_trajectory}")
    if report.notes:
        lines.append(f"Note: {report.notes}")
        return "\n".join(lines)

    lines.append("")
    lines.append(f"Mean predicted trajectory: {report.mean_trajectory:.3f}")
    lines.append(f"Mean actual activation count: {report.mean_activation_count:.3f}")
    lines.append("")
    lines.append(f"Spearman ρ (predicted vs actual): {report.correlation:+.3f}")
    lines.append("")
    lines.append("Interpretation:")
    lines.append("  +1.0 = the trajectory score perfectly predicts which memories get reactivated")
    lines.append("   0.0 = no relationship — trajectory scoring is not doing predictive work")
    lines.append("  -1.0 = it predicts the OPPOSITE of what gets reactivated (alarming)")
    lines.append("")

    if report.top_predicted:
        lines.append("Top 5 by predicted trajectory:")
        for item in report.top_predicted:
            lines.append(
                f"  pred={item['predicted_trajectory']:.2f}  actual={item['actual_count']}  "
                f"{item['id']}"
            )
        lines.append("")

    if report.top_actually_used:
        lines.append("Top 5 by actual reactivation count:")
        for item in report.top_actually_used:
            lines.append(
                f"  pred={item['predicted_trajectory']:.2f}  actual={item['actual_count']}  "
                f"{item['id']}"
            )

    return "\n".join(lines)
