"""Comprehensive ontology testing framework."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from rdflib import Graph

from ontologyops.utils.rdf_helpers import load_ontology, get_entities
from ontologyops.testing.validators import SchemaValidator, ValidationResult
from ontologyops.testing.business_rule_tests import (
    BusinessRuleTester,
    create_default_rules,
)
from ontologyops.testing.integration_tests import (
    RDFLibAdapter,
    validate_schema_binding,
    validate_sparql_query,
)


@dataclass
class TestReport:
    """Result of running the full test suite."""

    passed: bool
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)
    duration_seconds: float = 0.0


class OntologyTestSuite:
    """
    Comprehensive testing framework for OWL ontologies.

    Integrates schema validation, business rules, and integration tests.
    """

    def __init__(
        self,
        ontology_path: str,
        database_path: Optional[str] = None,
    ) -> None:
        """
        Initialize test suite for an ontology.

        Args:
            ontology_path: Path to the ontology file.
            database_path: Optional path to database for schema binding tests.
        """
        self.ontology_path = Path(ontology_path)
        self.database_path = database_path
        self._graph: Optional[Graph] = None
        self._validator: Optional[SchemaValidator] = None
        self._rule_tester: Optional[BusinessRuleTester] = None

    def _ensure_loaded(self) -> Graph:
        """Load ontology if not already loaded."""
        if self._graph is None:
            self._graph = load_ontology(str(self.ontology_path))
        return self._graph

    def test_ontology_is_valid_owl(self) -> ValidationResult:
        """
        Validate ontology conforms to OWL 2 DL.

        Returns:
            ValidationResult with pass/fail and details.
        """
        graph = self._ensure_loaded()
        if self._validator is None:
            self._validator = SchemaValidator(graph)
        return self._validator.validate_owl_dl()

    def test_all_entities_have_descriptions(self) -> ValidationResult:
        """
        Check that all entities have rdfs:comment or dcterms:description.

        Returns:
            ValidationResult with entities missing descriptions.
        """
        graph = self._ensure_loaded()
        if self._validator is None:
            self._validator = SchemaValidator(graph)
        return self._validator.check_descriptions()

    def test_all_entities_have_labels(self) -> ValidationResult:
        """
        Check that all entities have rdfs:label or skos:prefLabel.

        Returns:
            ValidationResult with entities missing labels.
        """
        graph = self._ensure_loaded()
        if self._validator is None:
            self._validator = SchemaValidator(graph)
        return self._validator.check_labels()

    def test_no_orphan_entities(self) -> ValidationResult:
        """
        Check for orphan entities not connected to ontology.

        Returns:
            ValidationResult with any orphan entities.
        """
        graph = self._ensure_loaded()
        if self._validator is None:
            self._validator = SchemaValidator(graph)
        return self._validator.check_orphans()

    def test_no_punning(self) -> ValidationResult:
        """
        Check for punning (same URI as multiple types).

        Returns:
            ValidationResult with any punning violations.
        """
        graph = self._ensure_loaded()
        if self._validator is None:
            self._validator = SchemaValidator(graph)
        return self._validator.check_punning()

    def test_no_circular_relationships(self) -> ValidationResult:
        """
        Check for circular subClassOf relationships.

        Returns:
            ValidationResult with any circular references.
        """
        graph = self._ensure_loaded()
        if self._validator is None:
            self._validator = SchemaValidator(graph)
        return self._validator.check_circular_relationships()

    def test_business_rule(self, rule_name: str) -> bool:
        """
        Run a specific business rule.

        Args:
            rule_name: Name of the rule to run.

        Returns:
            True if rule passes.
        """
        graph = self._ensure_loaded()
        if self._rule_tester is None:
            self._rule_tester = BusinessRuleTester(graph)
            create_default_rules(self._rule_tester)
        return self._rule_tester.evaluate_rule(rule_name)

    def test_schema_binding(
        self,
        entity: Optional[str] = None,
        database: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Validate ontology schema binding to database.

        Args:
            entity: Optional specific entity to check.
            database: Override database path.

        Returns:
            Validation result dictionary.
        """
        db_path = database or self.database_path
        if not db_path:
            return {"valid": False, "error": "No database path specified"}
        return validate_schema_binding(
            str(self.ontology_path), db_path
        )

    def test_sparql_query(self, sparql: str) -> bool:
        """
        Validate SPARQL query executes against ontology.

        Args:
            sparql: SPARQL query string.

        Returns:
            True if query executes successfully.
        """
        graph = self._ensure_loaded()
        return validate_sparql_query(sparql, graph)

    def run_all_tests(self) -> TestReport:
        """
        Run complete test suite.

        Returns:
            TestReport with all results.
        """
        import time
        start = time.time()
        failed: List[str] = []
        details: Dict[str, Any] = {}
        total = 0
        passed_count = 0

        tests = [
            ("OWL validity", lambda: self.test_ontology_is_valid_owl().passed),
            ("Entity descriptions", lambda: self.test_all_entities_have_descriptions().passed),
            ("Entity labels", lambda: self.test_all_entities_have_labels().passed),
            ("No orphans", lambda: self.test_no_orphan_entities().passed),
            ("No punning", lambda: self.test_no_punning().passed),
            ("No circular refs", lambda: self.test_no_circular_relationships().passed),
            ("Business rule: has_ontology", lambda: self.test_business_rule("has_ontology")),
            ("Business rule: has_classes", lambda: self.test_business_rule("has_classes")),
        ]

        for name, test_fn in tests:
            total += 1
            try:
                result = test_fn()
                details[name] = result
                if result:
                    passed_count += 1
                else:
                    failed.append(name)
            except Exception as e:
                failed.append(name)
                details[name] = str(e)

        if self.database_path:
            total += 1
            binding = self.test_schema_binding()
            details["schema_binding"] = binding
            if binding.get("valid", False):
                passed_count += 1
            else:
                failed.append("schema_binding")

        duration = time.time() - start
        return TestReport(
            passed=len(failed) == 0,
            total_tests=total,
            passed_tests=passed_count,
            failed_tests=failed,
            details=details,
            duration_seconds=duration,
        )
