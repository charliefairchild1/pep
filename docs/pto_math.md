# PTO — the math spine

Companion to `docs/pto.md`. Prose there; precision here.

PTO stands for **Potential → Transformation → Output**. It is a process-shape claim about what kinds of systems persist, not an acronym for a slogan. "PTO is mainly math" is false. PTO is a systems principle with four layers:

1. **Ontological claim** — what kinds of systems persist and spread. Stated in prose (`docs/pto.md`).
2. **Axiomatic framing** — primitive terms and a priori structure. §2 below.
3. **Mathematical optimality** — the trajectory functional. §8.
4. **Engineering design rules** — measurable goals and gating questions. `docs/pto.md` + every LAVAS sibling.

This document formalizes layers 2–3. It is a spine, not a proof: the axioms are *stipulated* (they characterize the class of systems PTO applies to); the claim that PTO-optimal systems dominate their environments is an empirical claim supported by the lineage in §10, not derived here.

---

## 1. Scope

**PTO claims:**

- Systems differ in how effectively they convert available potential into durable, future-enabling structure.
- This effectiveness is formalizable as a trajectory-level objective, not a per-step reward.
- Systems scoring higher on that objective tend to persist longer in their environments, across substrates.

**PTO does not claim:**

- That the universe has intent, purpose, or teleology.
- That all systems are PTO-optimizers. Only that persistence correlates with PTO score across the ensemble.
- That PTO-optimal is ethically good. The framework is substrate-agnostic; a powerful bioweapon can be PTO-optimal.
- That PTO subsumes thermodynamics, evolution, free-energy-minimization, or control theory. It frames them under a shared objective. See §10.
- That horizon `H` is universal. Each system has its own local-reward window `τ_local` and persistence-relevant horizon `τ_persist`. PTO's optimality claim is over `H > τ_local`. At `H → 0`, PTO collapses to reward-maximization.
- That `β` (capacity-investment weight) or `H` are *discovered* by systems. They are implicit properties, measurable from behavior.

**Substrate-agnostic.** Physical, biological, cognitive, economic, and computational systems all admit PTO interpretations when `(X, U, f, μ)` — state space, admissible controls, dynamics, utility measure — exist. See A8.

---

## 2. Axioms

Eight axioms characterize the class of systems PTO applies to. Each does independent work; none is a restatement of another.

**A1 — Transformation primacy.** A system's state change is describable by a rate `T` acting on available potential `P`, distinct from both gross activity and net output.

**A2 — Dissipation floor.** Every transformation incurs positive total dissipation `D > 0`. No transformation is free.

**A3 — Asymmetric dissipation.** `D = D_irr + D_rec` where `D_irr` is information-theoretically irreversible and `D_rec` is recoverable from surrounding state. Only `D_irr` strictly reduces future capacity.

**A4 — Capacity exists, non-circularly.** There exists a scalar `C(x, t)` measuring future transformability, definable independently of any future value of `T`. Circular definitions (`C := E[∫T]`) are rejected.

**A5 — Constructive decomposition.** `T` admits the form

```
T(t) = α·O(t) + β·(dC/dt) + Σ_k w_k · Δq_k(t)
```

where `O` is immediate output, `dC/dt` is capacity-shaping, `Δq_k` are per-dimension constructive gains, and `α, β, w_k ≥ 0`.

**A6 — Horizon primacy.** Optimality is defined over a horizon `H > τ_local`. PTO makes no claim about sub-`τ_local` optimization; at short horizons, PTO and reward-maximization coincide.

**A7 — Trajectory selection.** Among admissible policies `u(·)`, persistence favors those maximizing

```
J_H[u] = E[ ∫_t^{t+H} ( T − λ · D_irr ) dτ | x(t) ]
```

"Favors" is empirical: higher `J_H` correlates with higher persistence probability across the ensemble of systems sharing a substrate.

**A8 — Domain closure.** The framework applies wherever `(X, U, f, μ)` exist. No substrate is privileged — physical, biological, cognitive, or computational systems all qualify.

---

## 3. Derivable propositions

From A1–A8:

**P1 — Reward-maximizers are PTO-suboptimal at sufficient horizon.** A policy maximizing `∫_t^{t+H'} O dτ` for `H' < τ_persist` degrades `J_H` for `H > H'`. (A5, A6, A7.)

**P2 — Equal-dissipation accounting is sub-optimal.** A policy penalizing total `D` equally mis-values reversible compression and under-uses haze. (A3, A7.)

**P3 — Output-only systems have β = 0.** Setting `β = 0` in A5 collapses PTO to reward-maximization. This is a degenerate case of PTO, not an alternative. (A5.)

