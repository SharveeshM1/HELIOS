# HELIOS Frontend

This is the Next.js command dashboard for HELIOS. It talks to the FastAPI backend for health checks, source indexing, module-scoped chat, realtime voice session creation, and run ledger events.

## Getting Started

First, run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Runtime Surfaces

- `app/page.tsx` renders the AI operating workspace, module switcher, run ledger, source upload, voice controls, and chat composer.
- `NEXT_PUBLIC_HELIOS_API_URL` points browser calls at the FastAPI backend.
- `NEXT_PUBLIC_HELIOS_WS_URL` can override the run ledger WebSocket URL when deployed behind a gateway.

## Environment Variables

- `NEXT_PUBLIC_HELIOS_API_URL` (defaults to `http://localhost:8000`)
- `NEXT_PUBLIC_HELIOS_WS_URL` (optional, full WebSocket URL for live run ledger events)

## Quality Checks

```bash
npm run lint
npm run build
```

## Backend Pairing

Start the backend first:

```bash
cd ../backend
venv/bin/uvicorn backend.server:app --reload
```

The dashboard will show degraded/offline runtime state until `/health` is reachable.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
