# Security Policy

## Reporting A Vulnerability

If you discover a security issue, please do not open a public issue with exploit details.

Instead, describe:

- the affected area
- the impact
- how to reproduce it
- whether user data or secrets may be exposed

Until a dedicated security contact is configured, please report privately to the maintainer through a non-public channel.

## Scope Notes

This project may handle:

- resume files
- job descriptions
- user-provided API keys in local environments

Please be especially careful around:

- file upload handling
- secret storage
- prompt injection from untrusted documents
- unsafe export behavior
- any future external data connectors
