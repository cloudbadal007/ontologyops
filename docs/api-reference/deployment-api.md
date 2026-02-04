# Deployment API

## OntologyDeployer

- `deploy(ontology_path, version, environment)` - Deploy ontology
- `rollback(to_version, ontology_path)` - Rollback deployment
- `validate_deployment()` - Validate store connectivity
- `notify_agents(version, success)` - Send agent notification
- `get_deployment_status()` - Get deployment history

## Deployment Result

- `success` - Boolean
- `version` - Deployed version
- `environment` - Target environment
- `steps` - List of deployment steps
- `duration_seconds` - Deployment time
- `error` - Error message if failed
