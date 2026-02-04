"""RDF utility functions for ontology operations."""

from pathlib import Path
from typing import Dict, List, Set, Tuple

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import OWL, RDF, RDFS


def load_ontology(path: str) -> Graph:
    """
    Load an OWL ontology from file.

    Args:
        path: Path to the ontology file (.owl, .rdf, .ttl).

    Returns:
        RDFLib Graph containing the ontology.

    Raises:
        FileNotFoundError: If the ontology file does not exist.
    """
    path_obj = Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(f"Ontology file not found: {path}")

    graph = Graph()
    graph.parse(path, format=_infer_format(path))
    return graph


def save_ontology(graph: Graph, path: str, format: str = "xml") -> None:
    """
    Save an RDF graph to file.

    Args:
        graph: RDFLib Graph to save.
        path: Output file path.
        format: Output format (xml, turtle, n3, nt).
    """
    graph.serialize(destination=path, format=format)


def get_entities(graph: Graph) -> Dict[str, Set[str]]:
    """
    Extract all entities from ontology grouped by type.

    Args:
        graph: RDFLib Graph containing the ontology.

    Returns:
        Dictionary with keys 'classes', 'properties', 'individuals' mapping to
        sets of entity URIs (as strings).
    """
    classes: Set[str] = set()
    properties: Set[str] = set()
    individuals: Set[str] = set()

    for s, p, o in graph:
        subj = str(s) if isinstance(s, URIRef) else None
        pred = str(p)
        obj = str(o) if isinstance(o, URIRef) else None

        if pred == str(RDF.type):
            if obj == str(OWL.Class):
                if subj:
                    classes.add(subj)
            elif obj == str(OWL.ObjectProperty) or obj == str(OWL.DatatypeProperty):
                if subj:
                    properties.add(subj)
            elif obj and obj not in [str(OWL.Class), str(OWL.Thing)]:
                if subj and not subj.startswith("http://www.w3.org/"):
                    individuals.add(subj)

    # Also get classes from rdfs:subClassOf
    for s, p, o in graph.triples((None, RDFS.subClassOf, None)):
        if isinstance(s, URIRef) and str(s) not in classes:
            classes.add(str(s))

    return {"classes": classes, "properties": properties, "individuals": individuals}


def get_triples_for_entity(graph: Graph, entity_uri: str) -> List[Tuple[str, str, str]]:
    """
    Get all triples where the entity is subject or object.

    Args:
        graph: RDFLib Graph.
        entity_uri: URI of the entity.

    Returns:
        List of (subject, predicate, object) triples as strings.
    """
    results: List[Tuple[str, str, str]] = []
    entity_ref = URIRef(entity_uri)

    for s, p, o in graph:
        if s == entity_ref or o == entity_ref:
            results.append((str(s), str(p), str(o)))

    return results


def _infer_format(path: str) -> str:
    """Infer RDF format from file extension."""
    ext = Path(path).suffix.lower()
    mapping = {
        ".owl": "xml",
        ".rdf": "xml",
        ".xml": "xml",
        ".ttl": "turtle",
        ".n3": "n3",
        ".nt": "nt",
    }
    return mapping.get(ext, "xml")


def graph_to_dict(graph: Graph) -> Dict[str, List[Tuple[str, str]]]:
    """
    Convert graph to serializable dict format for version control.

    Args:
        graph: RDFLib Graph.

    Returns:
        Dictionary mapping entity URIs to list of (predicate, object) pairs.
    """
    entities: Dict[str, List[Tuple[str, str]]] = {}
    for s, p, o in graph:
        subj = str(s)
        if subj not in entities:
            entities[subj] = []
        entities[subj].append((str(p), str(o)))
    return entities
