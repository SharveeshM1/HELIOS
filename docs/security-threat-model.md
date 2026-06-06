# HELIOS Production Threat Model

## Trust Boundaries

- The browser is untrusted. Authentication uses an HttpOnly, `SameSite=Strict` session cookie; the frontend does not persist bearer tokens.
- The public API is untrusted. Production requires a distinct authentication secret, restricted CORS origins, rate limiting, role checks, and audit logging.
- API keys are service credentials with an explicit role. They do not bypass permission checks.
- Uploaded sources, URLs, tool inputs, and plugin code are untrusted content.
- Plugins are privileged extensions. They require integrity or HMAC signature verification, cannot replace built-in tools, cannot declare runtime dependencies, and execute in bounded subprocesses with a scrubbed environment.

## High-Risk Operations

Terminal commands, file changes, deployment, git writes, plugin upload/uninstall, user administration, and rollback are restricted by role and approval gates. Audit events and execution events record attempted actions, outcomes, durations, and failures.

## Production Requirements

- Use Postgres for multi-worker runtime state and durable jobs.
- Set unique, high-entropy values for `HELIOS_AUTH_SECRET`, `HELIOS_ADMIN_PASSWORD`, `HELIOS_API_KEY`, and `HELIOS_PLUGIN_SIGNING_KEY`.
- Set `HELIOS_AUTH_COOKIE_SECURE=true`, restrict `HELIOS_CORS_ORIGINS`, terminate TLS at the ingress, and rotate credentials through an external secret manager.
- Run API and worker containers as non-root with read-only application images and narrowly scoped writable volumes.
- Treat plugins as reviewed code. Subprocess isolation limits server-process impact but is not an operating-system sandbox; production deployments should additionally use container, seccomp, network, and filesystem policies.
- Review `/audit`, `/observability`, `/metrics`, and readiness checks before and after releases.

## Residual Risks

Model output can be incorrect or adversarially influenced by ingested content. Human approval remains required for risky actions. Provider outages can affect realtime voice and model-assisted planning, while deterministic fallbacks keep core workflows available.
