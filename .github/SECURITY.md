# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 1.0.x   | Yes                |
| < 1.0   | No                 |

## Reporting a Vulnerability

If you discover a security vulnerability in SiloPrompts, please report it responsibly.

**Do NOT open a public GitHub issue for security vulnerabilities.**

Instead, use [GitHub's private vulnerability reporting](https://github.com/bdharavathu/siloprompts/security/advisories/new) to submit your report securely.

### What to include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### What to expect

- Acknowledgment within 48 hours
- Status update within 7 days
- Credit in the fix release (unless you prefer anonymity)

## Security Design

SiloPrompts is designed with security in mind:

- **No cloud, no accounts** — your data never leaves your machine
- **Path traversal protection** — all file operations are validated against directory escape attacks
- **Input sanitization** — filenames and categories are restricted to `[a-zA-Z0-9_-]`
- **XSS prevention** — user content is escaped before rendering
- **Non-root Docker container** — runs as `siloprompts` user (UID 1000)
- **Health check** — built-in endpoint for container orchestration
- **No database** — no SQL injection surface; plain markdown files only
- **Size limits** — file uploads capped at 1MB (single) / 10MB (bulk) to prevent abuse
