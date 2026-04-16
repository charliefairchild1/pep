"""Category Engine — emergent categories from the memory graph.

Scans all memories, clusters them by tag co-occurrence + link structure,
and promotes stable clusters into named categories. Categories are the
"folds" in the paper fortune teller metaphor: they group related memories
so retrieval can descend through layers instead of searching everything.

Operations:
  - **discover**: find new clusters worth naming
  - **split**: break an overcrowded category into subcategories
  - **merge**: collapse two redundant categories into one
  - **decay**: remove categories that lost all their members
  - **update**: refresh stats (member_count, avg_brightness, top_tags)

The engine is called by `pep consolidate` (CLI) or can be wired into
a periodic schedule. It is NOT called on every turn — category evolution
is slower than per-turn reactivation.
"""

from __future__ import annotations

import uuid
from collections import Counter, defaultdict

from pep.memory.store import MemoryStore
from pep.schemas.memory_schema import MemoryObject

# Tunables
MIN_CLUSTER_SIZE = 3          # minimum memories to form a category
TAG_OVERLAP_THRESHOLD = 0.3   # Jaccard threshold for "same cluster"
SPLIT_THRESHOLD = 15          # split a category if it has more members than this
MERGE_THRESHOLD = 0.6         # merge two categories if tag Jaccard exceeds this
DECAY_THRESHOLD = 1           # delete a category if member_count drops to this or below


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _memory_tag_set(m: MemoryObject) -> set[str]:
    return {t.lower() for t in m.tags}


def _cluster_memories(memories: list[MemoryObject]) -> list[list[MemoryObject]]:
    """Greedy single-linkage clustering by tag Jaccard.

    Each memory is assigned to the first cluster it overlaps with sufficiently.
    If none match, it starts a new cluster. This is intentionally simple —
    real spectral/DBSCAN clustering would be better but also a dependency.
    """
    clusters: list[tuple[set[str], list[MemoryObject]]] = []

    for m in memories:
        tags = _memory_tag_set(m)
        if not tags:
            continue
        assigned = False
        for cluster_tags, cluster_members in clusters:
            if _jaccard(tags, cluster_tags) >= TAG_OVERLAP_THRESHOLD:
                cluster_tags |= tags
                cluster_members.append(m)
                assigned = True
                break
        if not assigned:
            clusters.append((set(tags), [m]))

    return [members for _, members in clusters if len(members) >= MIN_CLUSTER_SIZE]


def _name_cluster(members: list[MemoryObject]) -> tuple[str, str, list[str]]:
    """Generate a name, description, and top_tags for a new category."""
    all_tags: Counter[str] = Counter()
    for m in members:
        all_tags.update(t.lower() for t in m.tags)
    top = [tag for tag, _ in all_tags.most_common(6)]
    name = "+".join(top[:3]) if top else "unnamed"
    desc = f"Emergent category from {len(members)} memories. Top tags: {', '.join(top)}"
    return name, desc, top


def discover_categories(store: MemoryStore) -> list[str]:
    """Find new clusters in memory and promote them to categories.

    Returns the IDs of newly created categories.
    """
    memories = store.all_memories()
    if len(memories) < MIN_CLUSTER_SIZE:
        return []

    # Get memories not yet assigned to any category
    assigned_ids: set[str] = set()
    for cat in store.list_categories():
        for m in store.category_members(cat["id"]):
            assigned_ids.add(m.id)

    unassigned = [m for m in memories if m.id not in assigned_ids]
    if len(unassigned) < MIN_CLUSTER_SIZE:
        return []

    clusters = _cluster_memories(unassigned)
    new_ids: list[str] = []

    for members in clusters:
        name, desc, top_tags = _name_cluster(members)
        cat_id = f"cat_{uuid.uuid4().hex[:10]}"
        avg_b = sum(m.brightness for m in members) / len(members)

        store.upsert_category(
            category_id=cat_id,
            name=name,
            description=desc,
            member_count=len(members),
            avg_brightness=round(avg_b, 4),
            top_tags=top_tags,
        )
        for m in members:
            # Strength = how well this memory fits the cluster (tag overlap with top_tags)
            overlap = len(_memory_tag_set(m) & set(top_tags)) / max(1, len(top_tags))
            store.assign_memory_to_category(m.id, cat_id, strength=round(overlap, 3))

        new_ids.append(cat_id)

    return new_ids


