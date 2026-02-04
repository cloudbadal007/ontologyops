"""Monitoring demo."""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from ontologyops import OntologyMonitor

monitor = OntologyMonitor(
    ontology_path=str(Path(__file__).parent / "ontologies" / "supply_chain.owl")
)
health = monitor.get_health_status()
print("Health:", health)
print("Schema drift:", monitor.check_schema_drift())
