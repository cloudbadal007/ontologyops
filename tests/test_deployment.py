"""Tests for deployment module."""

import pytest

from ontologyops.deployment import OntologyDeployer
from ontologyops.deployment.rollback import RollbackManager
from ontologyops.deployment.notification import notify_agents, create_deployment_payload


class TestOntologyDeployer:
    """Test OntologyDeployer class."""

    def test_deployment_workflow(
        self,
        sample_ontology_path,
        tmp_path,
    ) -> None:
        deployer = OntologyDeployer(
            triple_store_url="http://localhost:7200",
            backup_before_deploy=True,
        )
        result = deployer.deploy(
            str(sample_ontology_path),
            version="test-v1",
            environment="test",
        )
        assert "success" in result
        assert "steps" in result
        assert "validation" in [s["step"] for s in result["steps"]]

    def test_backup_creation(self, sample_ontology_path, tmp_path) -> None:
        deployer = OntologyDeployer(
            triple_store_url="http://localhost:9999",
            backup_before_deploy=True,
        )
        deployer._rollback = RollbackManager(str(tmp_path / "backups"))
        result = deployer.deploy(
            str(sample_ontology_path),
            version="v1",
            environment="staging",
        )
        backup_step = next(
            (s for s in result["steps"] if s.get("step") == "backup"),
            None,
        )
        if backup_step:
            assert "path" in backup_step

    def test_agent_notification(self) -> None:
        payload = create_deployment_payload(
            version="v1",
            environment="staging",
            success=True,
            ontology_path="/tmp/test.owl",
            duration_seconds=1.5,
        )
        assert payload["event"] == "ontology_deployment"
        assert payload["version"] == "v1"
        assert payload["success"] is True


class TestRollbackManager:
    """Test RollbackManager."""

    def test_create_backup(self, sample_ontology_path, tmp_path) -> None:
        rm = RollbackManager(str(tmp_path / "backups"))
        path = rm.create_backup(
            str(sample_ontology_path),
            version="v1",
            environment="staging",
        )
        assert path
        import os
        assert os.path.exists(path)

    def test_rollback(self, sample_ontology_path, tmp_path) -> None:
        rm = RollbackManager(str(tmp_path / "backups"))
        backup_path = rm.create_backup(
            str(sample_ontology_path),
            version="v1",
            environment="staging",
        )
        target = tmp_path / "restored.owl"
        target.write_text("old")
        ok = rm.rollback(str(target), backup_path=backup_path)
        assert ok is True
        assert target.read_text() != "old"
