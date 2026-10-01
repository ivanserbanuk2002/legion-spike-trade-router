# legion-spike-trade-router

## Overview

Technical spike for the architecture of a trade-routing microservice using
Python 3.12, FastAPI, SQLAlchemy, and Docker. This repository contains only a
service scaffold. It has no trading rules, exchange integrations, credentials,
order execution, or database connections.

| Method | Path | Response |
| --- | --- | --- |
| GET | `/health` | `{"status": "ok"}` |
| POST | `/api/v1/stub` | `{"status": "scaffold"}` |

The stub accepts an empty request body and has no side effects.

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

Run the single pytest test:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

On Linux / macOS, use `.venv/bin/python -m pytest`.

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
  core/            Reserved for application configuration
  models/          Reserved for SQLAlchemy models
  schemas/         Reserved for request and response schemas
alembic/           Reserved for migration configuration and revisions
tests/             One health endpoint test
docker/            Reserved for container support files
Dockerfile         Python 3.12 image, non-root runtime
docker-compose.yml Local API service
```

The application entry point registers a small HTTP router. `/health` reports
process liveness only; it does not check external dependencies. SQLAlchemy and
Alembic are declared dependencies, but there is no engine, session, database
service, migration environment, or domain model yet. The reserved directories
contain placeholders only.

The intended boundary keeps domain decisions separate from HTTP handlers,
persistence, and venue adapters. This scaffold does not implement those layers
or establish that the architecture is valid for real trading.

Dependencies use version ranges rather than a lockfile. Docker configuration
is provided; no image build or deployment has been performed for this spike.

## Open questions

- What instrument identity and quantity units belong in the domain model?
- Which persistence backend and transaction boundaries fit the service?
- What should define request ownership and idempotency at the API boundary?
