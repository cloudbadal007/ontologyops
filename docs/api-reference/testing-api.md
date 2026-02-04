# Testing API

## OntologyTestSuite

- `test_ontology_is_valid_owl()` - OWL 2 DL validation
- `test_all_entities_have_descriptions()` - Description check
- `test_all_entities_have_labels()` - Label check
- `test_no_orphan_entities()` - Orphan detection
- `test_no_punning()` - Punning detection
- `test_business_rule(rule_name)` - Run business rule
- `test_schema_binding()` - Database binding validation
- `run_all_tests()` - Run full test suite

## TestReport

- `passed` - Overall pass/fail
- `total_tests` - Total count
- `passed_tests` - Passed count
- `failed_tests` - List of failed test names
- `duration_seconds` - Execution time
