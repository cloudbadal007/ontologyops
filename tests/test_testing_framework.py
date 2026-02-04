"""Tests for testing framework module."""

import pytest

from ontologyops.testing import OntologyTestSuite
from ontologyops.testing.validators import SchemaValidator, ValidationResult
from ontologyops.testing.business_rule_tests import BusinessRuleTester, create_default_rules
from ontologyops.testing.integration_tests import (
    RDFLibAdapter,
    validate_schema_binding,
    validate_sparql_query,
)
from rdflib import Graph


class TestOntologyTestSuite:
    """Test OntologyTestSuite class."""

    def test_ontology_is_valid_owl(self, sample_ontology_path) -> None:
        suite = OntologyTestSuite(str(sample_ontology_path))
        result = suite.test_ontology_is_valid_owl()
        assert isinstance(result, ValidationResult)
        assert result.passed is True

    def test_all_entities_have_labels(self, sample_ontology_path) -> None:
        suite = OntologyTestSuite(str(sample_ontology_path))
        result = suite.test_all_entities_have_labels()
        assert isinstance(result, ValidationResult)

    def test_all_entities_have_descriptions(self, sample_ontology_path) -> None:
        suite = OntologyTestSuite(str(sample_ontology_path))
        result = suite.test_all_entities_have_descriptions()
        assert isinstance(result, ValidationResult)

    def test_no_orphan_entities(self, sample_ontology_path) -> None:
        suite = OntologyTestSuite(str(sample_ontology_path))
        result = suite.test_no_orphan_entities()
        assert isinstance(result, ValidationResult)

    def test_business_rule_evaluation(self, sample_ontology_path) -> None:
        suite = OntologyTestSuite(str(sample_ontology_path))
        assert suite.test_business_rule("has_ontology") is True
        assert suite.test_business_rule("has_classes") is True

    def test_schema_binding_validation(
        self,
        sample_ontology_path,
        test_database_path,
    ) -> None:
        suite = OntologyTestSuite(
            str(sample_ontology_path),
            database_path=str(test_database_path),
        )
        result = suite.test_schema_binding()
        assert "valid" in result

    def test_run_all_tests(self, sample_ontology_path) -> None:
        suite = OntologyTestSuite(str(sample_ontology_path))
        report = suite.run_all_tests()
        assert report.total_tests >= 1
        assert report.passed_tests >= 1
        assert report.duration_seconds >= 0


class TestSchemaValidator:
    """Test SchemaValidator."""

    def test_validate_owl_dl(self, sample_ontology_path) -> None:
        from ontologyops.utils.rdf_helpers import load_ontology
        graph = load_ontology(str(sample_ontology_path))
        validator = SchemaValidator(graph)
        result = validator.validate_owl_dl()
        assert result.passed is True


class TestBusinessRuleTester:
    """Test BusinessRuleTester."""

    def test_add_and_evaluate_rule(self, sample_ontology_path) -> None:
        from ontologyops.utils.rdf_helpers import load_ontology
        graph = load_ontology(str(sample_ontology_path))
        tester = BusinessRuleTester(graph)
        create_default_rules(tester)
        results = tester.evaluate_all()
        assert "has_ontology" in results
        assert results["has_ontology"] is True


class TestIntegration:
    """Test integration components."""

    def test_rdflib_adapter_load(self, sample_ontology_path) -> None:
        adapter = RDFLibAdapter()
        ok = adapter.load_ontology(str(sample_ontology_path))
        assert ok is True
        assert adapter.get_entity_count() >= 1

    def test_validate_sparql(self, sample_ontology_path) -> None:
        from ontologyops.utils.rdf_helpers import load_ontology
        graph = load_ontology(str(sample_ontology_path))
        ok = validate_sparql_query("SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 1", graph)
        assert ok is True
