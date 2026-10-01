# legion-spike-trade-router

## Overview

📐 [Architecture](docs/ARCHITECTURE.md)

Technical spike for the architecture of a trade-routing microservice using
Python 3.12, FastAPI, SQLAlchemy, and Docker. This repository contains a service
scaffold and a minimal payments creation example. It has no trading rules,
exchange integrations, credentials, order execution, or database connections.

| Method | Path | Response |
| --- | --- | --- |
| GET | `/health` | `{"status": "ok"}` |
| POST | `/api/v1/stub` | `{"status": "scaffold"}` |
| POST | `/api/v1/payments` | `{"id": "<uuid>", "status": "pending"}` |

The stub accepts an empty request body and has no side effects.
The payments endpoint accepts `{"amount": 10.5, "currency": "USD"}` and returns
HTTP 201; malformed field types return HTTP 422. It creates a transient model
instance only: no payment is persisted, executed, or published as an event.

## Getting started

Use Python 3.12. From the repository root, create a virtual environment.

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Linux / macOS:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m uvicorn app.main:app --reload
```

The local server uses port 8000. Open [the API docs](http://127.0.0.1:8000/docs)
or [the health endpoint](http://127.0.0.1:8000/health). From another terminal:

```bash
curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/api/v1/stub
```

On Windows, use `curl.exe` if `curl` is a PowerShell alias.

Run the tests (one health test and two payments tests):

```powershell
.\.venv\Scripts\python.exe -m pytest
```

On Linux / macOS, use `.venv/bin/python -m pytest`.

With GNU Make and the virtual environment activated, use `make lint`,
`make test`, or `make run`. The interpreter can be selected with `PYTHON`.
Without Make, lint with `python -m ruff check .` in the activated environment.
GitHub Actions runs lint and tests on pushes and pull requests.

For Docker Compose, copy `.env.example` to `.env` with
`Copy-Item .env.example .env` in PowerShell or `cp .env.example .env` in a POSIX
shell, then run:

```bash
docker compose up --build
```

`APP_PORT` in `.env` selects the host port; the container listens on port 8000.
Compose exposes the service only on `127.0.0.1`. The direct Python commands
above do not read `.env`. Stop Compose with `docker compose down`.

## Architecture notes

```text
app/
  main.py          FastAPI application and router registration
  api/             HTTP endpoints
  core/            Shared UUID generation helper
  models/          Four-field SQLAlchemy Payment model
  schemas/         Reserved for request and response schemas
alembic/           Reserved for migration configuration and revisions
tests/             Health and payments endpoint tests
docker/            Reserved for container support files
Dockerfile         Python 3.12 image, non-root runtime
docker-compose.yml Local API service
```

The application entry point registers a small HTTP router. `/health` reports
process liveness only; it does not check external dependencies. The Payment
model maps `id`, `amount`, `currency`, and `status`. There is no engine, session,
database service, or migration environment. Alembic and schema directories
remain reserved placeholders.

The intended boundary keeps domain decisions separate from HTTP handlers,
persistence, and venue adapters. The spike does not implement persistence or
venue adapters, or establish suitability for real trading.

Dependencies use version ranges rather than a lockfile. Docker configuration
is provided; no image build or deployment has been performed for this spike.

## Open questions

- What instrument identity and quantity units belong in the domain model?
- Which persistence backend and transaction boundaries fit the service?
- What should define request ownership and idempotency at the API boundary?

## Status

✅ Spike complete — architecture validated, ready for feature build

Validation is limited to the example HTTP contract, model mapping, and
lint/test tooling. Persistence, payment execution, precise money handling,
and cross-service event delivery remain unvalidated.
