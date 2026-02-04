# OntologyOps: Production Infrastructure for AI Agent Ontologies

[![CI](https://github.com/cloudbadal007/ontologyops/actions/workflows/ci.yml/badge.svg)](https://github.com/cloudbadal007/ontologyops/actions)
[![PyPI version](https://badge.fury.io/py/ontologyops.svg)](https://badge.fury.io/py/ontologyops)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

**Production-grade infrastructure for AI agent ontology version control, testing, and deployment**

## The Problem

OWL ontologies power AI systems, knowledge graphs, and semantic data integration. Yet deploying ontologies to production often lacks the DevOps practices we expect: version control tracks lines not meaning, testing is manual, and deployments can cause costly outages. A single ontology deployment error can cascade into multi-million dollar incidents.

## The Solution

OntologyOps brings DevOps best practices to ontology management:

- **Semantic version control** - Entity-level diffs, not line-level
- **Comprehensive testing** - Schema validation, business rules, integration tests
- **Automated CI/CD** - GitHub Actions pipelines ready to use
- **Real-time monitoring** - Prometheus metrics and Grafana dashboards
- **One-command deployment** - With automatic rollback on failure
- **Multi-triple-store support** - GraphDB, Fuseki, Stardog, Neptune

## Features

- Semantic version control (entity-level diffs, merge strategies)
- OWL 2 DL validation, punning detection, orphan checks
- Business rule testing framework
- Integration with triple stores and database schemas
- Pre-deployment validation and automatic backup
- Prometheus metrics and health monitoring
- AI agent notification hooks

## Quick Start (5 minutes)

```bash
pip install ontologyops
```

```python
from ontologyops import OntologyVersionControl

vc = OntologyVersionControl('my_ontology.owl')
v1 = vc.create_snapshot(author='you@example.com', message='Initial version')

# Make changes to your ontology...

v2 = vc.create_snapshot(author='you@example.com', message='Added Customer entity')

# View semantic diff
diff = vc.diff(v1, v2)
print(f"Added: {diff.entities_added}")
print(f"Removed: {diff.entities_removed}")
```

## Installation

```bash
pip install ontologyops
```

Or from source:

```bash
git clone https://github.com/cloudbadal007/ontologyops.git
cd ontologyops
pip install -e .
```

## Usage Examples

### Version Control
```python
from ontologyops import OntologyVersionControl
from ontologyops.version_control import MergeStrategy

vc = OntologyVersionControl('ontology.owl')
v1 = vc.create_snapshot(author='dev@example.com', message='v1')
# ... modify ontology ...
v2 = vc.create_snapshot(author='dev@example.com', message='v2')
diff = vc.diff(v1, v2)
merged = vc.merge(v1, v2, MergeStrategy.UNION)
```

### Testing
```python
from ontologyops import OntologyTestSuite

suite = OntologyTestSuite('ontology.owl')
report = suite.run_all_tests()
print(f"Passed: {report.passed_tests}/{report.total_tests}")
```

### Deployment
```python
from ontologyops import OntologyDeployer

deployer = OntologyDeployer(triple_store_url='http://localhost:7200')
result = deployer.deploy('ontology.owl', version='v1', environment='staging')
```

### Monitoring
```python
from ontologyops import OntologyMonitor

monitor = OntologyMonitor(ontology_path='ontology.owl')
health = monitor.get_health_status()
print(health)
```

## Documentation

- [Getting Started](docs/getting-started.md)
- [User Guide](docs/user-guide/version-control.md)
- [API Reference](docs/api-reference/version-control-api.md)
- [Architecture](docs/architecture.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

MIT License - see [LICENSE](LICENSE)

## Citation

```bibtex
@software{ontologyops2026,
  author = {Kumar, Pankaj},
  title = {OntologyOps: Production Infrastructure for OWL Ontologies},
  year = {2026},
  url = {https://github.com/cloudbadal007/ontologyops}
}
```

## Acknowledgments

Built with [RDFLib](https://github.com/RDFLib/rdflib), [PyTest](https://pytest.org/), and [Prometheus](https://prometheus.io/).
