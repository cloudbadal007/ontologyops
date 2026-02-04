"""Tests for version control module."""

import pytest

from ontologyops.version_control import OntologyVersionControl, SemanticDiff, MergeStrategy
from ontologyops.version_control.semantic_diff import compute_semantic_diff
from ontologyops.version_control.merge_strategies import merge_union, merge_intersection


class TestOntologyVersionControl:
    """Test OntologyVersionControl class."""

    def test_create_snapshot(
        self,
        sample_ontology_path,
        temp_storage,
    ) -> None:
        vc = OntologyVersionControl(
            str(sample_ontology_path),
            storage_path=str(temp_storage),
        )
        v1 = vc.create_snapshot(author="test@example.com", message="Initial")
        assert v1
        assert len(v1) == 16

    def test_snapshot_hash_deterministic(
        self,
        sample_ontology_path,
        temp_storage,
    ) -> None:
        vc = OntologyVersionControl(
            str(sample_ontology_path),
            storage_path=str(temp_storage),
        )
        v1 = vc.create_snapshot(author="a", message="m1")
        v2 = vc.create_snapshot(author="a", message="m2")
        assert v1 == v2

    def test_diff_added_entities(
        self,
        sample_ontology_path,
        sample_ontology_v2_content,
        temp_storage,
    ) -> None:
        vc = OntologyVersionControl(
            str(sample_ontology_path),
            storage_path=str(temp_storage / "vc"),
        )
        h_a = vc.create_snapshot(author="a", message="v1")
        sample_ontology_path.write_text(sample_ontology_v2_content)
        h_b = vc.create_snapshot(author="a", message="v2")
        diff = vc.diff(h_a, h_b)
        assert len(diff.entities_added) >= 1

    def test_diff_removed_entities(
        self,
        sample_ontology_path,
        sample_ontology_v2_content,
        temp_storage,
    ) -> None:
        vc = OntologyVersionControl(
            str(sample_ontology_path),
            storage_path=str(temp_storage / "vc"),
        )
        sample_ontology_path.write_text(sample_ontology_v2_content)
        h_b = vc.create_snapshot(author="a", message="v2")
        sample_ontology_path.write_text(
            """<?xml version="1.0"?>
<rdf:RDF xmlns="http://example.org/ontology#" xmlns:owl="http://www.w3.org/2002/07/owl#"
     xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
     xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">
    <owl:Ontology rdf:about="http://example.org/ontology"/>
    <owl:Class rdf:about="http://example.org/ontology#Customer">
        <rdfs:label>Customer</rdfs:label><rdfs:comment>Customer</rdfs:comment>
    </owl:Class>
</rdf:RDF>"""
        )
        h_a = vc.create_snapshot(author="a", message="v1")
        diff = vc.diff(h_b, h_a)
        assert len(diff.entities_removed) >= 1

    def test_merge_union_strategy(
        self,
        sample_ontology_path,
        sample_ontology_v2_content,
        temp_storage,
    ) -> None:
        vc = OntologyVersionControl(
            str(sample_ontology_path),
            storage_path=str(temp_storage / "vc"),
        )
        h_a = vc.create_snapshot(author="a", message="v1")
        sample_ontology_path.write_text(sample_ontology_v2_content)
        h_b = vc.create_snapshot(author="a", message="v2")
        merged = vc.merge(h_a, h_b, MergeStrategy.UNION)
        assert len(merged) > 0

    def test_rollback_to_previous_version(
        self,
        sample_ontology_path,
        temp_storage,
    ) -> None:
        vc = OntologyVersionControl(
            str(sample_ontology_path),
            storage_path=str(temp_storage),
        )
        h = vc.create_snapshot(author="a", message="v1")
        vc.rollback(h)
        # Should not raise
        vc2 = OntologyVersionControl(
            str(sample_ontology_path),
            storage_path=str(temp_storage),
        )
        assert len(vc2.list_versions()) >= 1

    def test_list_versions(
        self,
        sample_ontology_path,
        temp_storage,
    ) -> None:
        vc = OntologyVersionControl(
            str(sample_ontology_path),
            storage_path=str(temp_storage),
        )
        vc.create_snapshot(author="a", message="v1")
        versions = vc.list_versions()
        assert len(versions) >= 1
        assert versions[0].author == "a"
        assert versions[0].message == "v1"

    def test_export_history(
        self,
        sample_ontology_path,
        temp_storage,
    ) -> None:
        vc = OntologyVersionControl(
            str(sample_ontology_path),
            storage_path=str(temp_storage),
        )
        vc.create_snapshot(author="a", message="v1")
        history = vc.export_history()
        assert "versions" in history
        assert "ontology_path" in history
        assert len(history["versions"]) >= 1


class TestSemanticDiff:
    """Test SemanticDiff class."""

    def test_is_empty(self) -> None:
        d = SemanticDiff()
        assert d.is_empty() is True
        d.entities_added.add("http://example.org/X")
        assert d.is_empty() is False

    def test_to_dict(self) -> None:
        d = SemanticDiff(
            entities_added={"a"},
            entities_removed={"b"},
        )
        result = d.to_dict()
        assert "a" in result["entities_added"]
        assert "b" in result["entities_removed"]
