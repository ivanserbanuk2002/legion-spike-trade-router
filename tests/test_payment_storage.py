from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app, create_app


def test_created_payment_can_be_retrieved() -> None:
    with TestClient(app) as client:
        created = client.post(
            "/api/v1/payments", json={"amount": 10.5, "currency": "USD"}
        ).json()
        response = client.get(f"/api/v1/payments/{created['id']}")

    assert response.status_code == 200
    assert response.json() == {
        "id": created["id"], "amount": 10.5, "currency": "USD", "status": "pending"
    }


def test_missing_payment_returns_not_found() -> None:
    with TestClient(app) as client:
        response = client.get(f"/api/v1/payments/{uuid4()}")
    assert response.status_code == 404


def test_app_instances_do_not_share_payments() -> None:
    with TestClient(create_app()) as first, TestClient(create_app()) as second:
        created = first.post(
            "/api/v1/payments", json={"amount": 1, "currency": "USD"}
        ).json()
        assert second.get(f"/api/v1/payments/{created['id']}").status_code == 404


@pytest.mark.parametrize("amount", ["0", "-1", "NaN", "Infinity", "-Infinity", "1e400"])
def test_nonpositive_or_nonfinite_amount_returns_validation_error(amount: str) -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/payments",
            content='{"amount": ' + amount + ', "currency": "USD"}',
            headers={"Content-Type": "application/json"},
        )
    assert response.status_code == 422
    assert any(error["loc"] == ["body", "amount"] for error in response.json()["detail"])


@pytest.mark.parametrize("currency", ["", "   "])
def test_empty_currency_returns_validation_error(currency: str) -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/payments", json={"amount": 1, "currency": currency}
        )
    assert response.status_code == 422