def update_category_stats(store: MemoryStore) -> int:
    """Refresh member_count, avg_brightness, and top_tags for all categories.

    Returns the number of categories updated.
    """
    updated = 0
    for cat in store.list_categories():
        members = store.category_members(cat["id"])
        if not members:
            continue
        all_tags: Counter[str] = Counter()
        total_b = 0.0
        for m in members:
            all_tags.update(t.lower() for t in m.tags)
            total_b += m.brightness
        top = [tag for tag, _ in all_tags.most_common(6)]
        store.upsert_category(
            category_id=cat["id"],
            name=cat["name"],
            description=cat["description"],
            parent_id=cat.get("parent_id"),
            member_count=len(members),
            avg_brightness=round(total_b / len(members), 4),
            top_tags=top,
        )
        updated += 1
    return updated


def split_large_categories(store: MemoryStore) -> list[str]:
    """Split categories that grew beyond SPLIT_THRESHOLD into subcategories.

    Returns IDs of newly created subcategories.
    """
    new_ids: list[str] = []
    for cat in store.list_categories():
        members = store.category_members(cat["id"])
        if len(members) <= SPLIT_THRESHOLD:
            continue

        # Re-cluster within the category
        sub_clusters = _cluster_memories(members)
        if len(sub_clusters) < 2:
            continue

        for sub_members in sub_clusters:
            name, desc, top_tags = _name_cluster(sub_members)
            sub_id = f"cat_{uuid.uuid4().hex[:10]}"
            avg_b = sum(m.brightness for m in sub_members) / len(sub_members)

            store.upsert_category(
                category_id=sub_id,
                name=name,
                description=desc,
                parent_id=cat["id"],
                member_count=len(sub_members),
                avg_brightness=round(avg_b, 4),
                top_tags=top_tags,
            )
            for m in sub_members:
                overlap = len(_memory_tag_set(m) & set(top_tags)) / max(1, len(top_tags))
                store.assign_memory_to_category(m.id, sub_id, strength=round(overlap, 3))

            new_ids.append(sub_id)

    return new_ids


def merge_similar_categories(store: MemoryStore) -> int:
    """Merge categories whose top_tags overlap beyond MERGE_THRESHOLD.

    Returns the number of merges performed.
    """
    cats = store.list_categories()
    merged_count = 0
    merged_ids: set[str] = set()

    for i in range(len(cats)):
        if cats[i]["id"] in merged_ids:
            continue
        tags_i = set(cats[i].get("top_tags") or [])
        for j in range(i + 1, len(cats)):
            if cats[j]["id"] in merged_ids:
                continue
            tags_j = set(cats[j].get("top_tags") or [])
            if _jaccard(tags_i, tags_j) >= MERGE_THRESHOLD:
                # Merge j into i: move j's members to i, delete j
                for m in store.category_members(cats[j]["id"]):
                    store.assign_memory_to_category(m.id, cats[i]["id"])
                store.delete_category(cats[j]["id"])
                merged_ids.add(cats[j]["id"])
                merged_count += 1

    if merged_count:
        update_category_stats(store)
    return merged_count


def decay_empty_categories(store: MemoryStore) -> int:
    """Delete categories with too few members. Returns count deleted."""
    deleted = 0
    for cat in store.list_categories():
        members = store.category_members(cat["id"])
        if len(members) <= DECAY_THRESHOLD:
            store.delete_category(cat["id"])
            deleted += 1
    return deleted


def run_category_engine(store: MemoryStore) -> dict[str, int]:
    """Run the full category lifecycle: discover, split, merge, decay, update.

    Returns a summary of what happened.
    """
    new = discover_categories(store)
    splits = split_large_categories(store)
    merges = merge_similar_categories(store)
    decayed = decay_empty_categories(store)
    updated = update_category_stats(store)

    return {
        "categories_created": len(new),
        "subcategories_from_splits": len(splits),
        "merges": merges,
        "decayed": decayed,
        "stats_updated": updated,
    }
