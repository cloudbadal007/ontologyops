"""Testing framework demo."""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from ontologyops import OntologyTestSuite

suite = OntologyTestSuite(str(Path(__file__).parent / "ontologies" / "supply_chain.owl"))
report = suite.run_all_tests()
print(f"Tests: {report.passed_tests}/{report.total_tests} passed")
if report.failed_tests:
    print("Failed:", report.failed_tests)
