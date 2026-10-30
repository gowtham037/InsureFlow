import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_endpoints():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "HEALTHY"

    res_root = client.get("/")
    assert res_root.status_code == 200
    assert res_root.json()["service"] == "InsureFlow"


def test_dashboard_endpoints():
    res_sum = client.get("/api/dashboard/summary")
    assert res_sum.status_code == 200
    data = res_sum.json()
    assert "total_applicants" in data
    assert "total_quotes" in data
    assert "issued_policies" in data

    res_met = client.get("/api/dashboard/metrics")
    assert res_met.status_code == 200
    met = res_met.json()
    assert "approval_rate" in met
    assert "precision" in met
    assert "recall" in met

    res_prod = client.get("/api/dashboard/product-distribution")
    assert res_prod.status_code == 200
    assert len(res_prod.json()) == 3


def test_applicants_endpoints():
    res = client.get("/api/applicants?page=1&page_size=10")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert len(data["items"]) <= 10

    # Test phone number validation (must be exactly 10 digits)
    invalid_short_payload = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test.shortphone@example.com",
        "phone": "12345678",  # 8 digits -> invalid
        "date_of_birth": "1990-01-01",
        "gender": "FEMALE"
    }
    res_short = client.post("/api/applicants", json=invalid_short_payload)
    assert res_short.status_code == 422
    assert "Phone number must contain exactly 10 digits" in res_short.text

    invalid_long_payload = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test.longphone@example.com",
        "phone": "123456789012",  # 12 digits -> invalid
        "date_of_birth": "1990-01-01",
        "gender": "MALE"
    }
    res_long = client.post("/api/applicants", json=invalid_long_payload)
    assert res_long.status_code == 422
    assert "Phone number must contain exactly 10 digits" in res_long.text

    valid_payload = {
        "first_name": "Test",
        "last_name": "ValidPhone",
        "email": f"test.validphone.{int(datetime.now().timestamp())}@example.com",
        "phone": "9876543210",  # exactly 10 digits -> valid
        "date_of_birth": "1990-01-01",
        "gender": "NON_BINARY"
    }
    res_valid = client.post("/api/applicants", json=valid_payload)
    assert res_valid.status_code == 201
    assert res_valid.json()["phone"] == "9876543210"


def test_products_endpoints():
    res = client.get("/api/products")
    assert res.status_code == 200
    products = res.json()
    assert len(products) == 3
    assert any(p["line_of_business"] == "MOTOR" for p in products)


def test_quotes_endpoints():
    res = client.get("/api/quotes?page=1&page_size=5")
    assert res.status_code == 200
    data = res.json()
    assert len(data["items"]) <= 5


def test_underwriting_endpoints():
    res_dec = client.get("/api/underwriting/decisions?limit=10")
    assert res_dec.status_code == 200

    res_ref = client.get("/api/underwriting/referrals")
    assert res_ref.status_code == 200


def test_anomalies_endpoints():
    res = client.get("/api/anomalies")
    assert res.status_code == 200
    anomalies = res.json()
    assert len(anomalies) >= 5

    res_sum = client.get("/api/anomalies/summary")
    assert res_sum.status_code == 200
    sum_data = res_sum.json()
    assert sum_data["total_anomalies"] >= 5


def test_admin_and_exports_endpoints():
    res_status = client.get("/api/admin/generation-status")
    assert res_status.status_code == 200
    assert res_status.json()["applicants"] > 0

    res_repro = client.get("/api/admin/reproducibility-check")
    assert res_repro.status_code == 200
    assert res_repro.json()["status"] == "REPRODUCIBLE"

    res_export = client.get("/api/exports/applicants")
    assert res_export.status_code == 200
    assert "text/csv" in res_export.headers.get("content-type", "")
