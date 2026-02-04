"""Rollback capabilities for ontology deployment."""

import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ontologyops.utils.rdf_helpers import load_ontology, save_ontology


class RollbackManager:
    """
    Manages deployment rollbacks.

    Creates backups before deployment and supports rollback to previous versions.
    """

    def __init__(self, backup_dir: str = ".ontologyops/backups") -> None:
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self._history_file = self.backup_dir / "deployment_history.json"
        self._history: List[Dict[str, Any]] = []
        self._load_history()

    def _load_history(self) -> None:
        if self._history_file.exists():
            import json
            with open(self._history_file, "r", encoding="utf-8") as f:
                self._history = json.load(f)
        else:
            self._history = []

    def _save_history(self) -> None:
        import json
        with open(self._history_file, "w", encoding="utf-8") as f:
            json.dump(self._history, f, indent=2)

    def create_backup(
        self,
        ontology_path: str,
        version: str,
        environment: str,
    ) -> str:
        """
        Create backup before deployment.

        Args:
            ontology_path: Path to ontology file.
            version: Version being deployed.
            environment: Target environment.

        Returns:
            Path to backup file.
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{Path(ontology_path).stem}_{environment}_{version}_{timestamp}.owl"
        backup_path = self.backup_dir / backup_name
        shutil.copy(ontology_path, backup_path)

        self._history.append({
            "backup_path": str(backup_path),
            "ontology_path": ontology_path,
            "version": version,
            "environment": environment,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        })
        self._save_history()
        return str(backup_path)

    def rollback(
        self,
        ontology_path: str,
        to_version: Optional[str] = None,
        backup_path: Optional[str] = None,
    ) -> bool:
        """
        Rollback to previous version.

        Args:
            ontology_path: Path to restore to.
            to_version: Version to rollback to (uses latest backup if None).
            backup_path: Direct path to backup file.

        Returns:
            True if rollback succeeded.
        """
        if backup_path:
            source = Path(backup_path)
        else:
            matching = [
                h for h in reversed(self._history)
                if h["ontology_path"] == ontology_path
                and (to_version is None or h["version"] == to_version)
            ]
            if not matching:
                return False
            source = Path(matching[0]["backup_path"])

        if not source.exists():
            return False
        shutil.copy(source, ontology_path)
        return True
