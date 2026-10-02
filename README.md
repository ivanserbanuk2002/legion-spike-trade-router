# legion-spike-trade-router

## Overview

📐 [Architecture](docs/ARCHITECTURE.md)

Technical spike for the architecture of a trade-routing microservice using
Python 3.12, FastAPI, SQLAlchemy, and Docker. This repository contains a service
scaffold and an in-memory payments example. It has no trading rules,
exchange integrations, credentials, order execution, or database connections.

| Method | Path | Response |
| --- | --- | --- |
| GET | `/health` | `{"status": "ok"}` |
| POST | `/api/v1/stub` | `{"status": "scaffold"}` |
| POST | `/api/v1/payments` | `{"id": "<uuid>", "status": "pending"}` |
| GET | `/api/v1/payments/{id}` | Payment `id`, `amount`, `currency`, and `status` |
| GET | `/api/v1/payments` | Array of payments in creation order |
| POST | `/api/v1/payments/{id}/cancel` | Full payment with status `cancelled` |

The stub accepts an empty request body and has no side effects.
The payments endpoint accepts `{"amount": 10.5, "currency": "USD"}` and returns
HTTP 201. Amount must be finite and greater than zero; currency must be a
nonempty string after trimming whitespace. Invalid input returns HTTP 422.
GET returns HTTP 404 for an unknown UUID (422 for a malformed UUID).
Records are kept only in application memory and disappear on restart. Each app
instance/worker has its own store; no payment is executed or published as an event.

The collection accepts `status=pending|cancelled`, `limit` (1–100, default 50),
and `offset` (0–1,000,000, default 0). Filtering happens before pagination.
Empty pages return `[]`; invalid query parameters return HTTP 422.

Cancellation changes `pending` to `cancelled` and returns HTTP 200. Repeating it
returns the same cancelled record. Missing UUIDs return HTTP 404. This is only a
local state change; it does not cancel anything at a payment provider or exchange.

Create optionally accepts `Idempotency-Key` (1–128 characters, not whitespace-only).
Keys are case-sensitive and compared exactly. A repeated key with the same amount
after float conversion and the same trimmed currency returns HTTP 200 with the
existing `id` and **current** status, including `cancelled`. A different normalized
payload returns HTTP 409 without changing the original record. Without a key, each
request creates a new payment. Key lookup and insertion share one lock, including
concurrent requests. Keys last until the store is discarded, with no expiry or
eviction; this is process-local behavior, not durable or account-scoped protection.

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

Run the offline tests:

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
  core/            UUID helper and lock-protected in-memory payment store
  models/          Four-field SQLAlchemy Payment model
  schemas/         Typed payment requests and responses
alembic/           Reserved for migration configuration and revisions
tests/             Health and payments endpoint tests
docker/            Reserved for container support files
Dockerfile         Python 3.12 image, non-root runtime
docker-compose.yml Local API service
```

The application entry point registers a small HTTP router. `/health` reports
process liveness only; it does not check external dependencies. The Payment
model maps `id`, `amount`, `currency`, and `status`. There is no engine, session,
database service, or migration environment. SQLAlchemy instances stay in a
lock-protected store; callers receive immutable snapshots. `create_app(store=None)`
creates isolated app state and optionally accepts an existing store for composition.
Alembic remains a reserved placeholder.

The intended boundary keeps domain decisions separate from HTTP handlers,
persistence, and venue adapters. The spike does not implement durable persistence or
venue adapters, or establish suitability for real trading.

Dependencies use version ranges rather than a lockfile. Docker configuration
is provided; no image build or deployment has been performed for this spike.

## Open questions

- What instrument identity and quantity units belong in the domain model?
- Which persistence backend and transaction boundaries fit the service?
- What should define ownership and durable, account-scoped idempotency?

## Design references

- Mikko Ohtamaa's [finite-value and strict-JSON boundary work](https://github.com/tradingstrategy-ai/web3-ethereum-defi/commit/382dbe6623bc79a6ed350139d3750ef75c09eb0b)
  inspired rejecting nonfinite amounts and returning JSON-safe validation errors.
- Nader Dabit's [typed payload/status and injected dispatch work](https://github.com/dabit3/a2a-x402-typescript/commit/43d7294c4fc489d574b579d3ed2f856ebefa5f3f)
  inspired typed responses and explicit store injection. These are design references,
  not copied implementations or integrations with either project.

Payment idempotency is a local addition; the references do not establish its behavior.

## Status

In-memory API example with offline contract tests; not production-ready.

Validation is limited to the example HTTP contract, in-memory behavior, and
lint/test tooling. Durable persistence, payment execution, precise money handling,
and cross-service event delivery remain unvalidated. Records and keys grow in memory
without a retention limit; this example has no authentication or account isolation.

`GET /api/v1/payments?currency=USD` adds an exact, case-sensitive currency
filter before pagination. Whitespace is trimmed; blank filters return 422.

`GET /api/v1/payment-reports/counts` returns current pending/cancelled counts
per currency from one locked snapshot. An empty store returns `{}`.
