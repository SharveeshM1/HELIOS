# HELIOS

HELIOS is an AI operating workspace with a FastAPI backend, Streamlit control app, and Next.js dashboard. It combines local model routing, persistent memory, source indexing, realtime voice hooks, and module-specific agent surfaces.

## Recruiter-Visible Engineering Highlights

- FastAPI API layer with typed request/response contracts for chat and source indexing.
- Health endpoint with runtime metadata, provider status, uptime, request count, memory stats, and source stats.
- Durable JSON persistence with atomic writes and backup recovery for chat memory.
- Source library indexing with deterministic content fingerprints, scoped retrieval, snippets, and match terms.
- Cognitive engine traces that expose plan, agent, synthesis, and memory stages to the frontend.
- Next.js command dashboard for modules, run ledger, health, sources, voice, and agent orchestration.
- Mission control ledger with create, advance, run, archive, agent activity, and artifact contracts.
- Streamlit app compatibility shims so backend modules remain testable outside a live Streamlit process.
- Local-first AI provider strategy with Ollama defaults and Gemini fallback support.
- Test coverage for memory, source ranking, and API contract behavior.

## Backend Quick Start

```bash
cd backend
python -m venv venv
venv/bin/pip install -r requirements.txt fastapi uvicorn pytest httpx
venv/bin/uvicorn backend.server:app --reload
```

The API defaults to `http://localhost:8000`.

## Frontend Quick Start

```bash
cd frontend
npm install
npm run dev
```

The frontend defaults to `http://localhost:3000` and reads the backend URL from `NEXT_PUBLIC_HELIOS_API_URL`.

## Useful Endpoints

- `GET /health` returns backend, AI provider, cognitive engine, and source-library status.
- `GET /ready` reports whether durable storage, authentication, admin credentials, and CORS are production-ready.
- `GET /voice/status` reports realtime voice readiness, model, and configured voice.
- `POST /auth/login` issues a signed user token when production auth is configured.
- `POST /auth/users` creates viewer, operator, or admin users.
- `GET /metrics` exposes Prometheus-compatible runtime counters.
- `GET /autonomy/jobs` reports durable worker jobs and lease state.
- `POST /code/repair` applies structured bounded edits and retries verification.
- `POST /code/repair/auto` asks the configured model to propose bounded edits, verifies them, and retries with failure context.
- `GET /git/status` previews repository status.
- `POST /git/commit` commits already-staged files only when `confirm=true`.
- `GET /observability` reports execution-ledger failure pressure, slow tools, and recommendations.
- `GET /project/brain` returns the Project Brain graph of memory, sources, missions, and execution.
- `POST /chat` sends a module-scoped message through HELIOS.
- `GET /missions/events?limit=40` returns mission timeline events, latest mission summaries, mission stats, and agent activity.
- `POST /missions` creates a mission and records Created/Assigned ledger events.
- `POST /missions/{mission_id}/advance` records an operational stage such as Executed, Reviewed, or Archived.
- `POST /missions/{mission_id}/run` executes the mission workflow and returns a module-specific artifact plus task telemetry.
- `GET /sources` lists indexed knowledge sources.
- `GET /sources/search?q=...` searches indexed sources with snippets and match terms.
- `POST /sources` indexes a project or chat-scoped source.
- `POST /realtime/session` starts a realtime voice bridge when `OPENAI_API_KEY` is configured.

## Mission Workflow Artifacts

Mission runs are deterministic local workflows that produce useful artifacts without requiring a model call:

- Research missions search indexed sources and report evidence, matched terms, and source coverage.
- Code missions scan project files for target signals, likely implementation files, line counts, and snippets.
- Planning, workflow, loop, and reasoning missions use the planning engine to produce routed execution steps.
- Analytics missions summarize project/source signals for inspection.
- Knowledge missions return matching indexed knowledge items and coverage stats.
- Voice missions return readiness checks for transcript capture and spoken-turn persistence.
- Swarm and collaboration missions convert the objective into agent assignments.

