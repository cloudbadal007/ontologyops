#!/bin/bash
# Run test suite
set -e
pytest --cov=ontologyops --cov-report=term-missing -v
