"""Tests for monitoring module."""

import pytest

from ontologyops.monitoring import OntologyMonitor
from ontologyops.monitoring.health_checks import run_health_checks
from ontologyops.monitoring.alerting import Alert, AlertSeverity, AlertManager


class TestOntologyMonitor:
    """Test OntologyMonitor class."""

    def test_monitor_initialization(self) -> None:
        monitor = OntologyMonitor()
        assert monitor is not None

    def test_get_health_status(self, sample_ontology_path) -> None:
        monitor = OntologyMonitor(ontology_path=str(sample_ontology_path))
        health = monitor.get_health_status()
        assert "status" in health
        assert health["entity_count"] >= 1

    def test_check_schema_drift(self, sample_ontology_path) -> None:
        monitor = OntologyMonitor(ontology_path=str(sample_ontology_path))
        report = monitor.check_schema_drift()
        assert "has_drift" in report
        assert "issues" in report

    def test_record_deployment(self) -> None:
        monitor = OntologyMonitor()
        monitor.record_deployment("v1", success=True)
        monitor.record_deployment("v2", success=False)
        # Should not raise

    def test_export_metrics(self) -> None:
        monitor = OntologyMonitor()
        data = monitor.export_metrics()
        assert isinstance(data, bytes)


class TestHealthChecks:
    """Test health checks."""

    def test_run_health_checks(self, sample_ontology_path) -> None:
        result = run_health_checks(str(sample_ontology_path))
        assert result["overall"] in ("healthy", "degraded", "unhealthy")
        assert "checks" in result
        assert result["checks"].get("loadable") is True


class TestAlerting:
    """Test alert management."""

    def test_alert_creation(self) -> None:
        alert = Alert(
            name="test",
            message="Test message",
            severity=AlertSeverity.WARNING,
        )
        assert alert.severity == AlertSeverity.WARNING

    def test_alert_manager(self) -> None:
        manager = AlertManager()
        alerts_received = []

        def handler(a: Alert) -> None:
            alerts_received.append(a)

        manager.add_handler(handler)
        manager.emit(Alert("x", "msg", AlertSeverity.INFO))
        assert len(alerts_received) == 1
        assert alerts_received[0].name == "x"
