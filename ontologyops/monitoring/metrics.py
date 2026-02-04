"""Prometheus metrics for ontology monitoring."""

from pathlib import Path
from typing import Any, Dict, Optional

from ontologyops.utils.rdf_helpers import load_ontology, get_entities
from ontologyops.testing.validators import SchemaValidator

try:
    from prometheus_client import (
        Counter,
        Gauge,
        Histogram,
        CollectorRegistry,
        generate_latest,
        CONTENT_TYPE_LATEST,
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


class OntologyMonitor:
    """
    Real-time monitoring with Prometheus integration.

    Tracks queries, schema drift, deployments, and health.
    """

    def __init__(
        self,
        ontology_path: Optional[str] = None,
        registry: Optional[Any] = None,
    ) -> None:
        """
        Initialize monitor.

        Args:
            ontology_path: Path to ontology for entity/drift checks.
            registry: Prometheus CollectorRegistry (uses default if None).
        """
        self.ontology_path = ontology_path
        self._registry = registry
        self._init_metrics()

    def _init_metrics(self) -> None:
        """Initialize Prometheus metrics."""
        if not PROMETHEUS_AVAILABLE:
            self._queries_total = None
            self._query_duration = None
            self._schema_drift_total = None
            self._entity_count = None
            self._deployment_success = None
            self._deployment_failures = None
            return

        registry = self._registry
        self._queries_total = Counter(
            "ontology_queries_total",
            "Total number of ontology queries",
            registry=registry,
        )
        self._query_duration = Histogram(
            "ontology_query_duration_seconds",
            "Ontology query duration in seconds",
            registry=registry,
        )
        self._schema_drift_total = Counter(
            "schema_drift_events_total",
            "Total schema drift events",
            registry=registry,
        )
        self._entity_count = Gauge(
            "entity_count",
            "Number of entities in ontology",
            registry=registry,
        )
        self._deployment_success = Counter(
            "deployment_success_total",
            "Successful deployments",
            registry=registry,
        )
        self._deployment_failures = Counter(
            "deployment_failures_total",
            "Failed deployments",
            registry=registry,
        )

    def monitor_query(self, query_fn: callable, *args, **kwargs) -> Any:
        """
        Execute query with timing and metrics.

        Args:
            query_fn: Callable to execute (e.g., SPARQL query).
            *args: Positional args for query_fn.
            **kwargs: Keyword args for query_fn.

        Returns:
            Result of query_fn.
        """
        if self._query_duration:
            with self._query_duration.time():
                result = query_fn(*args, **kwargs)
        else:
            result = query_fn(*args, **kwargs)
        if self._queries_total:
            self._queries_total.inc()
        return result

    def check_schema_drift(self, entity: Optional[str] = None) -> Dict[str, Any]:
        """
        Check for schema drift (changes from expected).

        Args:
            entity: Optional specific entity to check.

        Returns:
            Drift report with has_drift and issues.
        """
        if not self.ontology_path or not Path(self.ontology_path).exists():
            return {"has_drift": False, "issues": []}

        graph = load_ontology(self.ontology_path)
        validator = SchemaValidator(graph)
        issues: list = []

        for check in [
            validator.check_orphans,
            validator.check_punning,
            validator.check_circular_relationships,
        ]:
            result = check()
            if not result.passed:
                issues.append(result.message)
                if self._schema_drift_total:
                    self._schema_drift_total.inc()

        return {"has_drift": len(issues) > 0, "issues": issues}

    def record_deployment(self, version: str, success: bool) -> None:
        """
        Record deployment result in metrics.

        Args:
            version: Deployed version.
            success: Whether deployment succeeded.
        """
        if success and self._deployment_success:
            self._deployment_success.inc()
        elif not success and self._deployment_failures:
            self._deployment_failures.inc()

    def get_health_status(self) -> Dict[str, Any]:
        """
        Get overall health status.

        Returns:
            Health status dictionary.
        """
        status: Dict[str, Any] = {
            "status": "healthy",
            "entity_count": 0,
            "last_validated": None,
        }
        if not self.ontology_path or not Path(self.ontology_path).exists():
            return status

        try:
            graph = load_ontology(self.ontology_path)
            entities = get_entities(graph)
            status["entity_count"] = sum(len(v) for v in entities.values())
            if self._entity_count:
                self._entity_count.set(status["entity_count"])
            status["last_validated"] = "now"
        except Exception as e:
            status["status"] = "unhealthy"
            status["error"] = str(e)
        return status

    def export_metrics(self) -> bytes:
        """
        Export metrics in Prometheus format.

        Returns:
            Prometheus text format bytes.
        """
        if not PROMETHEUS_AVAILABLE:
            return b""
        return generate_latest()
