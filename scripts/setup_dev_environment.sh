#!/bin/bash
# Setup development environment
set -e
pip install -e ".[dev]"
pre-commit install
echo "Development environment ready. Run: pytest"
