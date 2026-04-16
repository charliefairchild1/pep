"""SQLite-backed memory store.

The store IS the persistent state of PEP: memories, links, state log,
and the run ledger that records every PEP invocation for debugging.

Phase 1: plain SQLite, no vector index. Phase 2 will add sqlite-vec.
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator

from pep.schemas.memory_schema import Link, MemoryObject
from pep.schemas.pep_packet import PEPPacket
from pep.schemas.state_schema import State

SCHEMA = """
CREATE TABLE IF NOT EXISTS memories (
    id TEXT PRIMARY KEY,
    core TEXT NOT NULL,
    payload TEXT NOT NULL,
    brightness REAL NOT NULL DEFAULT 0.5,
    activation_count INTEGER NOT NULL DEFAULT 0,
    drift_score REAL NOT NULL DEFAULT 0.0,
    session_id TEXT NOT NULL DEFAULT 'default',
    source_type TEXT NOT NULL DEFAULT 'conversation',
    created_at TEXT NOT NULL,
    last_activated TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_memories_session ON memories(session_id);
CREATE INDEX IF NOT EXISTS idx_memories_brightness ON memories(brightness);

CREATE TABLE IF NOT EXISTS links (
    from_id TEXT NOT NULL,
    to_id TEXT NOT NULL,
    relation TEXT NOT NULL DEFAULT 'semantic',
    weight REAL NOT NULL DEFAULT 0.5,
    PRIMARY KEY (from_id, to_id, relation)
);

CREATE INDEX IF NOT EXISTS idx_links_from ON links(from_id);
CREATE INDEX IF NOT EXISTS idx_links_to ON links(to_id);

CREATE TABLE IF NOT EXISTS state_log (
    session_id TEXT NOT NULL,
    turn_number INTEGER NOT NULL,
    state_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    PRIMARY KEY (session_id, turn_number)
);

CREATE TABLE IF NOT EXISTS pep_runs (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    user_input TEXT NOT NULL,
    packet_json TEXT NOT NULL,
    response TEXT,
    state_before TEXT,
    state_after TEXT,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_runs_session ON pep_runs(session_id);

CREATE TABLE IF NOT EXISTS categories (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    parent_id TEXT,
    member_count INTEGER NOT NULL DEFAULT 0,
    avg_brightness REAL NOT NULL DEFAULT 0.0,
    top_tags TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_categories_parent ON categories(parent_id);

CREATE TABLE IF NOT EXISTS memory_categories (
    memory_id TEXT NOT NULL,
    category_id TEXT NOT NULL,
    strength REAL NOT NULL DEFAULT 1.0,
    PRIMARY KEY (memory_id, category_id)
);

CREATE INDEX IF NOT EXISTS idx_memcat_category ON memory_categories(category_id);
"""


class MemoryStore:
    """SQLite-backed PEP memory + run ledger."""

    def __init__(self, db_path: str | Path = ":memory:"):
        self.db_path = str(db_path)
        if self.db_path != ":memory:":
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._migrate()

    def _migrate(self) -> None:
        with self._conn:
            self._conn.executescript(SCHEMA)

    @contextmanager
    def _tx(self) -> Iterator[sqlite3.Connection]:
        try:
            yield self._conn
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise

    # ---------- MemoryObject CRUD ----------

    def upsert_memory(self, m: MemoryObject) -> None:
        with self._tx() as conn:
            conn.execute(
                """
                INSERT INTO memories
                    (id, core, payload, brightness, activation_count,
                     drift_score, session_id, source_type, created_at, last_activated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    core = excluded.core,
                    payload = excluded.payload,
                    brightness = excluded.brightness,
                    activation_count = excluded.activation_count,
                    drift_score = excluded.drift_score,
                    last_activated = excluded.last_activated
                """,
                (
                    m.id,
                    m.core,
                    m.model_dump_json(),
                    m.brightness,
                    m.activation_count,
                    m.drift_score,
                    m.session_id,
                    m.source_type,
                    m.created_at.isoformat(),
                    m.last_activated.isoformat(),
                ),
            )
            for link in m.links:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO links (from_id, to_id, relation, weight)
                    VALUES (?, ?, ?, ?)
                    """,
                    (m.id, link.to_id, link.relation, link.weight),
                )

    def get_memory(self, memory_id: str) -> MemoryObject | None:
        row = self._conn.execute(
            "SELECT payload FROM memories WHERE id = ?", (memory_id,)
        ).fetchone()
        if not row:
            return None
        return MemoryObject.model_validate_json(row["payload"])

    def all_memories(self, session_id: str | None = None) -> list[MemoryObject]:
        if session_id:
            rows = self._conn.execute(
                "SELECT payload FROM memories WHERE session_id = ? ORDER BY brightness DESC",
                (session_id,),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT payload FROM memories ORDER BY brightness DESC"
            ).fetchall()
        return [MemoryObject.model_validate_json(r["payload"]) for r in rows]

    def neighbors(self, memory_id: str) -> list[Link]:
        rows = self._conn.execute(
            "SELECT to_id, relation, weight FROM links WHERE from_id = ?",
            (memory_id,),
        ).fetchall()
        return [Link(to_id=r["to_id"], relation=r["relation"], weight=r["weight"]) for r in rows]

    def touch_memory(self, memory_id: str, *, brightness_delta: float = 0.05) -> None:
        """Mark a memory as activated. Increments count, bumps brightness, increments drift."""
        with self._tx() as conn:
            row = conn.execute(
                "SELECT payload FROM memories WHERE id = ?", (memory_id,)
            ).fetchone()
            if not row:
                return
            m = MemoryObject.model_validate_json(row["payload"])
            m.activation_count += 1
            m.brightness = min(1.0, m.brightness + brightness_delta)
            m.drift_score = min(1.0, m.drift_score + 0.01)
            m.last_activated = datetime.utcnow()
        self.upsert_memory(m)

    def decay_unused_memories(
        self,
        *,
        decay: float = 0.005,
        floor: float = 0.05,
        exclude_ids: set[str] | None = None,
    ) -> int:
        """Apply per-turn brightness decay to memories not just activated.

        This is the (c) empirical reinforcement half of PTO trajectory storage:
        memories that get reactivated stay bright; memories that sit unused
        slowly fade. Memories whose brightness drops below `floor` are not
        deleted — they just become hard to surface, which is honest. Real
        deletion is a separate pruning step (Phase 3 Category Engine).

        Returns the number of memories whose brightness was lowered.
        """
        exclude = exclude_ids or set()
        rows = self._conn.execute(
            "SELECT id, payload FROM memories"
        ).fetchall()
        affected = 0
        for row in rows:
            if row["id"] in exclude:
                continue
            m = MemoryObject.model_validate_json(row["payload"])
            new_brightness = max(floor, m.brightness - decay)
            if new_brightness < m.brightness:
                m.brightness = new_brightness
                self.upsert_memory(m)
                affected += 1
        return affected

    # ---------- State log ----------

    def log_state(self, session_id: str, turn_number: int, state: State) -> None:
        with self._tx() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO state_log (session_id, turn_number, state_json, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    session_id,
                    turn_number,
                    state.model_dump_json(),
                    datetime.utcnow().isoformat(),
                ),
            )

    def latest_state(self, session_id: str) -> State:
        row = self._conn.execute(
            """
            SELECT state_json FROM state_log
            WHERE session_id = ?
            ORDER BY turn_number DESC LIMIT 1
            """,
            (session_id,),
        ).fetchone()
        if not row:
            return State.neutral()
        return State.model_validate_json(row["state_json"])

    def turn_count(self, session_id: str) -> int:
        row = self._conn.execute(
            "SELECT COUNT(*) AS n FROM state_log WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        return row["n"] or 0

    # ---------- Run ledger ----------

    def log_run(
        self,
        packet: PEPPacket,
        response: str,
        state_before: State,
        state_after: State,
    ) -> None:
        with self._tx() as conn:
            conn.execute(
                """
                INSERT INTO pep_runs
                    (id, session_id, user_input, packet_json, response, state_before, state_after, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    packet.id,
                    packet.session_id,
                    packet.raw_input,
                    packet.model_dump_json(),
                    response,
                    state_before.model_dump_json(),
                    state_after.model_dump_json(),
                    packet.created_at.isoformat(),
                ),
            )

    def get_run(self, run_id: str) -> dict | None:
        row = self._conn.execute(
            "SELECT * FROM pep_runs WHERE id = ?", (run_id,)
        ).fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "session_id": row["session_id"],
            "user_input": row["user_input"],
            "packet": json.loads(row["packet_json"]),
            "response": row["response"],
            "state_before": json.loads(row["state_before"]),
            "state_after": json.loads(row["state_after"]),
            "created_at": row["created_at"],
        }

    def list_runs(self, session_id: str | None = None, limit: int = 50) -> list[dict]:
        if session_id:
            rows = self._conn.execute(
                """
                SELECT id, session_id, user_input, created_at
                FROM pep_runs WHERE session_id = ?
                ORDER BY created_at DESC LIMIT ?
                """,
                (session_id, limit),
            ).fetchall()
        else:
            rows = self._conn.execute(
                """
                SELECT id, session_id, user_input, created_at
                FROM pep_runs ORDER BY created_at DESC LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]

    # ---------- Categories ----------

    def upsert_category(
        self,
        *,
        category_id: str,
        name: str,
        description: str = "",
        parent_id: str | None = None,
        member_count: int = 0,
        avg_brightness: float = 0.0,
        top_tags: list[str] | None = None,
    ) -> None:
        now = datetime.utcnow().isoformat()
        with self._tx() as conn:
            conn.execute(
                """
                INSERT INTO categories
                    (id, name, description, parent_id, member_count,
                     avg_brightness, top_tags, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    description = excluded.description,
                    parent_id = excluded.parent_id,
                    member_count = excluded.member_count,
                    avg_brightness = excluded.avg_brightness,
                    top_tags = excluded.top_tags,
                    updated_at = excluded.updated_at
                """,
                (
                    category_id, name, description, parent_id,
                    member_count, avg_brightness,
                    json.dumps(top_tags or []),
                    now, now,
                ),
            )

    def assign_memory_to_category(
        self, memory_id: str, category_id: str, strength: float = 1.0
    ) -> None:
        with self._tx() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO memory_categories
                    (memory_id, category_id, strength)
                VALUES (?, ?, ?)
                """,
                (memory_id, category_id, strength),
            )

    def get_category(self, category_id: str) -> dict | None:
        row = self._conn.execute(
            "SELECT * FROM categories WHERE id = ?", (category_id,)
        ).fetchone()
        if not row:
            return None
        return {**dict(row), "top_tags": json.loads(row["top_tags"])}

    def list_categories(self, parent_id: str | None = None) -> list[dict]:
        if parent_id is not None:
            rows = self._conn.execute(
                "SELECT * FROM categories WHERE parent_id = ? ORDER BY member_count DESC",
                (parent_id,),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM categories ORDER BY member_count DESC"
            ).fetchall()
        return [{**dict(r), "top_tags": json.loads(r["top_tags"])} for r in rows]

    def category_members(self, category_id: str) -> list[MemoryObject]:
        rows = self._conn.execute(
            """
            SELECT m.payload FROM memories m
            JOIN memory_categories mc ON m.id = mc.memory_id
            WHERE mc.category_id = ?
            ORDER BY mc.strength DESC
            """,
            (category_id,),
        ).fetchall()
        return [MemoryObject.model_validate_json(r["payload"]) for r in rows]

    def memory_categories(self, memory_id: str) -> list[dict]:
        rows = self._conn.execute(
            """
            SELECT c.*, mc.strength FROM categories c
            JOIN memory_categories mc ON c.id = mc.category_id
            WHERE mc.memory_id = ?
            """,
            (memory_id,),
        ).fetchall()
        return [{**dict(r), "top_tags": json.loads(r["top_tags"])} for r in rows]

    def delete_category(self, category_id: str) -> None:
        with self._tx() as conn:
            conn.execute("DELETE FROM memory_categories WHERE category_id = ?", (category_id,))
            conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))

    # ---------- Session housekeeping ----------

    def clear_session(self, session_id: str) -> dict[str, int]:
        """Wipe all memories, state log, and runs for a single session.

        Used by the Demo Runner so a scenario can be re-run cleanly without
        affecting other sessions. Returns counts of what was deleted.
        """
        with self._tx() as conn:
            # Find member ids before deletion (need them to clean links + categories)
            mem_rows = conn.execute(
                "SELECT id FROM memories WHERE session_id = ?", (session_id,)
            ).fetchall()
            mem_ids = [r["id"] for r in mem_rows]

            # Delete the memories themselves
            conn.execute("DELETE FROM memories WHERE session_id = ?", (session_id,))

            # Clean up links touching those memories
            link_count = 0
            for mid in mem_ids:
                cur = conn.execute(
                    "DELETE FROM links WHERE from_id = ? OR to_id = ?", (mid, mid)
                )
                link_count += cur.rowcount or 0

            # Clean memory_categories rows
            for mid in mem_ids:
                conn.execute("DELETE FROM memory_categories WHERE memory_id = ?", (mid,))

            # State log + runs
            cur = conn.execute("DELETE FROM state_log WHERE session_id = ?", (session_id,))
            states_deleted = cur.rowcount or 0

            cur = conn.execute("DELETE FROM pep_runs WHERE session_id = ?", (session_id,))
            runs_deleted = cur.rowcount or 0

        return {
            "memories_deleted": len(mem_ids),
            "links_deleted": link_count,
            "state_entries_deleted": states_deleted,
            "runs_deleted": runs_deleted,
        }

    def close(self) -> None:
        self._conn.close()
