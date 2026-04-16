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
    ("/strata/equities", "Strata Equities"),
]


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
