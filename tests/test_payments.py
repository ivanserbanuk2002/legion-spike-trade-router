from uuid import UUID

from fastapi.testclient import TestClient

from app.main import app


def test_create_payment_returns_pending() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/payments", json={"amount": 10.5, "currency": "USD"}
        )

    assert response.status_code == 201
    payload = response.json()
    assert set(payload) == {"id", "status"}
    assert UUID(payload["id"]).version == 4
    assert payload["status"] == "pending"


def test_create_payment_rejects_invalid_amount() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/payments", json={"amount": "invalid", "currency": "USD"}
        )

    assert response.status_code == 422
    assert any(
        error["loc"] == ["body", "amount"] for error in response.json()["detail"]
    )
