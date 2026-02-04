# Version Control API

## OntologyVersionControl

- `create_snapshot(author, message)` - Create version snapshot
- `diff(version_a, version_b)` - Compute semantic diff
- `merge(version_a, version_b, strategy)` - Merge versions
- `rollback(version_hash)` - Rollback to version
- `list_versions()` - List all versions
- `export_history()` - Export version history as JSON

## SemanticDiff

- `entities_added` - Set of added entity URIs
- `entities_removed` - Set of removed entity URIs
- `properties_modified` - Dict of modified properties
- `is_empty()` - Check if no changes
- `to_dict()` - Export as JSON-serializable dict
