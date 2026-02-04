#!/bin/bash
# Release script - tag and push
set -e
VERSION=${1:-}
if [ -z "$VERSION" ]; then
  echo "Usage: ./release.sh VERSION"
  exit 1
fi
git tag v$VERSION
git push origin main --tags
