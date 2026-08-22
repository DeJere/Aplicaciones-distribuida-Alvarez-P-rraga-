import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from app.main import app


def test_create_order_with_catalog_available(monkeypatch):
    class DummyResponse:
        status_code = 200
        def json(self):
            return {"id": 1, "sku": "SKU-001", "nombre": "Arroz", "precio": 1.5, "stock": 10}

    async def fake_get_product(self, product_id):
        return DummyResponse()

    monkeypatch.setattr("app.main.OrderService._get_catalog_product", fake_get_product)

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/pedidos",
            json={"product_id": 1, "quantity": 2},
        )
        assert response.status_code == 201
        body = response.json()
        assert body["status"] == "CREATED"
        assert body["items"][0]["quantity"] == 2
