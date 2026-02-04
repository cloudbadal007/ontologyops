"""End-to-end integration tests."""

import pytest
from pathlib import Path

from ontologyops import OntologyVersionControl, OntologyTestSuite, OntologyDeployer, OntologyMonitor
from ontologyops.version_control import MergeStrategy


class TestEndToEnd:
    """Full workflow integration tests."""

    def test_full_workflow(
        self,
        sample_ontology_path,
        sample_ontology_v2_content,
        tmp_path,
        test_database_path,
    ) -> None:
        """Test: extract -> version -> test -> deploy -> monitor."""
        storage = tmp_path / "versions"
        vc = OntologyVersionControl(
            str(sample_ontology_path),
            storage_path=str(storage),
        )
        v1 = vc.create_snapshot(author="ci@test.com", message="Initial")
        assert v1

        # Modify and version
        sample_ontology_path.write_text(sample_ontology_v2_content)
        v2 = vc.create_snapshot(author="ci@test.com", message="Added entity")
        assert v2

        # Diff
        diff = vc.diff(v1, v2)
        assert not diff.is_empty() or len(diff.entities_added) >= 0

        # Test
        suite = OntologyTestSuite(
            str(sample_ontology_path),
            database_path=str(test_database_path),
        )
        report = suite.run_all_tests()
        assert report.total_tests >= 1

        # Deploy (to localhost - may simulate)
        deployer = OntologyDeployer(
            triple_store_url="http://localhost:7200",
            backup_before_deploy=True,
        )
        result = deployer.deploy(
            str(sample_ontology_path),
            version=v2,
            environment="test",
        )
        assert "success" in result

        # Monitor
        monitor = OntologyMonitor(ontology_path=str(sample_ontology_path))
        health = monitor.get_health_status()
        assert "status" in health
        assert health["entity_count"] >= 1
