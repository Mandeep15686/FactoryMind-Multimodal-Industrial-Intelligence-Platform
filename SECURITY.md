# Security Policy

## Reporting a vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

Email: your-email@example.com  
Response time: within 48 hours.

## What to include
- Description of the vulnerability
- Steps to reproduce
- Affected component (API, agent, RAG, infra)
- Potential impact

## Scope
- Prompt injection vulnerabilities in agent inputs
- Secrets leaking via logs or API responses
- RBAC bypass in FastAPI routes
- Dependency vulnerabilities (please check `pip audit` first)
