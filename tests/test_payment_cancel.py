from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import create_app


def test_cancel_is_repeatable_and_visible_in_reads_and_filtered_pages() -> None:
    with TestClient(create_app()) as client:
        ids = [
            client.post("/api/v1/payments", json={"amount": 5, "currency": "EUR"})
            .json()["id"]
            for _ in range(3)
        ]
        expected = {"id": ids[1], "amount": 5.0, "currency": "EUR", "status": "cancelled"}
        response = client.post(f"/api/v1/payments/{ids[1]}/cancel")
        assert response.status_code == 200
        assert response.json() == expected
        assert client.post(f"/api/v1/payments/{ids[1]}/cancel").json() == expected
        assert client.get(f"/api/v1/payments/{ids[1]}").json() == expected
        assert client.get("/api/v1/payments?status=cancelled").json() == [expected]
        remaining = client.get("/api/v1/payments?status=pending&offset=1&limit=1").json()
        assert [item["id"] for item in remaining] == [ids[2]]
        assert [item["id"] for item in client.get("/api/v1/payments").json()] == ids


def test_cancel_missing_payment_returns_not_found() -> None:
    with TestClient(create_app()) as client:
        assert client.post(f"/api/v1/payments/{uuid4()}/cancel").status_code == 404
        assert client.get("/api/v1/payments").json() == []
