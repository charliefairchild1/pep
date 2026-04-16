"""Vectora dogfood — Vectora actually powers retrieval for the other LAVAS apps.

Each sibling app (Atria, Axona, Lingora, Strata) gets a VectoraRetriever
seeded with canonical items for its domain: players, memories, words, assets.
Canvases in those apps call /vectora/neighbors/{app}/{seed} to fetch a real
Vectora neighborhood instead of generating one in-browser.

Singleton retrievers are lazily initialized on first request and cached in
the module namespace. This is the "internal dogfood play" that backs the
claim that Vectora is the retrieval layer the other LAVAS siblings consume.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from .document import Document
from .retrieval import RetrievalMode, VectoraRetriever


# ═══════════════════════════════════════════════════════════════════════
# Canonical seed data per app
# ═══════════════════════════════════════════════════════════════════════

ATRIA_PLAYERS: list[Document] = [
    Document(id="p01", text="aggressive tryhard rank grinder high skill tilt prone solo queue", metadata={"label": "Tryhard grinder", "tier": "diamond"}),
    Document(id="p02", text="chill casual evening player social friendly team-focused communication", metadata={"label": "Chill casual", "tier": "gold"}),
    Document(id="p03", text="support main patient strategic team player low tilt high communication", metadata={"label": "Support main", "tier": "platinum"}),
    Document(id="p04", text="aggressive duelist flashy plays high mechanics low patience solo queue", metadata={"label": "Flashy duelist", "tier": "diamond"}),
    Document(id="p05", text="new player learning fundamentals asks questions polite low skill", metadata={"label": "Learning newbie", "tier": "bronze"}),
    Document(id="p06", text="competitive climber ranked-focused serious mechanics coachable", metadata={"label": "Ranked climber", "tier": "platinum"}),
    Document(id="p07", text="toxic tilter recent flags flame teammates negative communication", metadata={"label": "Toxic tilter", "tier": "gold"}),
    Document(id="p08", text="team captain shotcalls organizes strategic patient high communication", metadata={"label": "Team captain", "tier": "diamond"}),
    Document(id="p09", text="chill social friendly casual weekend player no tilt", metadata={"label": "Weekend warrior", "tier": "silver"}),
    Document(id="p10", text="smurf alt account high skill low visible rank mechanical outlier", metadata={"label": "Smurf detected", "tier": "silver"}),
    Document(id="p11", text="flex queue support or tank patient team-oriented versatile", metadata={"label": "Flex player", "tier": "platinum"}),
    Document(id="p12", text="dps main mechanical aggressive self-centered solo queue only", metadata={"label": "DPS main", "tier": "diamond"}),
    Document(id="p13", text="returning player rusty experienced high skill ceiling low current form", metadata={"label": "Returning veteran", "tier": "platinum"}),
    Document(id="p14", text="first-time player tutorial fresh account exploring the game mechanics", metadata={"label": "First timer", "tier": "bronze"}),
    Document(id="p15", text="coach analyst high game-sense low mechanics strategic patient", metadata={"label": "Analyst type", "tier": "gold"}),
    Document(id="p16", text="aggressive flex capable of any role high mechanics some tilt", metadata={"label": "Aggressive flex", "tier": "diamond"}),
    Document(id="p17", text="supportive healer-main low ego patient teammate-focused", metadata={"label": "Healer main", "tier": "platinum"}),
    Document(id="p18", text="speed-running tempo player fast decisions high skill low patience", metadata={"label": "Tempo player", "tier": "diamond"}),
    Document(id="p19", text="party queue with friends casual group not tryhard", metadata={"label": "Party player", "tier": "gold"}),
    Document(id="p20", text="anti-pump specialist counters aggressive playstyles defensive game-sense", metadata={"label": "Anti-aggro", "tier": "platinum"}),
]


AXONA_MEMORIES: list[Document] = [
    Document(id="m01", text="vivid childhood birthday party laughter cake family photograph emotional"),
    Document(id="m02", text="anxious job interview forgot answer palms sweating embarrassment"),
    Document(id="m03", text="quiet focused flow state solving hard problem hours passed"),
    Document(id="m04", text="beach vacation warm sun ocean salt smell relaxation peace"),
    Document(id="m05", text="grief loss funeral cold hollow chest unable to speak"),
    Document(id="m06", text="first kiss nervous butterflies embarrassed happy teenage romance"),
    Document(id="m07", text="learning bike fell scraped knee father catching me balance moment"),
    Document(id="m08", text="final exam pressure studied all night adrenaline time running out"),
    Document(id="m09", text="spontaneous laughter joke friends inside reference connection"),
    Document(id="m10", text="waiting room medical test anxiety fluorescent lights antiseptic smell"),
    Document(id="m11", text="morning coffee quiet apartment bird song routine comfort"),
    Document(id="m12", text="meeting deadline rushed typing code compiling heart racing stress"),
    Document(id="m13", text="graduation ceremony pride parents applause accomplishment hopeful"),
    Document(id="m14", text="car accident adrenaline loud crash relief checking body shock"),
    Document(id="m15", text="deep meditation breath body scan still mind clarity calm"),
    Document(id="m16", text="heartbreak relationship ended crying empty bed insomnia sad"),
    Document(id="m17", text="childhood treehouse summer afternoon imagination freedom play"),
    Document(id="m18", text="public speaking stage lights heart pounding shaking voice"),
    Document(id="m19", text="grandparent kitchen soup story warmth safety unconditional love"),
    Document(id="m20", text="first day school strange building nervous mother leaving separation anxiety"),
]


LINGORA_WORDS: list[Document] = [
    Document(id="w01", text="ocean sea salt water blue waves depth"),
    Document(id="w02", text="river stream flowing fresh water current"),
    Document(id="w03", text="lake still calm freshwater reflection"),
    Document(id="w04", text="mountain peak snow altitude cold stone"),
    Document(id="w05", text="valley low green fertile river between hills"),
    Document(id="w06", text="forest trees canopy green shade wildlife"),
    Document(id="w07", text="desert sand hot dry cactus sun"),
    Document(id="w08", text="city buildings streets crowds noise urban"),
    Document(id="w09", text="village small community rural houses close"),
    Document(id="w10", text="home house family comfort safety shelter"),
    Document(id="w11", text="joy happiness laughter bright positive emotion"),
    Document(id="w12", text="sorrow sadness grief loss heavy emotion"),
    Document(id="w13", text="anger rage fury heat red emotion"),
    Document(id="w14", text="calm peace quiet still mind state"),
    Document(id="w15", text="love affection warmth connection emotion bond"),
    Document(id="w16", text="fear terror dread cold flight emotion"),
    Document(id="w17", text="curiosity wonder exploration question mind"),
    Document(id="w18", text="bird wing feather flight song sky"),
    Document(id="w19", text="fish gill scale water swim silent"),
    Document(id="w20", text="tree branch leaf root growth tall"),
]


STRATA_ASSETS: list[Document] = [
    Document(id="AAPL", text="apple consumer technology hardware iphone services subscription", metadata={"sector": "Tech"}),
    Document(id="MSFT", text="microsoft software cloud azure enterprise office productivity", metadata={"sector": "Tech"}),
    Document(id="GOOGL", text="google alphabet search ads cloud youtube advertising", metadata={"sector": "Tech"}),
    Document(id="NVDA", text="nvidia chips gpu semiconductors ai accelerators datacenter", metadata={"sector": "Tech"}),
    Document(id="META", text="meta facebook social media advertising vr reality labs", metadata={"sector": "Tech"}),
    Document(id="JPM", text="jpmorgan bank financial services investment consumer", metadata={"sector": "Financial"}),
    Document(id="GS", text="goldman sachs investment bank trading wealth management", metadata={"sector": "Financial"}),
    Document(id="BAC", text="bank of america consumer lending mortgage wealth", metadata={"sector": "Financial"}),
    Document(id="XOM", text="exxon oil gas energy upstream downstream crude", metadata={"sector": "Energy"}),
    Document(id="CVX", text="chevron oil gas energy integrated petroleum", metadata={"sector": "Energy"}),
    Document(id="COP", text="conocophillips oil gas exploration production", metadata={"sector": "Energy"}),
    Document(id="JNJ", text="johnson healthcare pharmaceuticals medical devices consumer", metadata={"sector": "Healthcare"}),
    Document(id="PFE", text="pfizer pharmaceuticals vaccines drug development therapies", metadata={"sector": "Healthcare"}),
    Document(id="UNH", text="united health insurance healthcare managed care services", metadata={"sector": "Healthcare"}),
    Document(id="GLD", text="gold precious metal safe haven inflation hedge", metadata={"sector": "Safe haven"}),
    Document(id="TLT", text="treasury long bond government yield duration safe", metadata={"sector": "Safe haven"}),
    Document(id="BTC", text="bitcoin cryptocurrency digital gold decentralized volatile", metadata={"sector": "Crypto"}),
    Document(id="ETH", text="ethereum smart contract blockchain decentralized finance", metadata={"sector": "Crypto"}),
    Document(id="SPY", text="sp500 broad market index etf passive diversified", metadata={"sector": "Index"}),
    Document(id="QQQ", text="nasdaq 100 technology index etf growth large cap", metadata={"sector": "Index"}),
]


# ═══════════════════════════════════════════════════════════════════════
# Seeded retriever cache
# ═══════════════════════════════════════════════════════════════════════

APP_SEEDS: dict[str, list[Document]] = {
    "atria": ATRIA_PLAYERS,
    "axona": AXONA_MEMORIES,
    "lingora": LINGORA_WORDS,
    "strata": STRATA_ASSETS,
}


@dataclass(frozen=True)
class NeighborhoodHit:
    id: str
    text: str
    score: float
    hop_distance: int
    metadata: dict[str, Any]


@lru_cache(maxsize=4)
def _build_retriever(app: str) -> VectoraRetriever:
    """Return a Vectora retriever seeded with the app's canonical items."""
    docs = APP_SEEDS.get(app)
    if docs is None:
        raise KeyError(f"unknown app: {app!r} (expected one of {list(APP_SEEDS)})")
    r = VectoraRetriever(edge_top_m=4, edge_threshold=0.08)
    r.add_documents(docs)
    r.build_graph(include_keyword_edges=True)
    return r


