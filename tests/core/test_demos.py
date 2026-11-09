"""Demo Runner endpoints + clear_session tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from pep.demos import SCENARIOS, get_scenario, list_scenarios
from pep.main import app
from pep.memory.store import MemoryStore
from pep.schemas.memory_schema import MemoryObject


def test_list_scenarios_returns_all_scenarios() -> None:
    items = list_scenarios()
    assert len(items) == len(SCENARIOS)
    for item in items:
        assert "id" in item
        assert "title" in item
        assert "summary" in item
        assert "step_count" in item
        assert item["step_count"] >= 1


def test_get_scenario_returns_full_step_list() -> None:
    s = get_scenario("memory_across_turns")
    assert s is not None
    assert s["id"] == "memory_across_turns"
    assert "steps" in s
    assert len(s["steps"]) >= 3
    assert all("text" in step for step in s["steps"])


def test_get_scenario_unknown_returns_none() -> None:
    assert get_scenario("does_not_exist") is None


def test_demos_list_endpoint() -> None:
    with TestClient(app) as client:
        r = client.get("/demos")
        assert r.status_code == 200
        items = r.json()
        assert len(items) == len(SCENARIOS)
        ids = {item["id"] for item in items}
        assert "memory_across_turns" in ids


def test_demos_get_endpoint_returns_steps() -> None:
    with TestClient(app) as client:
        r = client.get("/demos/memory_across_turns")
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == "memory_across_turns"
        assert len(data["steps"]) >= 3


def test_demos_get_endpoint_404_for_unknown() -> None:
    with TestClient(app) as client:
        r = client.get("/demos/nonexistent")
        assert r.status_code == 404


def test_clear_session_wipes_memories_and_state() -> None:
    """clear_session() should remove memories, state log, and runs for one
    session while leaving other sessions untouched."""
    store = MemoryStore(":memory:")

    # Two sessions, each with memories
    for i in range(3):
        store.upsert_memory(MemoryObject(
            id=f"mem_demo_{i}", core=f"demo {i}",
            tags=["a"], session_id="demo",
        ))
    for i in range(2):
        store.upsert_memory(MemoryObject(
            id=f"mem_other_{i}", core=f"other {i}",
            tags=["b"], session_id="other",
        ))

    # Each gets some state log entries too
    from pep.schemas.state_schema import State
    store.log_state("demo", 1, State(urgency=0.3))
    store.log_state("other", 1, State(urgency=0.5))

    result = store.clear_session("demo")

    assert result["memories_deleted"] == 3
    assert result["state_entries_deleted"] == 1

    # Demo memories gone
    assert all(not m.id.startswith("mem_demo_") for m in store.all_memories())
    # Other session untouched
    assert any(m.id.startswith("mem_other_") for m in store.all_memories())
    # Demo state gone, other session state still there
    assert store.turn_count("demo") == 0
    assert store.turn_count("other") == 1


def test_clear_session_endpoint() -> None:
    with TestClient(app) as client:
        # Seed some memories via the chat endpoint so the persistent store has them
        client.post("/chat", json={"text": "demo seed message", "session_id": "demo"})
        # Clear the demo session
        r = client.post("/sessions/demo/clear")
        assert r.status_code == 200
        data = r.json()
        assert "memories_deleted" in data
        assert "runs_deleted" in data
