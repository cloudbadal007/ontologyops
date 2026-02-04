# Monitoring

## Prometheus Metrics

- `ontology_queries_total` - Query count
- `ontology_query_duration_seconds` - Query latency
- `schema_drift_events_total` - Drift events
- `entity_count` - Ontology entity count
- `deployment_success_total` - Successful deployments
- `deployment_failures_total` - Failed deployments

## Health Checks

```python
monitor = OntologyMonitor(ontology_path='ontology.owl')
health = monitor.get_health_status()
```

## Schema Drift

```python
report = monitor.check_schema_drift()
if report['has_drift']:
    print(report['issues'])
```
