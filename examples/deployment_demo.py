"""Deployment demo."""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from ontologyops import OntologyDeployer

deployer = OntologyDeployer(triple_store_url="http://localhost:7200")
result = deployer.deploy(
    str(Path(__file__).parent / "ontologies" / "supply_chain.owl"),
    version="demo-v1",
    environment="staging",
)
print("Success:" if result["success"] else "Failed:", result.get("error", ""))
