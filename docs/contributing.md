# Contributing

## Setup

```bash
git clone https://github.com/cloudbadal007/ontologyops.git
cd ontologyops
pip install -e ".[dev]"
pre-commit install
```

## Code Style

- Black (line length 100)
- isort (profile black)
- flake8

## Testing

```bash
pytest --cov=ontologyops
```

Coverage must remain above 85%.

## Pull Request Process

1. Fork and create feature branch
2. Add tests
3. Ensure all tests pass
4. Update documentation
5. Submit PR with description
