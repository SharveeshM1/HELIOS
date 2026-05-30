# HELIOS

HELIOS is an AI operating workspace with a FastAPI backend, Streamlit control app, and Next.js dashboard. It combines local model routing, persistent memory, source indexing, realtime voice hooks, and module-specific agent surfaces.

## Recruiter-Visible Engineering Highlights

- FastAPI API layer with typed request/response contracts for chat and source indexing.
- Health endpoint with runtime metadata, provider status, uptime, request count, memory stats, and source stats.
- Durable JSON persistence with atomic writes and backup recovery for chat memory.
- Source library indexing with deterministic content fingerprints, scoped retrieval, snippets, and match terms.
- Cognitive engine traces that expose plan, agent, synthesis, and memory stages to the frontend.
- Next.js command dashboard for modules, run ledger, health, sources, voice, and agent orchestration.
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
- `POST /chat` sends a module-scoped message through HELIOS.
- `GET /sources` lists indexed knowledge sources.
- `GET /sources/search?q=...` searches indexed sources with snippets and match terms.
- `POST /sources` indexes a project or chat-scoped source.
- `POST /realtime/session` starts a realtime voice bridge when `OPENAI_API_KEY` is configured.

## Environment

Copy `.env.example` into `backend/.env` and set only the providers you plan to use.
