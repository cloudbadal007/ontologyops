"""Alert management for ontology monitoring."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class AlertSeverity(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Alert:
    """Represents an alert event."""

    name: str
    message: str
    severity: AlertSeverity
    details: Dict[str, Any] = field(default_factory=dict)


class AlertManager:
    """
    Manages alerts for ontology monitoring.

    Supports configurable thresholds and handlers.
    """

    def __init__(self) -> None:
        self._handlers: List[Callable[[Alert], None]] = []
        self._alerts: List[Alert] = []

    def add_handler(self, handler: Callable[[Alert], None]) -> None:
        """Add alert handler (e.g., email, webhook)."""
        self._handlers.append(handler)

    def emit(self, alert: Alert) -> None:
        """Emit alert to all handlers."""
        self._alerts.append(alert)
        for h in self._handlers:
            try:
                h(alert)
            except Exception:
                pass

    def get_recent_alerts(self, limit: int = 100) -> List[Alert]:
        """Get recent alerts."""
        return self._alerts[-limit:]


def create_schema_drift_alert(entity: str, issues: List[str]) -> Alert:
    """Create alert for schema drift."""
    return Alert(
        name="schema_drift",
        message=f"Schema drift detected for {entity}",
        severity=AlertSeverity.WARNING,
        details={"entity": entity, "issues": issues},
    )


def create_deployment_failure_alert(version: str, error: str) -> Alert:
    """Create alert for deployment failure."""
    return Alert(
        name="deployment_failure",
        message=f"Deployment of {version} failed",
        severity=AlertSeverity.ERROR,
        details={"version": version, "error": error},
    )
