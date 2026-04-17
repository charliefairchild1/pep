"""Smoke tests for the LAVAS route surfaces and their bridges.

Verifies:
- Each sibling page returns 200 with HTML content
- Each bridge POST /event / GET /events / GET /pep-state round-trips
- The PEP /pep page loads and cross-references siblings
- The root redirect lands on /pep
- Bridge cross-reads between siblings work (trilateral+ mesh)
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from pep.main import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    with TestClient(app) as c:
        yield c


SIBLINGS = ["axona", "lingora", "atria", "vectora", "strata"]


def test_root_redirects_to_pep(client: TestClient) -> None:
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code in (307, 302, 303)
    assert resp.headers["location"] == "/pep"


def test_pep_teaching_page(client: TestClient) -> None:
    resp = client.get("/pep")
    assert resp.status_code == 200
    body = resp.text
    # Should mention every sibling on the LAVAS cards
    for sibling in SIBLINGS:
        assert sibling.capitalize() in body or sibling in body.lower()


@pytest.mark.parametrize("sibling", SIBLINGS)
def test_sibling_page_loads(client: TestClient, sibling: str) -> None:
    resp = client.get(f"/{sibling}")
    assert resp.status_code == 200
    body = resp.text
    # Every sibling page includes its own tab structure
    assert '<div class="tabs"' in body or 'id="tabs"' in body
    # Every sibling has a canvas dropdown for jumping between canvases
    assert 'id="canvas-select"' in body


@pytest.mark.parametrize("sibling", SIBLINGS)
def test_sibling_bridge_post_and_get_roundtrip(client: TestClient, sibling: str) -> None:
    # Post an event to the sibling's bridge and read it back.
    payload = {"type": "test.smoke", "payload": {"k": "v"}}
    post = client.post(f"/{sibling}/event", json=payload)
    assert post.status_code == 200
    body = post.json()
    assert body["ok"] is True
    assert body["stored"]["type"] == "test.smoke"

    events = client.get(f"/{sibling}/events?limit=5")
    assert events.status_code == 200
    data = events.json()
    assert data["count"] >= 1
    assert any(item["type"] == "test.smoke" for item in data["items"])


@pytest.mark.parametrize("sibling", SIBLINGS)
def test_sibling_pep_state(client: TestClient, sibling: str) -> None:
    resp = client.get(f"/{sibling}/pep-state")
    assert resp.status_code == 200
    data = resp.json()
    assert data["connected"] is True
    # pep-state always includes a timestamp and an event count for this sibling
    assert "t" in data
    assert f"{sibling}_events" in data


def test_strata_pep_state_cross_reads_all_siblings(client: TestClient) -> None:
    # Strata's bridge was written last and cross-reads all four others.
    # Used by the /pep mesh dashboard as the canonical source of counts.
    resp = client.get("/strata/pep-state")
    assert resp.status_code == 200
    data = resp.json()
    for sibling in SIBLINGS:
        assert f"{sibling}_events" in data, f"missing {sibling}_events in strata pep-state"


def test_axona_has_gallery_tab(client: TestClient) -> None:
    resp = client.get("/axona")
    assert resp.status_code == 200
    assert 'data-panel="gallery-tab"' in resp.text
    assert 'id="gallery-tab"' in resp.text


def test_atria_has_pitch_and_dashboard_tabs(client: TestClient) -> None:
    resp = client.get("/atria")
    assert resp.status_code == 200
    assert 'data-panel="pitch-tab"' in resp.text
    assert 'data-panel="dashboard-tab"' in resp.text


def test_vectora_grouped_tabs(client: TestClient) -> None:
    # Vectora was consolidated from 13 tabs to 7 grouped tabs.
    resp = client.get("/vectora")
    assert resp.status_code == 200
    body = resp.text
    # Grouped tabs use data-panels (plural)
    assert 'data-panels="keyword-tab embed-tab rerank-tab multihop-tab context-tab"' in body
    assert 'data-panels="kg-tab anomaly-tab"' in body
    assert 'data-panels="pitch-tab bench-tab"' in body


PRODUCT_PAGES = [
    ("/lingora/prompt", "Lingora Prompt"),
    ("/atria/match", "Atria Match"),
    ("/axona/edge", "Axona Edge"),
    ("/vectora/retrieval", "Vectora Retrieval"),
    ("/vectora/context", "Vectora Context"),
    ("/vectora/watch", "Vectora Watch"),
    ("/vectora/graph", "Vectora Graph"),
    ("/strata/equities", "Strata Equities"),
]


def test_vectora_playground_loads(client: TestClient) -> None:
    resp = client.get("/vectora/playground")
    assert resp.status_code == 200
    assert "Vectora Playground" in resp.text
    assert "Load sample" in resp.text


def test_vectora_playground_sample(client: TestClient) -> None:
    resp = client.get("/vectora/playground/sample")
    assert resp.status_code == 200
    data = resp.json()
    assert "documents" in data
    assert "suggested_queries" in data
    assert len(data["documents"]) > 10
    assert len(data["suggested_queries"]) > 0


def test_vectora_playground_retrieval_roundtrip(client: TestClient) -> None:
    payload = {
        "documents": [
            {"id": "a", "text": "redis caching django applications"},
            {"id": "b", "text": "memory pressure under heavy load"},
            {"id": "c", "text": "totally unrelated topic about sailing"},
        ],
        "query": "caching strategies",
        "k": 3,
    }
    resp = client.post("/vectora/playground/retrieve", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "topk" in data
    assert "vectora" in data
    assert "stats" in data
    assert data["stats"]["nodes"] == 3
    assert len(data["topk"]) > 0


def test_vectora_playground_rejects_too_many_docs(client: TestClient) -> None:
    payload = {
        "documents": [{"id": f"d{i}", "text": f"doc {i}"} for i in range(100)],
        "query": "anything",
        "k": 3,
    }
    resp = client.post("/vectora/playground/retrieve", json=payload)
    assert resp.status_code == 400


DOGFOOD_APPS = ["atria", "axona", "lingora", "strata"]


@pytest.mark.parametrize("app", DOGFOOD_APPS)
def test_dogfood_seeds_endpoint(client: TestClient, app: str) -> None:
    resp = client.get(f"/vectora/seeds/{app}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["app"] == app
    assert len(data["seeds"]) == 20
    assert data["stats"]["documents"] == 20


@pytest.mark.parametrize("app,seed", [
    ("atria", "p01"), ("axona", "m03"),
    ("lingora", "w06"), ("strata", "AAPL"),
])
def test_dogfood_neighbors_endpoint(client: TestClient, app: str, seed: str) -> None:
    resp = client.get(f"/vectora/neighbors/{app}/{seed}?k=5")
    assert resp.status_code == 200
    data = resp.json()
    assert data["powered_by"] == "vectora"
    assert data["seed"] == seed
    assert len(data["hits"]) > 0
    # The seed itself should not appear in the hits
    assert all(h["id"] != seed for h in data["hits"])


def test_dogfood_context_roundtrip(client: TestClient) -> None:
    sess = "roundtrip-" + "a" * 5
    rec = client.post(
        "/vectora/context/lingora/record",
        json={"session_id": sess, "doc_id": "w11"},
    )
    assert rec.status_code == 200
    assert rec.json()["session_size"] == 1
    cmp = client.post(
        "/vectora/context/lingora/compare",
        json={"session_id": sess, "seed_id": "w15", "k": 4},
    )
    assert cmp.status_code == 200
    data = cmp.json()
    assert "plain" in data and "contextual" in data
    assert data["session"]["size"] == 1


def test_dogfood_watch_roundtrip(client: TestClient) -> None:
    resp = client.post(
        "/vectora/watch/strata/score",
        json={"text": "rare earth element sovereign nationalization export ban"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "residual" in data
    assert data["label"] in ("normal", "notable", "unusual", "extreme")


def test_dogfood_kg_roundtrip(client: TestClient) -> None:
    viz = client.get("/vectora/kg/atria/viz")
    assert viz.status_code == 200
    assert viz.json()["stats"]["typed_edges"] > 0
    trav = client.post(
        "/vectora/kg/atria/traverse",
        json={"start": "p02", "max_hops": 2},
    )
    assert trav.status_code == 200


def test_eval_endpoint_returns_real_numbers(client: TestClient) -> None:
    resp = client.get("/vectora/eval/run?k=10")
    assert resp.status_code == 200
    data = resp.json()
    assert "topk" in data and "vectora" in data and "delta" in data
    # 12 labeled queries in the built-in eval
    assert data["topk"]["n_queries"] == 12
    # Vectora should beat top-k on recall on this corpus
    assert data["delta"]["recall"] > 0


def test_benchmark_page_loads(client: TestClient) -> None:
    resp = client.get("/vectora/benchmark")
    assert resp.status_code == 200
    assert "Vectora Benchmark" in resp.text


# ── Lingora Prompt API tests ────────────────────────────────────────────
def test_lingora_prompt_playground_loads(client: TestClient) -> None:
    resp = client.get("/lingora/prompt/playground")
    assert resp.status_code == 200
    assert "Lingora Prompt" in resp.text


def test_lingora_prompt_api_analyze(client: TestClient) -> None:
    resp = client.post(
        "/lingora/prompt-api/analyze",
        json={"text": "Please make sure to be helpful and useful. Thanks.", "include_rewrite": True},
    )
    assert resp.status_code == 200
    data = resp.json()
    # The engine should find at least one antipattern in that text
    assert len(data["findings"]) > 0
    assert data["total_tokens"] > 0
    assert data["rewrite"] is not None
    assert data["rewrite"]["compressed_tokens"] <= data["rewrite"]["original_tokens"]


def test_lingora_prompt_api_rewrite(client: TestClient) -> None:
    resp = client.post(
        "/lingora/prompt-api/rewrite",
        json={"text": "Please make sure to answer concisely."},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "make sure to" not in data["compressed_text"].lower()


def test_lingora_prompt_api_cost(client: TestClient) -> None:
    resp = client.post(
        "/lingora/prompt-api/cost",
        json={"text": "Hello world.", "daily_requests": 1000, "output_tokens": 100},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["costs"]) > 5  # multiple providers in the table


def test_lingora_prompt_api_compare(client: TestClient) -> None:
    resp = client.post(
        "/lingora/prompt-api/compare",
        json={"original": "Please please please be helpful.", "daily_requests": 10_000},
    )
    assert resp.status_code == 200
    data = resp.json()
    # Compressed should exist; savings may be 0 on short prompts but
    # the structure should be valid
    assert "compressed" in data
    assert isinstance(data["per_provider"], list)


def test_lingora_prompt_api_rejects_too_long(client: TestClient) -> None:
    resp = client.post(
        "/lingora/prompt-api/analyze",
        json={"text": "x" * 60_000},
    )
    assert resp.status_code == 400


def test_dogfood_unknown_app_404(client: TestClient) -> None:
    assert client.get("/vectora/neighbors/bogus/x").status_code == 404
    assert client.get("/vectora/seeds/bogus").status_code == 404


def test_dogfood_unknown_seed_404(client: TestClient) -> None:
    assert client.get("/vectora/neighbors/atria/nonexistent-id").status_code == 404


@pytest.mark.parametrize("path", [
    "/vectora/context-playground",
    "/vectora/watch-playground",
    "/vectora/graph-playground",
])
def test_product_playground_pages_load(client: TestClient, path: str) -> None:
    resp = client.get(path)
    assert resp.status_code == 200
    assert "Vectora" in resp.text


def test_context_playground_record_and_retrieve(client: TestClient) -> None:
    rec = client.post(
        "/vectora/context-playground/record",
        json={"session_id": "t-ctx", "doc_id": "cache-1"},
    )
    assert rec.status_code == 200
    retrieved = client.post(
        "/vectora/context-playground/retrieve",
        json={"session_id": "t-ctx", "query": "caching", "k": 5},
    )
    assert retrieved.status_code == 200
    data = retrieved.json()
    assert "plain" in data and "contextual" in data
    assert len(data["recent_views"]) >= 1


def test_watch_playground_score(client: TestClient) -> None:
    resp = client.post(
        "/vectora/watch-playground/score",
        json={"text": "redis caching strategies for django"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert 0 <= data["residual"] <= 100
    assert data["label"] in ("normal", "notable", "unusual", "extreme")


def test_kg_playground_triple_and_traverse(client: TestClient) -> None:
    add = client.post(
        "/vectora/graph-playground/triple",
        json={"source": "embed-1", "relation": "related_to", "target": "embed-4"},
    )
    assert add.status_code == 200
    viz = client.get("/vectora/graph-playground/viz")
    assert viz.status_code == 200
    assert viz.json()["stats"]["typed_edges"] >= 1
    trav = client.post(
        "/vectora/graph-playground/traverse",
        json={"start": "cache-1", "max_hops": 2},
    )
    assert trav.status_code == 200
    results = trav.json()["results"]
    # cache-1 has seeded edges so some results expected
    assert len(results) > 0


def test_dogfood_stats_covers_all_apps(client: TestClient) -> None:
    resp = client.get("/vectora/dogfood/stats")
    assert resp.status_code == 200
    apps = resp.json()["apps"]
    for app in DOGFOOD_APPS:
        assert app in apps
        assert apps[app]["documents"] > 0


def test_vectora_playground_rejects_empty(client: TestClient) -> None:
    resp = client.post(
        "/vectora/playground/retrieve",
        json={"documents": [], "query": "x", "k": 3},
    )
    assert resp.status_code == 400


@pytest.mark.parametrize("path,title", PRODUCT_PAGES)
def test_product_page_loads(client: TestClient, path: str, title: str) -> None:
    resp = client.get(path)
    assert resp.status_code == 200
    assert title in resp.text
    # Each product page links back to its parent app
    parent = path.rsplit("/", 1)[0]
    assert f'href="{parent}"' in resp.text


def test_strata_has_pitch_and_bench(client: TestClient) -> None:
    resp = client.get("/strata")
    assert resp.status_code == 200
    body = resp.text
    assert 'id="pitch-tab"' in body
    assert 'id="bench-tab"' in body
