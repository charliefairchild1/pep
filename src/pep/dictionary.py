"""Dictionary ingestion + cross-language graph comparison.

A dictionary is a set of `word: definition` entries. Each word becomes a
memory; the words appearing in the definition become tags. Two words whose
definitions reference each other end up linked via co-activation. The
result is a graph that the existing Sky View can render.

Two dictionaries (in different languages) can be loaded into separate
sessions and compared:
  - **Cross-language matches**: when the same headword appears in both
    sessions (literal match) or when their definitions share content words
  - **Structural divergence**: words that have very different neighborhoods
    in each language

This module is intentionally minimal and read-mostly. The web UI's Dictionary
tab calls `parse_dictionary_text` to extract entries, then `ingest_dictionary`
to write them into the store, then the existing `/memories?session_id=...`
endpoint + Sky View renderer to visualize.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from pep.memory.store import MemoryStore
from pep.schemas.memory_schema import Link, MemoryObject

# Words too generic to count as meaningful tags. Same idea as the
# interpreter's stopwords but tuned for dictionary definitions.
_DICT_STOPWORDS = {
    "the", "a", "an", "of", "to", "and", "or", "but", "for", "in", "on",
    "at", "by", "with", "as", "is", "are", "was", "were", "be", "been",
    "being", "this", "that", "these", "those", "it", "its", "they", "them",
    "their", "we", "our", "i", "you", "your", "he", "she", "his", "her",
    "from", "into", "out", "up", "down", "over", "under", "again", "more",
    "most", "some", "such", "no", "not", "only", "own", "same", "so",
    "than", "too", "very", "can", "will", "just", "don", "should", "now",
    "any", "all", "one", "two", "any", "each", "few", "many", "much",
    "other", "another", "any", "do", "does", "did", "doing", "have", "has",
    "had", "having", "what", "which", "who", "whom", "where", "when", "why",
    "how", "if", "then", "else", "may", "might", "must", "would", "could",
    "shall", "ought", "use", "used", "make", "made", "thing", "things",
    "way", "ways", "form", "forms", "kind", "kinds",
}

_WORD_RE = re.compile(r"[A-Za-z'\-]+")


@dataclass
class DictionaryEntry:
    word: str
    definition: str
    referenced_words: list[str]  # other defined words mentioned in the definition


def parse_dictionary_text(text: str) -> list[DictionaryEntry]:
    """Parse a block of dictionary text into entries.

    Accepted formats per line:
        word: definition text
        word - definition text
        word = definition text
        word    definition text   (tab-separated)

    Empty lines and lines starting with # are skipped (comments). The first
    pass collects all headwords; the second pass scans each definition for
    references to OTHER headwords in the dictionary, so links can be built
    later.
    """
    entries_raw: list[tuple[str, str]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Try the various separators in order of specificity
        for sep in (": ", " - ", " = ", "\t"):
            if sep in line:
                word, definition = line.split(sep, 1)
                word = word.strip().lower()
                definition = definition.strip()
                if word and definition:
                    entries_raw.append((word, definition))
                break

    headwords = {word for word, _ in entries_raw}
    entries: list[DictionaryEntry] = []
    for word, definition in entries_raw:
        # Find references: any headword (other than self) mentioned in the def
        def_words = {w.lower() for w in _WORD_RE.findall(definition)}
        referenced = sorted(def_words & headwords - {word})
        entries.append(DictionaryEntry(
            word=word,
            definition=definition,
            referenced_words=referenced,
        ))
    return entries


def _content_tags_from_definition(definition: str) -> list[str]:
    """Pull content tags out of a definition (lowercased, stopword-filtered)."""
    words = _WORD_RE.findall(definition.lower())
    out: list[str] = []
    seen: set[str] = set()
    for w in words:
        if len(w) > 2 and w not in _DICT_STOPWORDS and w not in seen:
            seen.add(w)
            out.append(w)
        if len(out) >= 12:
            break
    return out


def ingest_dictionary(
    store: MemoryStore,
    *,
    text: str,
    session_id: str = "dictionary:default",
    language: str = "english",
) -> dict:
    """Parse dictionary text and write entries into the store as memories.

    Each headword becomes a MemoryObject in `session_id`. Links are added
    between memories whose definitions reference each other (e.g. if "cat"'s
    definition mentions "feline" and "feline" is also a headword, the two
    memories get linked).

    Returns a summary dict with counts.
    """
    entries = parse_dictionary_text(text)
    if not entries:
        return {
            "ingested": 0,
            "links_created": 0,
            "session_id": session_id,
            "language": language,
            "notes": "no entries parsed (check format: 'word: definition' per line)",
        }

    # Pass 1: create one memory per entry, indexed by word
    word_to_id: dict[str, str] = {}
    for entry in entries:
        memory_id = f"dict_{language}_{entry.word.replace(' ', '_').replace('-', '_')[:30]}"
        word_to_id[entry.word] = memory_id

        tags = [language, "dictionary", entry.word] + _content_tags_from_definition(entry.definition)
        # Dedupe + cap
        tags_seen: set[str] = set()
        deduped: list[str] = []
        for t in tags:
            if t not in tags_seen:
                tags_seen.add(t)
                deduped.append(t)
        tags = deduped[:14]

        # Use a substantive face structure: semantic = the definition,
        # episodic = "from the <language> dictionary"
        m = MemoryObject(
            id=memory_id,
            core=entry.definition,
            faces={
                "semantic": entry.definition[:300],
                "episodic": f"a {language} dictionary entry for '{entry.word}'",
                "user": f"the word '{entry.word}'",
            },
            fold_weights={"semantic": 1.0, "episodic": 0.6, "user": 0.7},
            tags=tags,
            brightness=0.6,
            session_id=session_id,
            source_type="fact",
        )
        store.upsert_memory(m)

    # Pass 2: build links between entries whose definitions reference each other
    link_count = 0
    for entry in entries:
        if not entry.referenced_words:
            continue
        memory_id = word_to_id[entry.word]
        m = store.get_memory(memory_id)
        if not m:
            continue
        existing_targets = {l.to_id for l in m.links}
        for ref_word in entry.referenced_words:
            target_id = word_to_id.get(ref_word)
            if target_id and target_id not in existing_targets:
                m.links.append(Link(
                    to_id=target_id,
                    relation="semantic",
                    weight=0.7,
                ))
                existing_targets.add(target_id)
                link_count += 1
        store.upsert_memory(m)

    return {
        "ingested": len(entries),
        "links_created": link_count,
        "session_id": session_id,
        "language": language,
    }


def _word_from_memory(m: MemoryObject, language: str) -> str | None:
    """Recover the headword from a dictionary memory.

    The id is built as `dict_<language>_<word>` but languages can contain
    underscores, so naive splitting breaks. We strip the known prefix
    instead — the language is known because we know which session the
    memory came from.
    """
    prefix = f"dict_{language}_"
    if m.id.startswith(prefix):
        return m.id[len(prefix):].replace("_", " ")
    return None


def compare_dictionaries(
    store: MemoryStore,
    *,
    session_a: str,
    session_b: str,
) -> dict:
    """Compare two ingested dictionaries.

    Returns a summary with:
      - sizes (entries per language)
      - shared_headwords: word that exists in both (literal match — most
        useful when the dictionaries actually use the same word, e.g. for
        loanwords or scientific terms)
      - cross_definition_matches: word X in language A whose definition
        shares content tags with word Y in language B (a hint at semantic
        equivalence even when the headwords differ)
      - structural_divergence: words present in both whose tag neighborhoods
        differ a lot (potential false friends or polysemy across languages)
    """
    # Derive the language name from the session id (session is `dictionary:<lang>`)
    lang_a = session_a.split(":", 1)[1] if ":" in session_a else session_a
    lang_b = session_b.split(":", 1)[1] if ":" in session_b else session_b

    mems_a = store.all_memories(session_id=session_a)
    mems_b = store.all_memories(session_id=session_b)

    by_word_a: dict[str, MemoryObject] = {}
    by_word_b: dict[str, MemoryObject] = {}
    for m in mems_a:
        word = _word_from_memory(m, lang_a)
        if word:
            by_word_a[word] = m
    for m in mems_b:
        word = _word_from_memory(m, lang_b)
        if word:
            by_word_b[word] = m

    shared = sorted(set(by_word_a.keys()) & set(by_word_b.keys()))

    # Structural divergence on shared words: tag-neighborhood Jaccard
    divergence: list[dict] = []
    for word in shared:
        ta = {t for t in by_word_a[word].tags if t not in (session_a, "dictionary", word)}
        tb = {t for t in by_word_b[word].tags if t not in (session_b, "dictionary", word)}
        if not ta and not tb:
            continue
        union_size = len(ta | tb) or 1
        jaccard = len(ta & tb) / union_size
        divergence.append({
            "word": word,
            "tag_jaccard": round(jaccard, 3),
            "tags_a_only": sorted(ta - tb)[:6],
            "tags_b_only": sorted(tb - ta)[:6],
            "shared_tags": sorted(ta & tb)[:6],
        })
    divergence.sort(key=lambda d: d["tag_jaccard"])  # most divergent first

    # Cross-definition matches: words in A whose tags overlap heavily with
    # words in B even though the headwords differ
    cross_matches: list[dict] = []
    for word_a, mem_a in by_word_a.items():
        if word_a in by_word_b:
            continue  # skip literal matches; we already have those
        ta = {t for t in mem_a.tags if t not in (session_a, "dictionary", word_a)}
        if not ta:
            continue
        best_word_b = None
        best_score = 0.0
        for word_b, mem_b in by_word_b.items():
            tb = {t for t in mem_b.tags if t not in (session_b, "dictionary", word_b)}
            if not tb:
                continue
            score = len(ta & tb) / max(1, len(ta | tb))
            if score > best_score:
                best_score = score
                best_word_b = word_b
        if best_word_b and best_score >= 0.2:
            cross_matches.append({
                "word_a": word_a,
                "word_b": best_word_b,
                "tag_jaccard": round(best_score, 3),
            })
    cross_matches.sort(key=lambda d: d["tag_jaccard"], reverse=True)

    return {
        "session_a": session_a,
        "session_b": session_b,
        "size_a": len(by_word_a),
        "size_b": len(by_word_b),
        "shared_headwords": shared,
        "n_shared": len(shared),
        "structural_divergence": divergence[:30],
        "cross_definition_matches": cross_matches[:30],
    }
