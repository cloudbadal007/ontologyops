# Version Control

OntologyOps provides semantic version control for OWL ontologies.

## Creating Snapshots

```python
vc = OntologyVersionControl('ontology.owl')
hash = vc.create_snapshot(author='dev@example.com', message='Added Product class')
```

## Semantic Diff

Entity-level comparison between versions:

```python
diff = vc.diff(version_a_hash, version_b_hash)
print(diff.entities_added)
print(diff.entities_removed)
print(diff.properties_modified)
```

## Merge Strategies

- **Union** - Combine all triples from both versions
- **Intersection** - Keep only common triples
- **Manual** - Specify which triples to include

## Rollback

```python
vc.rollback(version_hash)
```
