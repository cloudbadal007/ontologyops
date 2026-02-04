"""Health check implementations for ontology monitoring."""

from typing import Any, Dict

from ontologyops.utils.rdf_helpers import load_ontology, get_entities


def run_health_checks(ontology_path: str) -> Dict[str, Any]:
    """
    Run comprehensive health checks on ontology.

    Args:
        ontology_path: Path to ontology file.

    Returns:
        Health check results.
    """
    results: Dict[str, Any] = {
        "path": ontology_path,
        "checks": {},
        "overall": "healthy",
    }
    try:
        graph = load_ontology(ontology_path)
        entities = get_entities(graph)
        entity_count = sum(len(v) for v in entities.values())

        results["checks"]["loadable"] = True
        results["checks"]["entity_count"] = entity_count
        results["entity_count"] = entity_count

        if entity_count == 0:
            results["checks"]["has_entities"] = False
            results["overall"] = "degraded"
        else:
            results["checks"]["has_entities"] = True

    except Exception as e:
        results["checks"]["loadable"] = False
        results["overall"] = "unhealthy"
        results["error"] = str(e)
    return results
