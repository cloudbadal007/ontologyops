# Getting Started

## 5-Minute Quickstart

```python
from ontologyops import OntologyVersionControl

vc = OntologyVersionControl('my_ontology.owl')
v1 = vc.create_snapshot(author='you@example.com', message='Initial version')

# Make changes to ontology...

v2 = vc.create_snapshot(author='you@example.com', message='Added Customer entity')

# View semantic diff
diff = vc.diff(v1, v2)
print(f"Added: {diff.entities_added}")
print(f"Removed: {diff.entities_removed}")
```

## Running Tests

```python
from ontologyops import OntologyTestSuite

suite = OntologyTestSuite('my_ontology.owl')
report = suite.run_all_tests()
print(f"Passed: {report.passed_tests}/{report.total_tests}")
```

## Deployment

```python
from ontologyops import OntologyDeployer

deployer = OntologyDeployer(triple_store_url='http://localhost:7200')
result = deployer.deploy('my_ontology.owl', version='v1', environment='staging')
```
