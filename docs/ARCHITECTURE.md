# Architecture RFC

## Context

This spike explores an HTTP boundary for a future trade-routing service.
The payments resource is a small example of accepting a typed command.
The implementation uses Python 3.12, FastAPI, Pydantic, and SQLAlchemy.
It does not execute payments, place orders, or connect to an exchange.
The design question is whether these boundaries are clear enough to extend.
This RFC records a provisional decision, not a production-readiness claim.

## Boundaries

- `app/main.py` composes the application and registers routers.
- `app/api/v1/payments.py` owns request validation and HTTP responses.
- The request requires `amount: float` and `currency: str`.
- `app/models/payment.py` owns the four-column relational representation.
- Its columns are `id`, `amount`, `currency`, and `status`.
- The model is transient: no engine, session, or database write is configured.
- `app/core/` is the location for small framework-independent helpers.
- `/health` remains a liveness endpoint with no external dependency checks.
- The companion event-bus spike is separate and is not wired into this API.

Future domain rules must remain independent of HTTP and venue adapters.
The current float field follows the spike contract; money precision is undecided.
Currency validation, persistence, and request ownership are not implemented.
No component currently guarantees idempotency or durable acknowledgement.

## Data flow

1. A client sends JSON to `POST /api/v1/payments`.
2. FastAPI and Pydantic validate the required fields and their types.
3. Invalid input returns HTTP 422 before the handler creates an identifier.
4. The handler creates a UUID and a transient `Payment` with status `pending`.
5. The API returns HTTP 201 with only `id` and `status`.
6. No payment is persisted and no event is emitted after the response.

The tests cover a valid response and a malformed amount; health has its own test.
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
