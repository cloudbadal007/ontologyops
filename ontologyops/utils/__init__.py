"""Utility modules for OntologyOps."""

from ontologyops.utils.config import load_config
from ontologyops.utils.rdf_helpers import (
    load_ontology,
    save_ontology,
    get_entities,
    get_triples_for_entity,
)

__all__ = [
    "load_config",
    "load_ontology",
    "save_ontology",
    "get_entities",
    "get_triples_for_entity",
]
