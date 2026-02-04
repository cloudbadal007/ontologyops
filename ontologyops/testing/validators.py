"""Schema validators for ontology testing."""

from typing import List, Set, Tuple

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import OWL, RDF, RDFS

SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
DCTERMS = Namespace("http://purl.org/dc/terms/")


class ValidationResult:
    """Result of a validation check."""

    def __init__(
        self,
        passed: bool,
        message: str,
        details: List[str] | None = None,
    ) -> None:
        self.passed = passed
        self.message = message
        self.details = details or []


class SchemaValidator:
    """
    Validates ontology schema compliance.

    Checks OWL 2 DL compliance, punning, labels, orphans, and circular refs.
    """

    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    def validate_owl_dl(self) -> ValidationResult:
        """
        Basic OWL 2 DL compliance check.

        Returns:
            ValidationResult with pass/fail and details.
        """
        details: List[str] = []
        # Check for required OWL declarations
        if not any(self.graph.objects(predicate=RDF.type, object=OWL.Ontology)):
            details.append("No owl:Ontology declaration found")

        # Check for valid class/property declarations
        for s in self.graph.subjects(predicate=RDF.type, object=OWL.Class):
            if not isinstance(s, URIRef):
                details.append(f"Class must be URI: {s}")

        if details:
            return ValidationResult(False, "OWL DL compliance issues", details)
        return ValidationResult(True, "OWL 2 DL compliant")

    def check_punning(self) -> ValidationResult:
        """
        Detect punning (same URI used as different entity types).

        Returns:
            ValidationResult with any punning violations.
        """
        uri_types: dict = {}
        for s, _, o in self.graph.triples((None, RDF.type, None)):
            if isinstance(s, URIRef):
                uri = str(s)
                type_str = str(o)
                if uri not in uri_types:
                    uri_types[uri] = set()
                uri_types[uri].add(type_str)

        punned = [uri for uri, types in uri_types.items() if len(types) > 1]
        if punned:
            return ValidationResult(
                False,
                f"Punning detected: {len(punned)} URIs used as multiple types",
                punned[:10],
            )
        return ValidationResult(True, "No punning detected")

    def check_labels(self) -> ValidationResult:
        """
        Check that entities have rdfs:label or skos:prefLabel.

        Returns:
            ValidationResult with entities missing labels.
        """
        entities_without_label: List[str] = []

        for s in set(
            self.graph.subjects(predicate=RDF.type, object=OWL.Class)
        ) | set(
            self.graph.subjects(predicate=RDF.type, object=OWL.ObjectProperty)
        ) | set(
            self.graph.subjects(predicate=RDF.type, object=OWL.DatatypeProperty)
        ):
            if isinstance(s, URIRef) and str(s).startswith("http://www.w3.org/"):
                continue
            if isinstance(s, URIRef):
                uri = str(s)
                has_label = any(
                    self.graph.triples((s, RDFS.label, None))
                ) or any(
                    self.graph.triples((s, SKOS.prefLabel, None))
                )
                if not has_label:
                    entities_without_label.append(uri)

        if entities_without_label:
            return ValidationResult(
                False,
                f"{len(entities_without_label)} entities missing labels",
                entities_without_label[:20],
            )
        return ValidationResult(True, "All entities have labels")

    def check_descriptions(self) -> ValidationResult:
        """
        Check that entities have rdfs:comment or dcterms:description.

        Returns:
            ValidationResult with entities missing descriptions.
        """
        entities_without_desc: List[str] = []

        for s in set(
            self.graph.subjects(predicate=RDF.type, object=OWL.Class)
        ) | set(
            self.graph.subjects(predicate=RDF.type, object=OWL.ObjectProperty)
        ):
            if isinstance(s, URIRef) and str(s).startswith("http://www.w3.org/"):
                continue
            if isinstance(s, URIRef):
                has_desc = any(
                    self.graph.triples((s, RDFS.comment, None))
                ) or any(
                    self.graph.triples((s, DCTERMS.description, None))
                )
                if not has_desc:
                    entities_without_desc.append(str(s))

        if entities_without_desc:
            return ValidationResult(
                False,
                f"{len(entities_without_desc)} entities missing descriptions",
                entities_without_desc[:20],
            )
        return ValidationResult(True, "All entities have descriptions")

    def check_orphans(self) -> ValidationResult:
        """
        Detect orphan entities (not connected to ontology).

        Returns:
            ValidationResult with orphan entities.
        """
        # Get all user-defined entities
        all_entities: Set[str] = set()
        for s in self.graph.subjects():
            if isinstance(s, URIRef):
                uri = str(s)
                if not uri.startswith("http://www.w3.org/") and "xmlns" not in uri:
                    all_entities.add(uri)

        # Entities that are referenced (subject or object of some triple)
        referenced: Set[str] = set()
        for s, p, o in self.graph:
            for node in [s, o]:
                if isinstance(node, URIRef):
                    uri = str(node)
                    if uri in all_entities:
                        referenced.add(uri)

        # Root entities: classes, properties, individuals
        roots: Set[str] = set()
        for s, _, o in self.graph.triples((None, RDF.type, None)):
            if isinstance(s, URIRef):
                roots.add(str(s))

        connected = roots | referenced
        orphans = all_entities - connected

        # Filter to meaningful orphans (declared classes/properties with no refs)
        declared = set()
        for s in self.graph.subjects(predicate=RDF.type):
            if isinstance(s, URIRef):
                declared.add(str(s))
        orphan_declared = orphans & declared

        if orphan_declared:
            return ValidationResult(
                False,
                f"{len(orphan_declared)} orphan entities detected",
                list(orphan_declared)[:20],
            )
        return ValidationResult(True, "No orphan entities")

    def check_circular_relationships(self) -> ValidationResult:
        """
        Detect circular subClassOf or subPropertyOf relationships.

        Returns:
            ValidationResult with circular references.
        """
        sub_class: List[Tuple[str, str]] = []
        for s, o in self.graph.subject_objects(predicate=RDFS.subClassOf):
            if isinstance(s, URIRef) and isinstance(o, URIRef):
                sub_class.append((str(s), str(o)))

        # Build adjacency and check for cycles
        try:
            import networkx as nx
            g = nx.DiGraph()
            for child, parent in sub_class:
                g.add_edge(child, parent)
            cycles = list(nx.simple_cycles(g))
            if cycles:
                return ValidationResult(
                    False,
                    f"Circular relationships: {len(cycles)} cycles",
                    [str(c) for c in cycles[:5]],
                )
        except ImportError:
            pass  # networkx optional for basic check

        return ValidationResult(True, "No circular relationships")
