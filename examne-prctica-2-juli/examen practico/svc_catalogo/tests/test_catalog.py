import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from app.main import app


def test_create_and_fetch_product():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/productos",
            json={"sku": "SKU-001", "nombre": "Arroz", "precio": 1.5, "stock": 10},
        )
        assert response.status_code == 201
        body = response.json()
        assert body["sku"] == "SKU-001"
        assert body["stock"] == 10

        product_id = body["id"]
        fetched = client.get(f"/api/v1/productos/{product_id}")
        assert fetched.status_code == 200
        assert fetched.json()["nombre"] == "Arroz"
