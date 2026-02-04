"""Semantic diff engine for ontology comparison."""

from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class SemanticDiff:
    """
    Represents semantic differences between two ontology versions.

    Tracks entity-level changes rather than line-level changes.
    """

    entities_added: Set[str] = field(default_factory=set)
    entities_removed: Set[str] = field(default_factory=set)
    properties_modified: Dict[str, List[tuple]] = field(default_factory=dict)
    relationships_added: List[tuple] = field(default_factory=list)
    relationships_removed: List[tuple] = field(default_factory=list)

    def is_empty(self) -> bool:
        """Check if there are any differences."""
        return (
            len(self.entities_added) == 0
            and len(self.entities_removed) == 0
            and len(self.properties_modified) == 0
            and len(self.relationships_added) == 0
            and len(self.relationships_removed) == 0
        )

    def to_dict(self) -> Dict:
        """Export diff as JSON-serializable dictionary."""
        return {
            "entities_added": list(self.entities_added),
            "entities_removed": list(self.entities_removed),
            "properties_modified": {
                k: v for k, v in self.properties_modified.items()
            },
            "relationships_added": self.relationships_added,
            "relationships_removed": self.relationships_removed,
        }

    def __str__(self) -> str:
        """Human-readable diff summary."""
        parts = []
        if self.entities_added:
            parts.append(f"+{len(self.entities_added)} entities")
        if self.entities_removed:
            parts.append(f"-{len(self.entities_removed)} entities")
        if self.properties_modified:
            parts.append(f"~{len(self.properties_modified)} modified")
        if self.relationships_added:
            parts.append(f"+{len(self.relationships_added)} relationships")
        if self.relationships_removed:
            parts.append(f"-{len(self.relationships_removed)} relationships")
        return ", ".join(parts) if parts else "No changes"


def compute_semantic_diff(
    entities_a: Dict[str, Set[str]],
    entities_b: Dict[str, Set[str]],
    triples_a: Dict[str, List[tuple]],
    triples_b: Dict[str, List[tuple]],
) -> SemanticDiff:
    """
    Compute semantic diff between two ontology snapshots.

    Args:
        entities_a: Entities from version A (classes, properties, individuals).
        entities_b: Entities from version B.
        triples_a: Entity triples from version A.
        triples_b: Entity triples from version B.

    Returns:
        SemanticDiff object with all changes.
    """
    all_entities_a = (
        entities_a.get("classes", set())
        | entities_a.get("properties", set())
        | entities_a.get("individuals", set())
    )
    all_entities_b = (
        entities_b.get("classes", set())
        | entities_b.get("properties", set())
        | entities_b.get("individuals", set())
    )

    diff = SemanticDiff(
        entities_added=all_entities_b - all_entities_a,
        entities_removed=all_entities_a - all_entities_b,
    )

    # Find modified properties (same entity, different triples)
    common_entities = all_entities_a & all_entities_b
    for entity in common_entities:
        triples_a_entity = {
            (p, o) for p, o in triples_a.get(entity, [])
        }
        triples_b_entity = {
            (p, o) for p, o in triples_b.get(entity, [])
        }
        if triples_a_entity != triples_b_entity:
            added = list(triples_b_entity - triples_a_entity)
            removed = list(triples_a_entity - triples_b_entity)
            diff.properties_modified[entity] = [("added", added), ("removed", removed)]

    # Relationship changes (object properties between entities)
    def get_relationships(triples: Dict[str, List[tuple]]) -> Set[tuple]:
        rels = set()
        for entity, preds in triples.items():
            for p, o in preds:
                if "ObjectProperty" in p or "owl:ObjectProperty" in p:
                    continue
                if entity != o and not o.startswith("http://www.w3.org/"):
                    rels.add((entity, p, o))
        return rels

    rels_a = get_relationships(triples_a)
    rels_b = get_relationships(triples_b)
    diff.relationships_added = list(rels_b - rels_a)
    diff.relationships_removed = list(rels_a - rels_b)

    return diff
