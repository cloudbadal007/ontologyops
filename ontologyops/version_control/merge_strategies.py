"""Merge strategies for ontology conflict resolution."""

from enum import Enum
from typing import Any, Dict, List, Set, Tuple

from rdflib import Graph


class MergeStrategy(Enum):
    """Available merge strategies for ontology conflicts."""

    UNION = "union"
    INTERSECTION = "intersection"
    MANUAL = "manual"


def merge_union(graph_a: Graph, graph_b: Graph) -> Graph:
    """
    Union merge: combine all triples from both graphs.

    Args:
        graph_a: First ontology graph.
        graph_b: Second ontology graph.

    Returns:
        New graph containing all triples from both.
    """
    result = Graph()
    for s, p, o in graph_a:
        result.add((s, p, o))
    for s, p, o in graph_b:
        result.add((s, p, o))
    return result


def merge_intersection(graph_a: Graph, graph_b: Graph) -> Graph:
    """
    Intersection merge: keep only triples present in both graphs.

    Args:
        graph_a: First ontology graph.
        graph_b: Second ontology graph.

    Returns:
        New graph containing only common triples.
    """
    triples_a = set(graph_a)
    triples_b = set(graph_b)
    result = Graph()
    for s, p, o in triples_a & triples_b:
        result.add((s, p, o))
    return result


def merge_manual(
    graph_a: Graph,
    graph_b: Graph,
    include_from_a: Set[Tuple[Any, Any, Any]],
    include_from_b: Set[Tuple[Any, Any, Any]],
) -> Graph:
    """
    Manual merge: explicitly specify which triples to include.

    Args:
        graph_a: First ontology graph.
        graph_b: Second ontology graph.
        include_from_a: Triples to include from graph_a.
        include_from_b: Triples to include from graph_b.

    Returns:
        New graph with selected triples.
    """
    result = Graph()
    for s, p, o in include_from_a:
        if (s, p, o) in graph_a:
            result.add((s, p, o))
    for s, p, o in include_from_b:
        if (s, p, o) in graph_b:
            result.add((s, p, o))
    return result


def detect_conflicts(
    entities_a: Dict[str, Set[str]],
    entities_b: Dict[str, Set[str]],
    triples_a: Dict[str, List[tuple]],
    triples_b: Dict[str, List[tuple]],
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Detect merge conflicts between two ontology versions.

    Args:
        entities_a: Entities from version A.
        entities_b: Entities from version B.
        triples_a: Triples from version A.
        triples_b: Triples from version B.

    Returns:
        Dictionary of conflict descriptions for resolution.
    """
    conflicts: Dict[str, List[Dict[str, Any]]] = {"entity": [], "property": []}

    all_a = (
        entities_a.get("classes", set())
        | entities_a.get("properties", set())
        | entities_a.get("individuals", set())
    )
    all_b = (
        entities_b.get("classes", set())
        | entities_b.get("properties", set())
        | entities_b.get("individuals", set())
    )

    # Entity-level conflicts (same name, different definition)
    common = all_a & all_b
    for entity in common:
        triples_a_e = {tuple(t) for t in triples_a.get(entity, [])}
        triples_b_e = {tuple(t) for t in triples_b.get(entity, [])}
        if triples_a_e != triples_b_e:
            conflicts["entity"].append({
                "entity": entity,
                "version_a_triples": len(triples_a_e),
                "version_b_triples": len(triples_b_e),
                "description": f"Entity {entity} modified in both versions",
            })

    return conflicts
