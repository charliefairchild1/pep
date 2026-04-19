"""Axona Haze Slope — pre-clinical D_rec → D_irr detection.

Operational hypothesis: the earliest measurable signal of neurodegenerative
graph damage is an accelerating rate at which recoverable forgetting
(D_rec) becomes irrecoverable (D_irr). In a healthy graph, anchor
neighbors sustain each other: a hazed node stays reconstructible because
its neighbors are above threshold. When pathology starts taking anchor
neighbors out faster than reinforcement replaces them, D_rec nodes start
falling past the reconstruction horizon.

This module implements the minimum operational form of that detector:

  1. An `EpisodicNode` mirrors the opacity / half-life / reinforce model
     used by `pep.vectora.document.Document`, plus an explicit list of
     `anchors` — the neighbors that would have to be alive for
     reconstruction to succeed.

  2. `classify(node, ...)` returns 'alive' | 'D_rec' | 'D_irr'.

  3. `SlopeSnapshot` summarizes the graph at a point in time, including
     the 7-day transition rate (D_rec → D_irr per day, normalized).

  4. `detect_alerts(snap, baseline)` z-scores the transition rate against
     the user's own baseline — the pre-clinical signal is personal, not
     absolute.

Everything runs on heuristics and exponential decay — no model calls.
Thresholds are explicit and tunable; no coefficient is hidden.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field


# ─── Node model (mirrors vectora.Document for episodic memory) ────────────

@dataclass
class EpisodicNode:
    """Episodic-memory node with opacity, half-life, and reconstruction anchors."""
    id: str
    label: str = ""
    opacity: float = 1.0
    opacity_floor: float = 0.0
    last_reinforced_ts: float = 0.0
    half_life_s: float = 86400 * 30         # 30-day default for episodic
    anchors: list[str] = field(default_factory=list)

    def effective_opacity(self, now_ts: float) -> float:
        elapsed = max(0.0, now_ts - self.last_reinforced_ts)
        decayed = self.opacity * (0.5 ** (elapsed / self.half_life_s))
        return max(self.opacity_floor, decayed)

    def reinforce(self, now_ts: float, amount: float = 0.4) -> None:
        self.opacity = min(1.0, self.effective_opacity(now_ts) + amount)
        self.last_reinforced_ts = now_ts


# ─── Classification ───────────────────────────────────────────────────────

def classify(
    node: EpisodicNode,
    graph: dict[str, EpisodicNode],
    now_ts: float,
    threshold: float = 0.2,
    k: int = 2,
) -> str:
    """One of 'alive' | 'D_rec' | 'D_irr'.

    - alive : effective opacity ≥ threshold
    - D_rec : below threshold, but ≥ k anchor neighbors are alive
    - D_irr : below threshold, and fewer than k anchors alive
    """
    op = node.effective_opacity(now_ts)
    if op >= threshold:
        return "alive"
    alive_anchors = sum(
        1 for aid in node.anchors
        if aid in graph and graph[aid].effective_opacity(now_ts) >= threshold
    )
    return "D_rec" if alive_anchors >= k else "D_irr"


def anchor_support(node: EpisodicNode, graph: dict[str, EpisodicNode], now_ts: float, threshold: float) -> int:
    return sum(
        1 for aid in node.anchors
        if aid in graph and graph[aid].effective_opacity(now_ts) >= threshold
    )


# ─── Snapshot + slope ─────────────────────────────────────────────────────

@dataclass
class SlopeSnapshot:
    ts: float
    total_nodes: int
    alive: int
    d_rec: int
    d_irr: int
    transition_rate_7d: float          # D_rec → D_irr / total / day, last 7d
    mean_anchor_support: float         # avg alive-anchor count across non-alive nodes
    irr_share: float                   # d_irr / total


def snapshot(
    graph: dict[str, EpisodicNode],
    now_ts: float,
    threshold: float = 0.2,
    k: int = 2,
    prior_snapshots: list[SlopeSnapshot] | None = None,
) -> SlopeSnapshot:
    """Classify every node and compute the 7-day D_rec→D_irr transition rate."""
    alive = d_rec = d_irr = 0
    anchor_counts: list[int] = []
    for n in graph.values():
        c = classify(n, graph, now_ts, threshold, k)
        if c == "alive":
            alive += 1
        elif c == "D_rec":
            d_rec += 1
            anchor_counts.append(anchor_support(n, graph, now_ts, threshold))
        else:
            d_irr += 1
            anchor_counts.append(anchor_support(n, graph, now_ts, threshold))
    total = len(graph) or 1

    # Compute transition rate as the change in d_irr fraction per day,
    # averaged over the last 7 days of snapshots. If history is thin,
    # fall back to the instantaneous irr_share / half-life approximation.
    rate = 0.0
    irr_share_now = d_irr / total
    if prior_snapshots:
        week_ago = now_ts - 7 * 86400
        recent = [s for s in prior_snapshots if s.ts >= week_ago]
        if recent:
            oldest = min(recent, key=lambda s: s.ts)
            dt_days = max(0.5, (now_ts - oldest.ts) / 86400)
            d_share = irr_share_now - (oldest.d_irr / max(1, oldest.total_nodes))
            rate = max(0.0, d_share / dt_days)
    return SlopeSnapshot(
        ts=now_ts,
        total_nodes=total,
        alive=alive,
        d_rec=d_rec,
        d_irr=d_irr,
        transition_rate_7d=rate,
        mean_anchor_support=(sum(anchor_counts) / len(anchor_counts)) if anchor_counts else 0.0,
        irr_share=irr_share_now,
    )


# ─── Baseline + alerts ────────────────────────────────────────────────────

@dataclass
class HazeSlopeBaseline:
    """Per-user personal baseline for transition rate.

    Defaults are healthy-adult approximations used when history is thin.
    Real use: update these from rolling 60-day history of SlopeSnapshots.
    """
    mean_transition_rate: float = 0.002    # ~0.2% of graph / day at steady state
    std_transition_rate: float = 0.0015
    mean_anchor_support: float = 3.0
    days_observed: int = 0


@dataclass
class HazeSlopeAlert:
    level: str           # 'info' | 'watch' | 'act'
    code: str
    message: str
    recommendation: str = ""


def detect_alerts(snap: SlopeSnapshot, baseline: HazeSlopeBaseline) -> list[HazeSlopeAlert]:
    alerts: list[HazeSlopeAlert] = []

    # Primary signal: transition-rate z-score against personal baseline.
    z = (snap.transition_rate_7d - baseline.mean_transition_rate) / (baseline.std_transition_rate + 1e-9)

    if z > 2.5:
        alerts.append(HazeSlopeAlert(
            level="act",
            code="accelerating_irreversible_loss",
            message=f"D_rec→D_irr rate {z:+.1f}σ above personal baseline",
            recommendation="pre-clinical signal — schedule cognitive screening; review sleep, hearing, cardiovascular",
        ))
    elif z > 1.5:
        alerts.append(HazeSlopeAlert(
            level="watch",
            code="elevated_irreversible_loss",
            message=f"D_rec→D_irr rate {z:+.1f}σ above personal baseline",
            recommendation="increase targeted rehearsal of under-reinforced clusters; protect sleep",
        ))

    # Anchor-thinning is a second-order signal — the graph is losing redundancy
    # even if the transition rate hasn't caught up yet.
    if snap.mean_anchor_support < max(1.0, baseline.mean_anchor_support - 1.0):
        alerts.append(HazeSlopeAlert(
            level="watch",
            code="anchor_thinning",
            message=f"mean anchor support {snap.mean_anchor_support:.1f} (baseline {baseline.mean_anchor_support:.1f})",
            recommendation="reconstruction paths are thinning — expand topic breadth, social engagement",
        ))

    # Absolute-scale sanity floor: if D_irr has become a large fraction of
    # the graph at all, that's a clinical-range signal regardless of baseline.
    if snap.irr_share > 0.35:
        alerts.append(HazeSlopeAlert(
            level="act",
            code="clinical_irr_share",
            message=f"{snap.irr_share:.0%} of graph in D_irr state",
            recommendation="compensation-mode: external reconstruction scaffolding (see clinic / prosthetic)",
        ))

    return alerts


# ─── Simulation (for playground demos + self-test) ────────────────────────

def build_toy_graph(
    n_nodes: int = 60,
    clusters: int = 6,
    anchors_per_node: int = 4,
    age_days_spread: int = 180,
    now_ts: float = 0.0,
    seed: int = 1,
) -> dict[str, EpisodicNode]:
    """Generate a clustered episodic graph with varied ages.

    Nodes inside a cluster preferentially anchor to each other; a small
    fraction of anchors cross clusters. This is the topology cognitive
    reserve lives in: cross-cluster anchors are the ones that keep D_rec
    reconstructible when a local cluster degrades.
    """
    rng = random.Random(seed)
    nodes: dict[str, EpisodicNode] = {}
    ids_by_cluster: list[list[str]] = [[] for _ in range(clusters)]
    per = n_nodes // clusters
    for c in range(clusters):
        for i in range(per):
            nid = f"c{c}n{i}"
            age_s = rng.uniform(0, age_days_spread) * 86400
            nodes[nid] = EpisodicNode(
                id=nid,
                label=f"cluster {c} · node {i}",
                opacity=1.0,
                last_reinforced_ts=now_ts - age_s,
                half_life_s=86400 * rng.uniform(20, 45),
                anchors=[],
            )
            ids_by_cluster[c].append(nid)
    for c in range(clusters):
        ids = ids_by_cluster[c]
        for nid in ids:
            pool_in = [x for x in ids if x != nid]
            in_anchors = rng.sample(pool_in, k=min(len(pool_in), anchors_per_node - 1))
            other = rng.randrange(clusters)
            while other == c and clusters > 1:
                other = rng.randrange(clusters)
            cross = [rng.choice(ids_by_cluster[other])] if ids_by_cluster[other] else []
            nodes[nid].anchors = in_anchors + cross
    return nodes


def simulate_damage(
    graph: dict[str, EpisodicNode],
    now_ts: float,
    mode: str = "healthy",
) -> None:
    """In-place simulated pathology. 'healthy' is a no-op.

    - healthy : no damage, baseline aging only
    - aging   : slight global half-life reduction (10%)
    - pre_clinical : shorten half-life by 30% in two clusters; mild global 10%
    - clinical : shorten half-life by 60% in three clusters; global 20%
    """
    if mode == "healthy":
        return
    affected_ids: set[str] = set()
    clusters = sorted({n.id.split("n")[0] for n in graph.values()})
    if mode == "aging":
        for n in graph.values():
            n.half_life_s *= 0.9
        return
    if mode == "pre_clinical":
        targets = clusters[:2]
        factor_local, factor_global = 0.7, 0.9
    elif mode == "clinical":
        targets = clusters[:3]
        factor_local, factor_global = 0.4, 0.8
    else:
        return
    for n in graph.values():
        n.half_life_s *= factor_global
        if any(n.id.startswith(t + "n") for t in targets):
            n.half_life_s *= (factor_local / factor_global)
            affected_ids.add(n.id)


def assess(graph: dict[str, EpisodicNode], now_ts: float, baseline: HazeSlopeBaseline | None = None,
           threshold: float = 0.2, k: int = 2) -> dict:
    """End-to-end: graph + baseline → snapshot + alerts dict."""
    baseline = baseline or HazeSlopeBaseline()
    snap = snapshot(graph, now_ts, threshold, k)
    alerts = detect_alerts(snap, baseline)
    return {
        "snapshot": {
            "total_nodes": snap.total_nodes,
            "alive": snap.alive,
            "d_rec": snap.d_rec,
            "d_irr": snap.d_irr,
            "irr_share": round(snap.irr_share, 4),
            "transition_rate_7d": round(snap.transition_rate_7d, 6),
            "mean_anchor_support": round(snap.mean_anchor_support, 3),
        },
        "baseline": {
            "mean_transition_rate": baseline.mean_transition_rate,
            "std_transition_rate": baseline.std_transition_rate,
        },
        "alerts": [{"level": a.level, "code": a.code, "message": a.message, "recommendation": a.recommendation} for a in alerts],
    }


# Preset scenarios for the playground. Each returns a (graph, baseline).
def sample_scenario(kind: str, now_ts: float) -> tuple[dict[str, EpisodicNode], HazeSlopeBaseline]:
    g = build_toy_graph(now_ts=now_ts, seed={"healthy": 1, "aging": 2, "pre_clinical": 3, "clinical": 4}.get(kind, 1))
    simulate_damage(g, now_ts, kind)
    return g, HazeSlopeBaseline()