**P4 — Two systems with identical `O` can have different `J_H`.** If their `(dC/dt, Δq_k)` differ, `J_H` differs. Output alone is not diagnostic. (A5, A7.)

**P5 — Horizon miscalibration produces apparent reward-maximization.** A PTO system evaluated at `H_observed < H_true` appears to under-perform. Its capacity investments look like waste to a short-horizon observer. (A6, A7.)

**P6 — `D_rec` can silently migrate to `D_irr`.** If the context supporting reconstruction is itself hazed, `D_rec` becomes `D_irr` without the system noticing. This motivates PEP's drift-tracking module. (A3.)

**P7 — Substrate-independence is a corollary of A8.** Any two systems satisfying A1–A7 over isomorphic `(X, U, f, μ)` have the same PTO score regardless of physical substrate.

---

## 4. State, dynamics, primitives

Let a system occupy state `x(t) ∈ X` under control `u(t) ∈ U` and environment `e(t)`. Dynamics:

```
ẋ = f(x, u, e, t)
```

PTO names three quantities on this trajectory:

- **Potential** `P(x, e, t)` — available gradients, resources, signals, or opportunities. What *could* be transformed.
- **Transformation** rate `T(x, u, e, t)` — the rate of constructive work on `P`.
- **Output** `O(x, u, e, t)` — the realized immediate effect: action taken, artifact produced, information emitted.

These are the P, T, and O in the name. Nouns in a pipeline, not variables in a single equation.

---

## 5. Dissipation and the asymmetry

All transformation costs. Let `D(x, u, e, t) > 0` be total expenditure per unit time. A3 splits this:

```
D(t) = D_irr(t) + D_rec(t)
```

- `D_irr` — irreversible: heat, semantic collapse, information-theoretically lost detail, hallucination, contradiction, brittleness.
- `D_rec` — recoverable: structure temporarily below reuse threshold but reconstructible from context. PEP's *haze* primitive is this.

Haze is not waste; it is capacity under compression. A system treating all forgetting as loss either hoards (retrieval drag explodes) or panic-prunes (irreversible loss of things it later needs). The split is how PEP avoids both.

---

## 6. Capacity, non-circularly

`C(x, t)` measures the system's future ability to keep transforming. The tempting definition — "expected future `T`" — is circular because `T` itself depends on `dC/dt`.

Two non-circular candidates:

**(a) Reachable-utility volume.** Let `R_H(x)` be the set of states reachable from `x` within horizon `H` under admissible controls, and `μ` a domain utility measure on states. Then

```
C(x, t) = ∫_{R_H(x)} μ(y) dy
```

Capacity is the measure of useful futures the system keeps open. Close to *empowerment* in the Klyubin/Polani sense.

**(b) Predictive mutual information.** For systems whose output depends on internal models,

```
C(x, t) = I( past ; future | x(t) )
```

the information the current state retains about the past that is relevant to the future. Bialek/Still's *predictive information*. Anchored in information theory, not in future `T`.

Either satisfies A4. PEP's haze + memory-store maps most cleanly onto (b); Vectora's retrieval graph maps onto (a).

---

## 7. Constructive transformation, decomposed

Per A5, `T` has an operational form. The constructive-vs-dissipative dimensions from `docs/pto.md` become a weighted decomposition:

```
T(t) = α·O(t) + β·(dC/dt) + Σ_k w_k · Δq_k(t)
```

where `Δq_k` are per-dimension gains:

- `Δq_pred` — predictive accuracy gained
- `Δq_amb` — ambiguity reduced (sign-flipped from error)
- `Δq_ret` — retrieval precision gained
- `Δq_cmp` — compression quality gained (size down, reconstruction preserved)
- `Δq_coh` — internal coherence gained
- `Δq_adp` — adaptability to novelty gained

Weights `w_k` are domain-specific. Vectora weights `Δq_ret` and `Δq_cmp`; Axona weights `Δq_coh` and `Δq_adp`. The `β·(dC/dt)` term is the *future-enabling* channel — a system can have small `O` and large `dC/dt` and still be transformation-optimal.

---

## 8. The optimality claim

Per A7, for horizon `H` and policy `u(·)`:

```
max_u  J_H[u] = E[ ∫_t^{t+H} ( T(x, u, e, τ) − λ · D_irr(x, u, e, τ) ) dτ | x(t) ]
```

Three properties of this form:

