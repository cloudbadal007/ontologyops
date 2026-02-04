"""Version control module for OWL ontologies."""

from ontologyops.version_control.ontology_version_control import OntologyVersionControl
from ontologyops.version_control.semantic_diff import SemanticDiff
from ontologyops.version_control.merge_strategies import MergeStrategy

__all__ = ["OntologyVersionControl", "SemanticDiff", "MergeStrategy"]
