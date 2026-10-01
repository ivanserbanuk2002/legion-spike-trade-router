from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


def test_replay_uses_normalized_payload_and_current_status() -> None:
    with TestClient(create_app()) as client:
        headers = {"Idempotency-Key": "example-1"}
        first = client.post(
            "/api/v1/payments", json={"amount": "10.50", "currency": " USD "},
            headers=headers,
        )
        replay = client.post(
            "/api/v1/payments", json={"amount": 10.5, "currency": "USD"}, headers=headers,
        )
        assert first.status_code == 201
        assert replay.status_code == 200
        assert replay.json() == first.json()
        payment_id = first.json()["id"]
        client.post(f"/api/v1/payments/{payment_id}/cancel")
        cancelled_replay = client.post(
            "/api/v1/payments", json={"amount": 10.5, "currency": "USD"}, headers=headers,
        )
        assert cancelled_replay.status_code == 200
        assert cancelled_replay.json() == {"id": payment_id, "status": "cancelled"}
        assert len(client.get("/api/v1/payments").json()) == 1


@pytest.mark.parametrize(
    "changed", [{"amount": 11, "currency": "USD"}, {"amount": 10.5, "currency": "EUR"}]
)
def test_same_key_with_different_payload_conflicts(changed: dict) -> None:
    with TestClient(create_app()) as client:
        headers = {"Idempotency-Key": "example-1"}
        first = client.post(
            "/api/v1/payments", json={"amount": 10.5, "currency": "USD"}, headers=headers,
        ).json()
        assert client.post(
            "/api/v1/payments", json=changed, headers=headers,
        ).status_code == 409
        records = client.get("/api/v1/payments").json()
        assert records == [
            {"id": first["id"], "status": "pending", "amount": 10.5, "currency": "USD"}
        ]


def test_without_key_each_request_creates_a_payment() -> None:
    with TestClient(create_app()) as client:
        first, second = [
            client.post("/api/v1/payments", json={"amount": 1, "currency": "USD"})
            for _ in range(2)
        ]
        assert first.status_code == second.status_code == 201
        assert first.json()["id"] != second.json()["id"]


def test_concurrent_retries_create_exactly_one_payment() -> None:
    with TestClient(create_app()) as client:
        def create(_index: int):
            return client.post(
                "/api/v1/payments", json={"amount": 2, "currency": "USD"},
                headers={"Idempotency-Key": "concurrent"},
            )

        with ThreadPoolExecutor(max_workers=8) as pool:
            responses = list(pool.map(create, range(16)))
        assert sorted(response.status_code for response in responses) == [200] * 15 + [201]
        assert len({response.json()["id"] for response in responses}) == 1
        assert len(client.get("/api/v1/payments").json()) == 1


@pytest.mark.parametrize("key", ["", "   ", "a" * 129])
def test_empty_or_oversized_key_is_rejected(key: str) -> None:
    with TestClient(create_app()) as client:
        assert client.post(
            "/api/v1/payments", json={"amount": 1, "currency": "USD"},
            headers={"Idempotency-Key": key},
        ).status_code == 422
        assert client.get("/api/v1/payments").json() == []
