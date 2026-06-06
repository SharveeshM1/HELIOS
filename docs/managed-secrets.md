# HELIOS Managed Secrets

HELIOS production deployments use External Secrets Operator instead of checked-in env files.

## Kubernetes Flow

1. Install External Secrets Operator in the cluster.
2. Choose one provider template:
   - `ops/k8s/secretstore-aws.yaml`
   - `ops/k8s/secretstore-gcp.yaml`
   - `ops/k8s/secretstore-azure.yaml`
3. Render the template with the provider-specific environment variables.
4. Apply `ops/k8s/external-secret.yaml`.
5. Deploy `ops/k8s/helios.yaml`.

The ExternalSecret writes a Kubernetes Secret named `helios-secrets`; the HELIOS deployment consumes that Secret through `envFrom`.

## Required Remote Secret Keys

- `helios/auth-secret`
- `helios/admin-password`
- `helios/database-url`
- `helios/vector-database-url`
- `helios/plugin-signing-key`

Optional provider keys:

- `helios/openai-api-key`
- `helios/gemini-api-key`

Rotate secrets in the cloud secret manager. External Secrets Operator refreshes the in-cluster Secret on the configured interval.