1. **Horizon `H` extends past the immediate reward window.** A system optimizing turn-N response is not doing PTO. A system optimizing turn-N+50 is.
2. **Only `D_irr` is penalized.** `D_rec` (haze) is neutral. Forgetting something recoverable is not a cost — it is compression.
3. **`T` includes `dC/dt`**, so investments in future capacity are first-class. The system is rewarded for shaping the next state to be more transformative, not only for emitting output now.

Equivalent ratio form:

```
F(t) = T(x, u, e, t) / max(D_irr(x, u, e, t), ε)
```

with `max ∫ F dt`. The penalized form is easier to optimize; the ratio form is easier to explain.

### What this form is *not*

- Not `max O` — that is a reward-maximizer; PTO rejects it (P1, P3).
- Not `max (O − λD)` — standard regularized control; ignores `dC/dt` and the `D_irr/D_rec` split (P2, P3).
- Not `max E[∫T | x]` — circular; A4 rejects it.

The penalized, horizoned, split-dissipation form is the minimum that captures PTO's actual content.

---

## 9. Worked examples

### Example 1 — a cell

- `P`: chemical gradients across the membrane.
- `O`: motility, signaling, waste export.
- `C`: ability to keep maintaining integrity (homeostasis) and reproduce (lineage).
- `D_irr`: heat loss, irreversible damage to membranes and DNA.
- `D_rec`: metabolites in temporary imbalance, reversible under re-equilibration.
- Cells that push all transformation into `O` (runaway metabolism) die. Cells investing in `dC/dt` (membrane repair, DNA maintenance, stress response) persist.
- Lineage: natural selection is A7 made mechanism.

### Example 2 — a memory system deciding to store vs forget

- `P`: incoming event stream.
- `O`: immediate retrieval queries served.
- `C`: graph structure + haze profile + predictive model of future queries.
- `D_irr`: overwritten-and-unreconstructible nodes, lost distinctions.
- `D_rec`: hazed nodes still reconstructible from context. **Expected to haze over time; that is the design.**
- A system with `β = 0` stores everything → retrieval drag grows, eventually exceeds query rate, `J_H` collapses.
- A system with well-tuned `β` hazes aggressively, tracks drift, keeps reconstruction paths alive. `J_H` stable over arbitrary `H`.

### Example 3 — a trading agent

- `P`: market microstructure, order flow, information asymmetry.
- `O`: P&L per trade.
- `C`: regime classification, counterparty models, residual scorers that still work under distribution shift.
- `D_irr`: model collapse, regime-change losses, reputation damage.
- `D_rec`: stale signals that can be re-derived from updated data.
- Short-horizon reward-maximizers blow up in regime shifts — they have `β = 0` and cannot adapt. Long-horizon PTO agents continuously invest in `dC/dt` through model updating.

---

## 10. Lineage and adjacent frameworks

| Framework | Covers | Misses | Key difference |
|---|---|---|---|
| Second law of thermodynamics | A2 | A1, A4–A7 | No future capacity, no optimality claim |
| Prigogine dissipative structures | A2, A5 hints | A4, A6 explicit | Describes; doesn't prescribe |
| Natural selection | A7 for biological | A1, A4 formally | Mechanism, not principle |
| Free-energy principle (Friston) | `Δq_pred`, `Δq_amb` | A3 split, A6 horizon | All loss treated equal |
| Empowerment (Klyubin/Polani) | A4 via reachable states | A5, A7 | No output channel |
| Predictive information (Bialek/Still) | A4 via `I(past;future)` | Control, output | Descriptive not prescriptive |
| LQR / MPC control | A7 penalized form | A3, A5 dimensions | Scalar cost, no capacity term |
| Bounded rationality (Simon) | A6 in spirit | Formalism | Satisficing, not optimality |
| Algorithmic info theory | A4 via K-complexity | A6, A7 | No dynamics |
| Multi-objective RL | A5 flavor | A3, A4 non-circularity | Fixed reward function |

PTO picks A4 candidates from the right column and pairs them with A7's trajectory objective. It claims less than any single framework in its own domain and more across domains.

---

## 11. Mapping to PEP

| PEP module | PTO role | What it computes |
|---|---|---|
| Predictor | `Δq_pred`, `Δq_amb` | forecast, residual → learning signal |
| Residual scorer | weights on `Δq_k` | decides what enters `dC/dt` |
| Reactivator (spreading activation) | pulls `C` into `T` | low-resistance path from need to capacity |
| State modulator | domain weights on `w_k` | biases which dimensions count now |
| Haze / opacity | `D_rec` vs `D_irr` split | enforces compression without irreversibility |
| Multi-face memory | recoverability of `C` | preserves reconstruction paths |
| Drift tracking | honesty about P6 | flags when `D_rec` became `D_irr` |
| Evaluator | `J_H[u]` | scores trajectory quality, not per-turn accuracy |

