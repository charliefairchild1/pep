"""SQLite persistence for Vectora's DocumentGraph.

Stores documents + edges + opacity state in a SQLite database so the
graph survives server restarts. The in-memory graph is the primary
data structure; SQLite is the backup that loads on startup and saves
on mutating operations.

Usage:
    from vectora.persistence import PersistentGraph
    pg = PersistentGraph("my_corpus.db")
    pg.add_document(Document(id="a", text="hello"))
    pg.save()  # explicit save
    # On restart:
    pg = PersistentGraph("my_corpus.db")  # auto-loads existing data
"""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any

from .document import Document
from .graph import DocumentGraph, Edge


class PersistentGraph:
    """DocumentGraph backed by SQLite for cross-session persistence."""

    def __init__(self, db_path: str | Path = "vectora.db") -> None:
        self.db_path = str(db_path)
        self.graph = DocumentGraph()
        self._conn = sqlite3.connect(self.db_path)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._create_tables()
        self._load()

    def _create_tables(self) -> None:
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                text TEXT NOT NULL,
                embedding TEXT,
                metadata TEXT,
                opacity REAL DEFAULT 1.0,
                opacity_floor REAL DEFAULT 0.0,
                encoded_at REAL,
                half_life_seconds REAL DEFAULT 604800
            );
            CREATE TABLE IF NOT EXISTS edges (
                source TEXT NOT NULL,
                target TEXT NOT NULL,
                weight REAL NOT NULL,
                edge_type TEXT DEFAULT 'embedding',
                UNIQUE(source, target, edge_type)
            );
            CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source);
        """)
        self._conn.commit()

    def _load(self) -> None:
        """Load existing data from SQLite into the in-memory graph."""
        cursor = self._conn.execute("SELECT * FROM documents")
        for row in cursor.fetchall():
            doc = Document(
                id=row[0], text=row[1],
                embedding=json.loads(row[2]) if row[2] else [],
                metadata=json.loads(row[3]) if row[3] else {},
                opacity=row[4] or 1.0,
                opacity_floor=row[5] or 0.0,
                encoded_at=row[6] or time.time(),
                half_life_seconds=row[7] or 604800,
            )
            try:
                self.graph.add_document(doc)
            except ValueError:
                pass  # duplicate on reload

        cursor = self._conn.execute("SELECT * FROM edges")
        for row in cursor.fetchall():
            try:
                self.graph.add_edge(Edge(source=row[0], target=row[1], weight=row[2], edge_type=row[3] or "embedding"))
            except ValueError:
                pass

    # ── Document operations ─────────────────────────────────────────────
    def add_document(self, doc: Document) -> None:
        self.graph.add_document(doc)
        self._conn.execute(
            "INSERT OR REPLACE INTO documents (id, text, embedding, metadata, opacity, opacity_floor, encoded_at, half_life_seconds) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (doc.id, doc.text,
             json.dumps(doc.embedding) if doc.embedding else None,
             json.dumps(doc.metadata) if doc.metadata else None,
             doc.opacity, doc.opacity_floor, doc.encoded_at, doc.half_life_seconds),
        )
        self._conn.commit()

    def get_document(self, doc_id: str) -> Document | None:
        return self.graph.get_document(doc_id)

    def documents(self) -> list[Document]:
        return self.graph.documents()

    # ── Edge operations ─────────────────────────────────────────────────
    def add_edge(self, edge: Edge) -> None:
        self.graph.add_edge(edge)
        self._conn.execute(
            "INSERT OR REPLACE INTO edges (source, target, weight, edge_type) VALUES (?, ?, ?, ?)",
            (edge.source, edge.target, edge.weight, edge.edge_type),
        )
        self._conn.commit()

    # ── Bulk operations ─────────────────────────────────────────────────
    def save(self) -> None:
        """Persist the current in-memory state to SQLite (full sync)."""
        self._conn.execute("DELETE FROM documents")
        self._conn.execute("DELETE FROM edges")
        for doc in self.graph.documents():
            self._conn.execute(
                "INSERT INTO documents (id, text, embedding, metadata, opacity, opacity_floor, encoded_at, half_life_seconds) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (doc.id, doc.text,
                 json.dumps(doc.embedding) if doc.embedding else None,
                 json.dumps(doc.metadata) if doc.metadata else None,
                 doc.opacity, doc.opacity_floor, doc.encoded_at, doc.half_life_seconds),
            )
        for edge in self.graph.edges():
            self._conn.execute(
                "INSERT OR IGNORE INTO edges (source, target, weight, edge_type) VALUES (?, ?, ?, ?)",
                (edge.source, edge.target, edge.weight, edge.edge_type),
            )
        self._conn.commit()

    def close(self) -> None:
        self.save()
        self._conn.close()

    # ── Stats ───────────────────────────────────────────────────────────
    def stats(self) -> dict[str, Any]:
        return {
            "documents": len(self.graph),
            "edges": self.graph.edge_count(),
            "db_path": self.db_path,
            "db_size_bytes": Path(self.db_path).stat().st_size if Path(self.db_path).exists() else 0,
        }

    def __len__(self) -> int:
        return len(self.graph)

    def __contains__(self, doc_id: object) -> bool:
        return doc_id in self.graph

    def __enter__(self) -> "PersistentGraph":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