The Next.js dashboard renders these artifacts in Mission Field, Mission Timeline, Research, and Agent Dock views.

## Verification

```bash
cd backend
venv/bin/python -m pytest

cd ../frontend
/usr/bin/env PATH=/opt/homebrew/bin:/opt/homebrew/sbin:/usr/bin:/bin:/usr/sbin:/sbin npm run build
/usr/bin/env PATH=/opt/homebrew/bin:/opt/homebrew/sbin:/usr/bin:/bin:/usr/sbin:/sbin npm run lint
```

Runtime memory files under `memory/*.json` and `backend/memory/*.json` are generated local state and are ignored for future changes.

## Production Readiness

HELIOS is still local-first, but the backend now supports deploy-time guardrails:

- Set `HELIOS_API_KEY` to require `x-helios-api-key` on private API routes.
- Set `HELIOS_RATE_LIMIT_PER_MINUTE` to bound requests per client IP.
- Security headers are emitted by the FastAPI middleware.
- `HELIOS_STORAGE_BACKEND=json` keeps local JSON storage; `sqlite` enables durable single-node runtime storage; `postgres` with `HELIOS_DATABASE_URL` enables multi-worker production runtime storage.
- Runtime state should be mounted as persistent volumes in deployment.

Docker Compose:

```bash
cp .env.example .env
docker compose up --build
```

Compose starts PostgreSQL, the API, frontend, and a separate durable autonomous worker. Runs are claimed with database leases and can be recovered by another worker after an expired lease.

For public deployment, place HELIOS behind HTTPS using `ops/nginx.conf`, set `HELIOS_AUTH_SECRET`, `HELIOS_ADMIN_PASSWORD`, and a restricted `HELIOS_CORS_ORIGINS`. The signed-token flow supports viewer, operator, and admin roles. SQLite-backed deployments share rate-limit buckets across API workers.

To use the Compose TLS gateway, place `fullchain.pem` and `privkey.pem` in `ops/certs/`, then run:

```bash
./ops/generate_dev_certs.sh ops/certs localhost
docker compose --profile production up --build
```

The `production` profile also starts scheduled runtime backups, Prometheus, and Alertmanager. Prometheus is available on port `9090`; Alertmanager is available on port `9093`. Replace `ops/alertmanager.yml` with a receiver based on `ops/alertmanager-webhook.yml.example` to deliver alerts externally.

Back up runtime state with:

```bash
python ops/backup_runtime.py --source backend/memory --destination backups --keep 7
```

Managed database replication, cloud secret rotation, TLS certificates, and external alert delivery remain responsibilities of the target hosting platform.

## Managed Deployment

`ops/k8s/helios.yaml` provides Kubernetes deployments, services, persistent volumes, scalable autonomous workers, managed PostgreSQL configuration, cert-manager TLS ingress, probes, and a database backup CronJob. Replace the example domain, database URL, and image names before applying it.

For cloud secret managers, install External Secrets Operator and adapt `ops/k8s/external-secret.yaml` to your `ClusterSecretStore`.

Build and publish container images by creating a `v*` Git tag or running the `HELIOS Release Images` GitHub Actions workflow. Set repository variables `HELIOS_PUBLIC_API_URL` and `HELIOS_PUBLIC_WS_URL` before building the frontend image.

After deployment, verify HTTPS, readiness, metrics, and optional voice configuration:

```bash
python ops/verify_production.py https://helios.example.com/api
python ops/verify_production.py https://helios.example.com/api --require-voice
```

`NEXT_PUBLIC_HELIOS_API_KEY` can connect the browser dashboard to the API-key gate for private single-user deployments, but it is visible to the browser. Public multi-user deployments should use a trusted reverse proxy or session-based auth instead.

## Environment

Copy `.env.example` into `backend/.env` and set only the providers you plan to use.
