"""Ontology version control implementation."""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from rdflib import Graph

from ontologyops.utils.rdf_helpers import (
    load_ontology,
    save_ontology,
    get_entities,
    graph_to_dict,
)
from ontologyops.version_control.semantic_diff import (
    SemanticDiff,
    compute_semantic_diff,
)
from ontologyops.version_control.merge_strategies import (
    MergeStrategy,
    merge_union,
    merge_intersection,
    detect_conflicts,
)


@dataclass
class VersionInfo:
    """Information about a version snapshot."""

    version_hash: str
    author: str
    message: str
    timestamp: str
    entity_count: int


class OntologyVersionControl:
    """
    Version control for OWL ontologies with semantic snapshots.

    Provides entity-level versioning, semantic diff, and merge capabilities.
    """

    def __init__(
        self,
        ontology_path: str,
        storage_path: Optional[str] = None,
    ) -> None:
        """
        Initialize version control for an ontology.

        Args:
            ontology_path: Path to the ontology file.
            storage_path: Directory for version storage. Defaults to .ontologyops/versions.
        """
        self.ontology_path = Path(ontology_path)
        self.storage_path = Path(
            storage_path or ".ontologyops/versions"
        ) / self.ontology_path.stem
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._versions_file = self.storage_path / "versions.json"
        self._versions: List[Dict[str, Any]] = []
        self._load_versions()

    def _load_versions(self) -> None:
        """Load version history from storage."""
        if self._versions_file.exists():
            with open(self._versions_file, "r", encoding="utf-8") as f:
                self._versions = json.load(f)
        else:
            self._versions = []

    def _save_versions(self) -> None:
        """Persist version history to storage."""
        with open(self._versions_file, "w", encoding="utf-8") as f:
            json.dump(self._versions, f, indent=2)

    def _compute_hash(self, graph: Graph) -> str:
        """Compute deterministic hash for ontology content."""
        content = sorted(
            (str(s), str(p), str(o)) for s, p, o in graph
        )
        return hashlib.sha256(
            json.dumps(content, sort_keys=True).encode()
        ).hexdigest()[:16]

    def create_snapshot(
        self,
        author: str,
        message: str,
    ) -> str:
        """
        Create a semantic snapshot of the current ontology.

        Args:
            author: Author identifier (e.g., email).
            message: Commit message describing changes.

        Returns:
            Version hash of the created snapshot.
        """
        graph = load_ontology(str(self.ontology_path))
        version_hash = self._compute_hash(graph)
        entities = get_entities(graph)
        entity_count = sum(len(v) for v in entities.values())

        version_info = {
            "version_hash": version_hash,
            "author": author,
            "message": message,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "entity_count": entity_count,
        }
        self._versions.append(version_info)
        self._save_versions()

        snapshot_dir = self.storage_path / version_hash
        snapshot_dir.mkdir(exist_ok=True)
        snapshot_path = snapshot_dir / "ontology.owl"
        save_ontology(graph, str(snapshot_path))

        metadata_path = snapshot_dir / "metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    **version_info,
                    "entities": {k: list(v) for k, v in entities.items()},
                    "triples": graph_to_dict(graph),
                },
                f,
                indent=2,
            )

        return version_hash

    def diff(
        self,
        version_a: str,
        version_b: str,
    ) -> SemanticDiff:
        """
        Compute semantic diff between two versions.

        Args:
            version_a: Hash of first version.
            version_b: Hash of second version.

        Returns:
            SemanticDiff object with all changes.
        """
        meta_a = self._load_version_metadata(version_a)
        meta_b = self._load_version_metadata(version_b)
        if not meta_a or not meta_b:
            raise ValueError("Version not found")

        entities_a = {
            k: set(v) for k, v in meta_a.get("entities", {}).items()
        }
        entities_b = {
            k: set(v) for k, v in meta_b.get("entities", {}).items()
        }
        triples_a = meta_a.get("triples", {})
        triples_b = meta_b.get("triples", {})

        triples_a_list = {
            k: [(p, o) for p, o in v] for k, v in triples_a.items()
        }
        triples_b_list = {
            k: [(p, o) for p, o in v] for k, v in triples_b.items()
        }

        return compute_semantic_diff(
            entities_a, entities_b, triples_a_list, triples_b_list
        )

    def _load_version_metadata(self, version_hash: str) -> Optional[Dict]:
        """Load metadata for a version."""
        metadata_path = self.storage_path / version_hash / "metadata.json"
        if not metadata_path.exists():
            return None
        with open(metadata_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def merge(
        self,
        version_a: str,
        version_b: str,
        strategy: MergeStrategy = MergeStrategy.UNION,
    ) -> Graph:
        """
        Merge two ontology versions.

        Args:
            version_a: First version hash.
            version_b: Second version hash.
            strategy: Merge strategy (union, intersection, manual).

        Returns:
            Merged RDF Graph.
        """
        graph_a = self._load_version_graph(version_a)
        graph_b = self._load_version_graph(version_b)
        if not graph_a or not graph_b:
            raise ValueError("Version not found")

        if strategy == MergeStrategy.UNION:
            return merge_union(graph_a, graph_b)
        elif strategy == MergeStrategy.INTERSECTION:
            return merge_intersection(graph_a, graph_b)
        else:
            raise ValueError("Manual merge requires explicit triple selection")

    def rollback(self, version_hash: str) -> None:
        """
        Rollback ontology to a previous version.

        Args:
            version_hash: Target version to rollback to.
        """
        graph = self._load_version_graph(version_hash)
        if not graph:
            raise ValueError(f"Version not found: {version_hash}")
        save_ontology(graph, str(self.ontology_path))

    def _load_version_graph(self, version_hash: str) -> Optional[Graph]:
        """Load graph for a version."""
        ontology_path = self.storage_path / version_hash / "ontology.owl"
        if not ontology_path.exists():
            return None
        return load_ontology(str(ontology_path))

    def list_versions(self) -> List[VersionInfo]:
        """
        List all version snapshots.

        Returns:
            List of VersionInfo objects, newest first.
        """
        versions = []
        for v in reversed(self._versions):
            versions.append(
                VersionInfo(
                    version_hash=v["version_hash"],
                    author=v["author"],
                    message=v["message"],
                    timestamp=v["timestamp"],
                    entity_count=v.get("entity_count", 0),
                )
            )
        return versions

    def export_history(self) -> Dict[str, Any]:
        """
        Export full version history as JSON.

        Returns:
            Dictionary with version history and metadata.
        """
        return {
            "ontology_path": str(self.ontology_path),
            "versions": self._versions,
            "exported_at": datetime.utcnow().isoformat() + "Z",
        }
