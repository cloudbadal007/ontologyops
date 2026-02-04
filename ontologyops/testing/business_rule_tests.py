"""Business rule testing for ontologies."""

import re
from typing import Any, Callable, Dict, List, Optional

from rdflib import Graph


class BusinessRuleTester:
    """
    Evaluates business rules against ontology.

    Supports rule evaluation, condition parsing, and action validation.
    """

    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self._rules: Dict[str, Dict[str, Any]] = {}

    def add_rule(
        self,
        name: str,
        condition: Callable[[Graph], bool],
        description: str = "",
    ) -> None:
        """
        Add a business rule to evaluate.

        Args:
            name: Rule identifier.
            condition: Callable that takes Graph and returns bool.
            description: Human-readable rule description.
        """
        self._rules[name] = {
            "condition": condition,
            "description": description,
        }

    def evaluate_rule(self, rule_name: str) -> bool:
        """
        Evaluate a single business rule.

        Args:
            rule_name: Name of the rule to evaluate.

        Returns:
            True if rule passes, False otherwise.
        """
        if rule_name not in self._rules:
            raise ValueError(f"Unknown rule: {rule_name}")
        return self._rules[rule_name]["condition"](self.graph)

    def evaluate_all(self) -> Dict[str, bool]:
        """
        Evaluate all registered rules.

        Returns:
            Dictionary mapping rule names to pass/fail.
        """
        return {
            name: rule["condition"](self.graph)
            for name, rule in self._rules.items()
        }

    def parse_condition(self, condition_str: str) -> Callable[[Graph], bool]:
        """
        Parse a condition string into a callable.

        Supports: "has_class X", "has_property X", "entity_count > N"

        Args:
            condition_str: Condition in supported format.

        Returns:
            Callable that evaluates the condition.
        """
        parts = condition_str.strip().split()
        if not parts:
            return lambda g: True

        if parts[0] == "has_class" and len(parts) >= 2:
            class_name = parts[1]
            return lambda g: self._has_class(g, class_name)

        if parts[0] == "has_property" and len(parts) >= 2:
            prop_name = parts[1]
            return lambda g: self._has_property(g, prop_name)

        if parts[0] == "entity_count" and len(parts) >= 3:
            op = parts[1]
            try:
                count = int(parts[2])
            except ValueError:
                return lambda g: False
            return lambda g: self._entity_count_check(g, op, count)

        return lambda g: False

    def _has_class(self, graph: Graph, class_name: str) -> bool:
        """Check if ontology contains a class with given name/local part."""
        from rdflib.namespace import OWL, RDF
        for s in graph.subjects(predicate=RDF.type, object=OWL.Class):
            if class_name in str(s):
                return True
        return False

    def _has_property(self, graph: Graph, prop_name: str) -> bool:
        """Check if ontology contains a property with given name."""
        from rdflib.namespace import OWL, RDF
        for s, _, _ in graph.triples((None, RDF.type, OWL.ObjectProperty)):
            if prop_name in str(s):
                return True
        for s, _, _ in graph.triples((None, RDF.type, OWL.DatatypeProperty)):
            if prop_name in str(s):
                return True
        return False

    def _entity_count_check(self, graph: Graph, op: str, count: int) -> bool:
        """Check entity count against threshold."""
        from ontologyops.utils.rdf_helpers import get_entities
        entities = get_entities(graph)
        total = sum(len(v) for v in entities.values())
        if op == ">":
            return total > count
        if op == ">=":
            return total >= count
        if op == "<":
            return total < count
        if op == "<=":
            return total <= count
        if op == "==":
            return total == count
        return False


def create_default_rules(tester: BusinessRuleTester) -> None:
    """Add common default business rules."""
    from rdflib.namespace import OWL, RDF

    def has_ontology_declaration(g: Graph) -> bool:
        return any(g.objects(predicate=RDF.type, object=OWL.Ontology))

    def has_at_least_one_class(g: Graph) -> bool:
        return any(g.subjects(predicate=RDF.type, object=OWL.Class))

    tester.add_rule("has_ontology", has_ontology_declaration, "Ontology has declaration")
    tester.add_rule("has_classes", has_at_least_one_class, "Ontology has at least one class")
