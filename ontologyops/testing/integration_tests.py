"""Integration testing for ontologies."""

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from rdflib import Graph

from ontologyops.utils.rdf_helpers import get_entities, load_ontology


class TripleStoreAdapter:
    """Abstract adapter for triple store operations."""

    def load_ontology(self, path: str) -> bool:
        """Load ontology into store. Returns success."""
        raise NotImplementedError

    def query(self, sparql: str) -> List[Dict[str, Any]]:
        """Execute SPARQL query. Returns list of result dicts."""
        raise NotImplementedError

    def get_entity_count(self) -> int:
        """Get total entity count in store."""
        raise NotImplementedError


class RDFLibAdapter(TripleStoreAdapter):
    """In-memory adapter using RDFLib for testing."""

    def __init__(self) -> None:
        self._graph = Graph()

    def load_ontology(self, path: str) -> bool:
        try:
            self._graph = load_ontology(path)
            return True
        except Exception:
            return False

    def query(self, sparql: str) -> List[Dict[str, Any]]:
        try:
            results = self._graph.query(sparql)
            return [
                {str(k): str(v) for k, v in row.asdict().items()}
                for row in results
            ]
        except Exception:
            return []

    def get_entity_count(self) -> int:
        entities = get_entities(self._graph)
        return sum(len(v) for v in entities.values())


def validate_schema_binding(
    ontology_path: str,
    database_path: str,
    binding_config: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Validate ontology entities map to database schema.

    Args:
        ontology_path: Path to ontology file.
        database_path: Path to SQLite database.
        binding_config: Optional mapping of entity URI to table.column.

    Returns:
        Validation result with matches and mismatches.
    """
    graph = load_ontology(ontology_path)
    entities = get_entities(graph)
    all_entities = (
        entities.get("classes", set())
        | entities.get("properties", set())
        | entities.get("individuals", set())
    )

    result: Dict[str, Any] = {
        "valid": True,
        "checked": len(all_entities),
        "bound": 0,
        "unbound": [],
        "database_tables": [],
    }

    if not Path(database_path).exists():
        result["valid"] = False
        result["error"] = "Database file not found"
        return result

    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = [row[0] for row in cursor.fetchall()]
        result["database_tables"] = tables
        conn.close()
    except Exception as e:
        result["valid"] = False
        result["error"] = str(e)
        return result

    if binding_config:
        for entity in all_entities:
            local = entity.split("/")[-1].split("#")[-1]
            if entity in binding_config or local in str(binding_config):
                result["bound"] += 1
            else:
                result["unbound"].append(entity)
        result["valid"] = len(result["unbound"]) == 0
    else:
        result["bound"] = len(all_entities)

    return result


def validate_sparql_query(sparql: str, graph: Graph) -> bool:
    """
    Validate SPARQL query syntax and execution.

    Args:
        sparql: SPARQL query string.
        graph: Graph to query.

    Returns:
        True if query executes successfully.
    """
    try:
        graph.query(sparql)
        return True
    except Exception:
        return False
