# Monitoring API

## OntologyMonitor

- `monitor_query(query_fn)` - Execute query with metrics
- `check_schema_drift(entity)` - Check for schema drift
- `record_deployment(version, success)` - Record deployment
- `get_health_status()` - Get health status
- `export_metrics()` - Export Prometheus format

## Health Status

- `status` - healthy/degraded/unhealthy
- `entity_count` - Number of entities
- `last_validated` - Last validation timestamp
