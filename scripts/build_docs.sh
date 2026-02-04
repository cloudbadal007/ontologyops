#!/bin/bash
# Build documentation
set -e
pip install mkdocs mkdocs-material mkdocstrings[python]
mkdocs build
