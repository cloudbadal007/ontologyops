# CI/CD Setup

Use the provided GitHub Actions workflows:

- `.github/workflows/ci.yml` - Run tests on push/PR
- `.github/workflows/publish-pypi.yml` - Publish on release
- `.github/workflows/docs.yml` - Build documentation

Configure `PYPI_API_TOKEN` secret for PyPI publishing.
