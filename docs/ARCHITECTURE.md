# Architecture RFC

## Context

This spike explores an HTTP boundary for a future trade-routing service.
The payments resource is a small example of accepting a typed command.
The implementation uses Python 3.12, FastAPI, Pydantic, and SQLAlchemy.
It does not execute payments, place orders, or connect to an exchange.
The design question is whether these boundaries are clear enough to extend.
This RFC records a provisional decision, not a production-readiness claim.

## Boundaries

- `app/main.py` creates each app with an injected or fresh in-memory store.
- `app/api/v1/payments.py` owns request validation and HTTP responses.
- `app/schemas/payment.py` validates a finite positive amount and trimmed nonempty currency.
- `app/models/payment.py` owns the four-column relational representation.
- Its columns are `id`, `amount`, `currency`, and `status`.
- `app/core/payments.py` holds transient models under a lock and returns immutable snapshots.
- No engine, session, or database write is configured. App instances do not share state.
- `/health` remains a liveness endpoint with no external dependency checks.
- The companion event-bus spike is separate and is not wired into this API.

Future domain rules must remain independent of HTTP and venue adapters.
The current float field follows the spike contract; money precision is undecided.
Currency identity validation, durable persistence, and request ownership are not implemented.
No component currently guarantees idempotency or durable acknowledgement.

## Data flow

1. A client sends JSON to `POST /api/v1/payments`.
2. FastAPI and Pydantic validate the required fields and their types.
3. Invalid input returns HTTP 422 before the handler creates an identifier.
4. The store creates a UUID and keeps a transient `Payment` with status `pending`.
5. The API returns HTTP 201 with only `id` and `status`.
6. `GET /api/v1/payments/{id}` reads all four fields, or returns 404 for a missing UUID.
7. Restarting the process loses all records; no event is emitted.

`GET /api/v1/payments` returns an array in insertion order. An optional status
filter runs before offset/limit pagination. Defaults are offset 0 and limit 50;
the HTTP boundary accepts offsets through 1,000,000 and limits from 1 to 100.
The store takes each page under its lock, copying only the selected records.
Pages across separate requests are not a transactional snapshot.

Validation errors expose only type, location, and message, so raw nonfinite input
cannot break JSON error serialization. Currency case is preserved, not validated
against an external currency list. Malformed UUID paths return HTTP 422.

The tests cover creation, retrieval, pagination, missing records, input validation, app isolation,
and the original health contract.
CI runs Ruff and pytest on pushes and pull requests using Python 3.12.
These checks cover the spike contract, not failure recovery or load capacity.

## ADR-001: Why FastAPI over Flask

Decision: use FastAPI for this typed HTTP spike.
FastAPI integrates Pydantic request validation and generated OpenAPI descriptions.
That keeps the example request contract beside its handler with little glue code.
Flask is a viable alternative, but equivalent validation requires explicit setup.
No comparative performance benchmark has been run, so speed is not the rationale.
The trade-off is coupling the HTTP layer to FastAPI and Pydantic conventions.
SQLAlchemy remains outside the route framework; its storage lifecycle is deferred.
Revisit the decision if the service needs a different execution or integration model.

Status: draft, review scheduled next sprint
