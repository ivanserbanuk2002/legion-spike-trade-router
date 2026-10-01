import pytest
from fastapi.testclient import TestClient

from app.main import create_app


def test_list_payments_pages_in_insertion_order() -> None:
    with TestClient(create_app()) as client:
        assert client.get("/api/v1/payments").json() == []
        ids = [
            client.post("/api/v1/payments", json={"amount": amount, "currency": "USD"})
            .json()["id"]
            for amount in (3, 1, 2)
        ]
        response = client.get("/api/v1/payments?limit=1&offset=1")
        assert response.status_code == 200
        assert response.json() == [
            {"id": ids[1], "amount": 1.0, "currency": "USD", "status": "pending"}
        ]
        assert [item["id"] for item in client.get("/api/v1/payments").json()] == ids
        assert client.get("/api/v1/payments?offset=3").json() == []
        assert client.get("/api/v1/payments?status=cancelled").json() == []
        assert len(client.get("/api/v1/payments?status=pending").json()) == 3


@pytest.mark.parametrize(
    "query", ["limit=0", "limit=101", "offset=-1", "offset=1000001", "status=paid"]
)
def test_list_rejects_invalid_pagination_and_status(query: str) -> None:
    with TestClient(create_app()) as client:
        assert client.get(f"/api/v1/payments?{query}").status_code == 422