Every PEP module is doing one of: (i) measuring `T`, (ii) preserving `C`, (iii) distinguishing `D_irr` from `D_rec`, or (iv) extending the optimization horizon `H`.

---

## 12. LAVAS specialization

| App | Dominant `w_k` | Primary `C` form |
|---|---|---|
| Vectora | `Δq_ret`, `Δq_cmp` | reachable-utility (graph) |
| Lingora | `Δq_cmp`, `Δq_coh` | predictive info (language model) |
| Atria | `Δq_pred` over compatibility | reachable-utility (match graph) |
| Axona | `Δq_coh`, `Δq_adp` | state-space volume |
| Strata | `Δq_amb`, `Δq_adp` | reachable-utility (regime space) |

---

## 13. Objections and replies

**"Capacity `C` is vague."** — Only if you decline to pick a definition. §6 gives two non-circular ones; commit to one per domain and capacity becomes measurable.

**"`β` is a free parameter."** — Yes. It encodes the system's investment policy. Systems don't discover their `β`; they have it, implicitly, and you can measure it from behavior.

**"The horizon `H` is a free parameter."** — Also yes. It encodes what persistence means for this system. An organism's `H` is its lifespan; a chat session's is turn count. Wrong `H` → you are not doing PTO.

**"This is multi-objective RL with a capacity bonus."** — Closer than thermodynamics or free energy, but no. RL optimizes a fixed reward function. PTO's `T` includes `dC/dt`, which itself depends on future `T` — PTO is about trajectory shape, not climbing a pre-specified reward surface. The `D_irr/D_rec` asymmetry (A3) is also outside RL's standard framing.

**"Isn't this teleology with equations?"** — No. PTO does not claim systems *try* to be PTO-optimal. It claims PTO-optimal systems persist, and persisters dominate the observable ensemble. Same logic as natural selection.

**"Why call the objective PTO, not fitness?"** — Fitness is reproductive success. PTO applies to non-biological systems (data structures, markets, language models) where reproduction is ill-defined but persistence is not.

**"Axioms A3 and A4 carry all the work."** — Partly true. They are the axioms that distinguish PTO from ordinary optimization. A3 introduces the dissipation asymmetry; A4 insists capacity exist without reference to future transformation. Remove either and PTO collapses into control theory or empowerment respectively.

**"The empirical claim in A7 is unfalsifiable — any persistent system will be labeled PTO-optimal post-hoc."** — Real objection. Operationalization requires: (i) fix `C`, `β`, `H` *before* measurement; (ii) compare `J_H` across systems in a shared ensemble; (iii) show persistence correlates with pre-registered `J_H`. Non-trivial but possible. See §14.

---

## 14. Open problems

1. **Calibrating `λ`.** The trade-off between transformation gain and irreversible loss is domain-specific and currently hand-set.
2. **Measuring `dC/dt` online.** Reachable-utility is exponentially expensive; predictive-info needs stable estimators. Both need approximations that survive real data.
3. **Horizon `H` selection.** Too short → reward-maximizer. Too long → paralysis, discounting noise. PEP uses session-level `H` heuristically.
4. **`D_rec`/`D_irr` detection.** P6 names the drift; the formal criterion for when `D_rec` has crossed into `D_irr` is unfinished.
5. **Cross-module weight consistency.** Each LAVAS app picks `w_k`. There is no proof that sibling weights compose coherently at the mesh level.
6. **Falsification protocol.** Per the last objection in §13: what concrete experiment would disprove A7? Best candidate so far: pre-register `J_H` on held-out ensembles of model variants, measure persistence (uptime, user retention, benchmark-longevity), check correlation.
7. **Relationship to thermodynamic bounds.** Landauer's limit says irreversible erasure has an energy floor. PTO's `D_irr` includes but exceeds this. The exact relationship is unresolved.

---

## 15. One-line formal statement

> **PTO.** A system with state `x`, control `u`, capacity `C`, and irreversible dissipation `D_irr` tends to evolve toward policies maximizing `E[ ∫_t^{t+H} ( T − λ·D_irr ) dτ ]` where `T = α·O + β·dC/dt + Σ w_k Δq_k`, for horizon `H` beyond the immediate output window, with recoverable loss `D_rec` held neutral and `C` defined non-circularly.

That is the spine. `docs/pto.md` is the prose. Everything in PEP is one of the terms above, made computable.
