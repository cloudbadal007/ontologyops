# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: security@ontologyops.dev (or cloudpankaj@example.com)

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

Please include:

- Type of issue (e.g., buffer overflow, SQL injection, cross-site scripting)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

## Security Best Practices

When using OntologyOps:

1. **Triple Store Access**: Always use authentication for triple store connections
2. **API Tokens**: Never commit API tokens or credentials to version control
3. **Agent Endpoints**: Use HTTPS for all agent notification endpoints
4. **Configuration Files**: Store sensitive config in environment variables
5. **Deployment**: Run with minimal required permissions

## Disclosure Policy

We follow coordinated vulnerability disclosure:

1. We acknowledge receipt within 48 hours
2. We confirm the vulnerability and determine affected versions
3. We prepare a fix and release it as quickly as possible
4. We publicly disclose the vulnerability after the fix is deployed

## Security Hall of Fame

We recognize security researchers who help keep OntologyOps secure:

[List of security researchers]
