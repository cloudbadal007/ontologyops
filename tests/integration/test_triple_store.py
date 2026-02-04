"""Triple store integration tests."""

import pytest

from ontologyops.testing.integration_tests import RDFLibAdapter, validate_sparql_query
from ontologyops.utils.rdf_helpers import load_ontology


class TestTripleStore:
    """Test triple store adapters."""

    def test_rdflib_adapter_load_and_query(self, sample_ontology_path) -> None:
        adapter = RDFLibAdapter()
        assert adapter.load_ontology(str(sample_ontology_path)) is True
        results = adapter.query("SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 5")
        assert isinstance(results, list)
        assert len(results) >= 1

    def test_sparql_validation(self, sample_ontology_path) -> None:
        graph = load_ontology(str(sample_ontology_path))
        assert validate_sparql_query(
            "SELECT * WHERE { ?s ?p ?o } LIMIT 1",
            graph,
        ) is True
