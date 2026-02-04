"""Configuration management for OntologyOps."""

from pathlib import Path
from typing import Any, Dict, Optional

import yaml


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file or return defaults.

    Args:
        config_path: Path to configuration file. If None, uses default locations.

    Returns:
        Configuration dictionary with merged defaults.
    """
    defaults: Dict[str, Any] = {
        "version_control": {
            "storage_path": ".ontologyops/versions",
            "hash_algorithm": "sha256",
        },
        "deployment": {
            "triple_store_url": "http://localhost:7200",
            "timeout": 30,
            "backup_before_deploy": True,
        },
        "monitoring": {
            "prometheus_port": 9090,
            "health_check_interval": 60,
        },
    }

    if config_path is None:
        for path in [
            Path("config/example-config.yml"),
            Path("config.yml"),
            Path(".ontologyops/config.yml"),
        ]:
            if path.exists():
                config_path = str(path)
                break

    if config_path and Path(config_path).exists():
        with open(config_path, "r", encoding="utf-8") as f:
            user_config = yaml.safe_load(f) or {}
        return _deep_merge(defaults, user_config)

    return defaults


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge override dict into base."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result
