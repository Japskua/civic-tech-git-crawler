# Security Policy

## Reporting a Vulnerability

If you believe you have found a security vulnerability in this project, please
**do not file a public issue.** Instead, report it privately by email to the
maintainer:

> **japskua@gmail.com**

Please include:

1. A clear description of the vulnerability and the impact you expect.
2. Steps to reproduce, ideally a minimal proof of concept.
3. The version / commit you observed it on.

You can expect an acknowledgement within a few working days. Once the issue is
understood, the maintainer will work with you on a fix and a coordinated
disclosure timeline.

## Scope

This project is a research crawler that talks to GitHub's API on the
contributor's behalf using a personal access token. Relevant categories of
security report include (but are not limited to):

- Token leakage through logs, exports, or error messages.
- Command-injection or path-traversal issues in the CLI or wrapper scripts.
- Dependency vulnerabilities exposing the runtime to remote execution.

## Supported Versions

Only the latest tagged release on `master` is actively supported. Pull requests
backporting security fixes to earlier versions are welcome but not guaranteed.
