"""Agent notification system for deployment events."""

import json
from typing import Any, Dict, List

import requests


def notify_agents(
    endpoints: List[str],
    payload: Dict[str, Any],
    timeout: int = 10,
) -> List[Dict[str, Any]]:
    """
    Send deployment notification to agent endpoints.

    Args:
        endpoints: List of agent notification URLs.
        payload: Notification payload (version, status, etc.).
        timeout: Request timeout in seconds.

    Returns:
        List of response status per endpoint.
    """
    results: List[Dict[str, Any]] = []
    for url in endpoints:
        try:
            resp = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=timeout,
            )
            results.append({
                "endpoint": url,
                "status_code": resp.status_code,
                "success": 200 <= resp.status_code < 300,
            })
        except requests.RequestException as e:
            results.append({
                "endpoint": url,
                "success": False,
                "error": str(e),
            })
    return results


def create_deployment_payload(
    version: str,
    environment: str,
    success: bool,
    ontology_path: str,
    duration_seconds: float,
    message: str = "",
) -> Dict[str, Any]:
    """Create standard deployment notification payload."""
    return {
        "event": "ontology_deployment",
        "version": version,
        "environment": environment,
        "success": success,
        "ontology_path": ontology_path,
        "duration_seconds": duration_seconds,
        "message": message,
    }
