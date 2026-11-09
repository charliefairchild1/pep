"""Dictionary ingestion + cross-language graph comparison tests."""

from __future__ import annotations

from pep.dictionary import (
    DictionaryEntry,
    compare_dictionaries,
    ingest_dictionary,
    parse_dictionary_text,
)
from pep.memory.store import MemoryStore


SAMPLE_ENGLISH = """\
memory: a stored representation of past experience
prediction: an inference about a future state based on a model
context: information that gives meaning to a fact
inference: drawing a conclusion from premises
model: a structured representation of regularities in some domain
"""

SAMPLE_SPANISH = """\
memoria: una representacion almacenada de experiencias pasadas
prediccion: una inferencia sobre un estado futuro basada en un modelo
contexto: la informacion que da significado a un hecho
inferencia: extraer una conclusion a partir de premisas
modelo: una representacion estructurada de regularidades en algun dominio
"""


# ─── parsing ────────────────────────────────────────────────────────────

def test_parse_extracts_word_and_definition() -> None:
    entries = parse_dictionary_text("memory: a stored representation")
    assert len(entries) == 1
    assert entries[0].word == "memory"
    assert "stored representation" in entries[0].definition


def test_parse_handles_dash_separator() -> None:
    entries = parse_dictionary_text("memory - a stored representation")
    assert len(entries) == 1
    assert entries[0].word == "memory"


def test_parse_handles_equals_separator() -> None:
    entries = parse_dictionary_text("memory = a stored representation")
    assert len(entries) == 1
    assert entries[0].word == "memory"


def test_parse_handles_tab_separator() -> None:
    entries = parse_dictionary_text("memory\ta stored representation")
    assert len(entries) == 1
    assert entries[0].word == "memory"


def test_parse_skips_empty_and_comment_lines() -> None:
    text = """\
# this is a comment
memory: a thing

# another comment
prediction: another thing
"""
    entries = parse_dictionary_text(text)
    assert len(entries) == 2
    assert {e.word for e in entries} == {"memory", "prediction"}


def test_parse_finds_referenced_headwords_in_definitions() -> None:
    """A definition that mentions another headword should record the
    reference so the ingester can build links between them."""
    entries = parse_dictionary_text(SAMPLE_ENGLISH)
    by_word = {e.word: e for e in entries}
    # "prediction"'s definition mentions "model" — should be referenced
    assert "model" in by_word["prediction"].referenced_words
    # "inference" doesn't mention any other defined word
    assert by_word["inference"].referenced_words == []


# ─── ingestion ──────────────────────────────────────────────────────────

def test_ingest_creates_one_memory_per_entry() -> None:
    store = MemoryStore(":memory:")
    result = ingest_dictionary(
        store, text=SAMPLE_ENGLISH,
        session_id="dictionary:english", language="english",
    )
    assert result["ingested"] == 5
    assert result["session_id"] == "dictionary:english"
    mems = store.all_memories(session_id="dictionary:english")
    assert len(mems) == 5
    # Each memory should be tagged with the language
    for m in mems:
        assert "english" in m.tags
        assert "dictionary" in m.tags


def test_ingest_creates_links_between_referenced_headwords() -> None:
    store = MemoryStore(":memory:")
    result = ingest_dictionary(
        store, text=SAMPLE_ENGLISH,
        session_id="dictionary:english", language="english",
    )
    # We expect at least one link: "prediction" → "model"
    assert result["links_created"] >= 1
    # Verify the link exists in the prediction memory
    pred = store.get_memory("dict_english_prediction")
    assert pred is not None
    target_ids = {l.to_id for l in pred.links}
    assert "dict_english_model" in target_ids


def test_ingest_returns_helpful_note_on_empty_input() -> None:
    store = MemoryStore(":memory:")
    result = ingest_dictionary(store, text="", session_id="dictionary:empty")
    assert result["ingested"] == 0
    assert "no entries" in result.get("notes", "")


# ─── cross-language comparison ──────────────────────────────────────────

def test_compare_returns_sizes_and_shared_headwords() -> None:
    """Two dictionaries with no overlapping headwords should still produce
    a comparison report with both sizes."""
    store = MemoryStore(":memory:")
    ingest_dictionary(
        store, text=SAMPLE_ENGLISH,
        session_id="dictionary:english", language="english",
    )
    ingest_dictionary(
        store, text=SAMPLE_SPANISH,
        session_id="dictionary:spanish", language="spanish",
    )
    result = compare_dictionaries(
        store, session_a="dictionary:english", session_b="dictionary:spanish",
    )
    assert result["size_a"] == 5
    assert result["size_b"] == 5
    # English and Spanish headwords are different so no literal matches
    assert result["n_shared"] == 0
    # But the structure of the report is sound
    assert "structural_divergence" in result
    assert "cross_definition_matches" in result


def test_compare_finds_literal_matches_for_shared_headwords() -> None:
    """When the same headword appears in both dictionaries (e.g. loanwords
    or technical terms), it should appear in shared_headwords."""
    store = MemoryStore(":memory:")
    ingest_dictionary(
        store, text="cafe: a place where coffee is served\ninternet: a global network",
        session_id="dictionary:lang_a", language="lang_a",
    )
    ingest_dictionary(
        store, text="cafe: un lugar donde se sirve cafe\ninternet: una red global",
        session_id="dictionary:lang_b", language="lang_b",
    )
    result = compare_dictionaries(
        store, session_a="dictionary:lang_a", session_b="dictionary:lang_b",
    )
    assert "cafe" in result["shared_headwords"]
    assert "internet" in result["shared_headwords"]
    assert result["n_shared"] == 2
