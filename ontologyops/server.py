"""Minimal metrics server for Docker deployment."""

import os
import threading

try:
    from prometheus_client import start_http_server, REGISTRY
    from ontologyops.monitoring import OntologyMonitor
    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False


def main() -> None:
    """Start metrics server on configured port."""
    port = int(os.environ.get("PROMETHEUS_PORT", "9090"))
    if HAS_PROMETHEUS:
        start_http_server(port, registry=REGISTRY)
        print(f"OntologyOps metrics server on port {port}")
        while True:
            threading.Event().wait(60)
    else:
        print("OntologyOps ready (install prometheus-client for metrics)")
        while True:
            threading.Event().wait(60)


if __name__ == "__main__":
    main()
