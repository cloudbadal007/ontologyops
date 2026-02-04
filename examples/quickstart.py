"""
5-Minute OntologyOps Quickstart
================================

This script demonstrates the core functionality of OntologyOps in under 5 minutes.
"""

import shutil
from pathlib import Path

# Ensure we can import from parent
sys_path = Path(__file__).resolve().parent.parent
if str(sys_path) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(sys_path))

# 1. Version Control
print("=" * 50)
print("STEP 1: Version Control")
print("=" * 50)

from ontologyops import OntologyVersionControl

base = Path(__file__).parent / "ontologies"
ontology_path = base / "supply_chain.owl"
work_path = base / "_work_supply_chain.owl"
shutil.copy(ontology_path, work_path)

vc = OntologyVersionControl(str(work_path))
v1 = vc.create_snapshot(
    author="demo@example.com",
    message="Initial extraction from Power BI",
)
print(f"✓ Created version: {v1}")

# Simulate changes - overwrite with v2
shutil.copy(base / "supply_chain_v2.owl", work_path)
v2 = vc.create_snapshot(
    author="demo@example.com",
    message="Added Subscription entity",
)

diff = vc.diff(v1, v2)
print(f"✓ Entities added: {len(diff.entities_added)}")
print(f"✓ Properties modified: {len(diff.properties_modified)}")

# 2. Testing
print("\n" + "=" * 50)
print("STEP 2: Automated Testing")
print("=" * 50)

from ontologyops import OntologyTestSuite

test_suite = OntologyTestSuite(str(ontology_path))  # Use original, not work copy
test_suite.test_ontology_is_valid_owl()
print("✓ OWL validation passed")

result = test_suite.test_all_entities_have_descriptions()
print(f"✓ All entities documented" if result.passed else f"⚠ {result.message}")

result = test_suite.test_no_orphan_entities()
print(f"✓ No orphan entities" if result.passed else f"⚠ {result.message}")

# 3. Deployment
print("\n" + "=" * 50)
print("STEP 3: Deployment")
print("=" * 50)

from ontologyops import OntologyDeployer

deployer = OntologyDeployer(
    triple_store_url="http://localhost:7200",
    agent_endpoints=[],
)

result = deployer.deploy(
    ontology_path=str(ontology_path),
    version=v2,
    environment="staging",
)

if result["success"]:
    print(f"✓ Deployed version {v2} to staging")
    print(f"✓ Deployment time: {result['duration_seconds']:.2f}s")
else:
    print(f"✗ Deployment failed: {result.get('error', 'check triple store')}")

# 4. Monitoring
print("\n" + "=" * 50)
print("STEP 4: Monitoring")
print("=" * 50)

from ontologyops import OntologyMonitor

monitor = OntologyMonitor(ontology_path=str(ontology_path))
health = monitor.get_health_status()
print(f"✓ Ontology health: {health['status']}")
print(f"✓ Entity count: {health['entity_count']}")
print(f"✓ Last validation: {health.get('last_validated', 'N/A')}")

drift_report = monitor.check_schema_drift("Shipment")
if drift_report["has_drift"]:
    print(f"⚠ Schema drift detected: {len(drift_report['issues'])} issues")
else:
    print("✓ No schema drift")

print("\n" + "=" * 50)
print("QUICKSTART COMPLETE!")
print("=" * 50)
print("\nNext steps:")
print("1. Read the full documentation: docs/getting-started.md")
print("2. Try the tutorials: docs/tutorials/")
print("3. Check out more examples: examples/")
