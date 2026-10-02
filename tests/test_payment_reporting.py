from fastapi.testclient import TestClient

from app.main import create_app


def test_currency_filter_precedes_pagination_and_combines_with_status():
    with TestClient(create_app()) as client:
        for currency in ("EUR", "USD", "EUR", "USD"):
            client.post("/api/v1/payments", json={"amount": 2, "currency": currency})
        rows = client.get("/api/v1/payments?currency=USD&limit=1&offset=1").json()
        assert len(rows) == 1 and rows[0]["currency"] == "USD"
        assert client.get("/api/v1/payments?currency=GBP").json() == []
        assert client.get("/api/v1/payments?currency=USD&status=cancelled").json() == []
        assert client.get("/api/v1/payments?currency=%20%20").status_code == 422


def test_counts_group_by_currency_and_current_status():
    with TestClient(create_app()) as client:
        assert client.get("/api/v1/payment-reports/counts").json() == {}
        ids = [client.post("/api/v1/payments", json={"amount": 2, "currency": c})
               .json()["id"] for c in ("USD", "USD", "EUR")]
        client.post(f"/api/v1/payments/{ids[0]}/cancel")
        assert client.get("/api/v1/payment-reports/counts").json() == {
            "USD": {"pending": 1, "cancelled": 1},
            "EUR": {"pending": 1, "cancelled": 0},
        }
        assert len(client.get("/api/v1/payments").json()) == 3
