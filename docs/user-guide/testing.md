# Testing

## Schema Validation

- OWL 2 DL compliance
- Punning detection
- Missing labels/descriptions
- Orphan entity detection
- Circular relationship detection

## Business Rules

```python
suite = OntologyTestSuite('ontology.owl')
suite.test_business_rule('has_ontology')
suite.test_business_rule('has_classes')
```

## Integration Tests

- Database schema binding
- SPARQL query validation
- Triple store loading
