# Contributing to OntologyOps

## Development Setup

```bash
git clone https://github.com/cloudbadal007/ontologyops.git
cd ontologyops
pip install -e ".[dev]"
pre-commit install
```

## Code Style

- **Black** - Line length 100
- **isort** - Profile black
- **flake8** - Max line length 100, E203/W503 ignored

```bash
black ontologyops/ tests/
isort ontologyops/ tests/
flake8 ontologyops/ tests/
```

## Testing

```bash
pytest --cov=ontologyops
```

Coverage must remain above 85%. Add tests for new features.

## Pull Request Process

1. Create feature branch from `main`
2. Add/update tests
3. Ensure all tests pass
4. Update documentation
5. Submit PR with description
6. Address review feedback

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Tests

## Branch Naming

- `feature/short-description`
- `fix/issue-number`
- `docs/topic`