def neighbors(app: str, seed_id: str, k: int = 8, decay: float = 0.35) -> list[NeighborhoodHit]:
    """Return the Vectora neighborhood around a seed node for the given app.

    The query is the seed document's own text — we spread from where it is.
    """
    r = _build_retriever(app)
    doc = r.graph.get_document(seed_id)
    if doc is None:
        raise KeyError(f"unknown seed id for {app}: {seed_id!r}")
    results = r.retrieve(doc.text, k=k + 1, mode=RetrievalMode.VECTORA, decay=decay)
    # Drop the seed itself from the results
    hits: list[NeighborhoodHit] = []
    for res in results:
        if res.doc.id == seed_id:
            continue
        hits.append(
            NeighborhoodHit(
                id=res.doc.id,
                text=res.doc.text,
                score=round(res.score, 4),
                hop_distance=res.hop_distance,
                metadata=dict(res.doc.metadata),
            )
        )
        if len(hits) >= k:
            break
    return hits


def seed_catalog(app: str) -> list[dict[str, Any]]:
    """Return the list of seed docs for an app (for UI dropdowns, etc)."""
    docs = APP_SEEDS.get(app)
    if docs is None:
        raise KeyError(f"unknown app: {app!r}")
    return [{"id": d.id, "text": d.text, "metadata": dict(d.metadata)} for d in docs]


def stats(app: str) -> dict[str, int]:
    r = _build_retriever(app)
    return {
        "documents": len(r.graph),
        "edges": r.graph.edge_count(),
    }


def all_stats() -> dict[str, dict[str, int]]:
    return {app: stats(app) for app in APP_SEEDS}
