import pytest, time
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_health_returns_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "saga_stats" in data

def test_products_returns_20(client):
    r = client.get("/products")
    assert r.status_code == 200
    assert len(r.json()["products"]) == 20

def test_place_order_returns_immediately(client):
    start = time.time()
    r = client.post("/orders", json={
        "customer_id": "cust_1", "customer_email": "a@b.com",
        "product_id": "prod_001", "quantity": 1, "shipping_address": "1 Main St"
    })
    elapsed = time.time() - start
    assert r.status_code == 202
    assert elapsed < 0.5  # saga runs in background
    assert r.json()["status"] == "saga_started"

def test_order_detail_has_saga_steps(client):
    r = client.post("/orders", json={
        "customer_id": "c2", "customer_email": "b@c.com",
        "product_id": "prod_002", "quantity": 1, "shipping_address": "2 Elm St"
    })
    order_id = r.json()["order_id"]
    time.sleep(1.5)  # wait for saga to complete (~350ms total delay)
    r2 = client.get(f"/orders/{order_id}")
    assert r2.status_code == 200
    data = r2.json()
    assert len(data["saga_steps"]) == 4
    assert data["saga_status"] == "completed"

def test_payment_failure_triggers_compensation(client):
    r = client.post("/orders?fail_at=payment", json={
        "customer_id": "c3", "customer_email": "c@d.com",
        "product_id": "prod_003", "quantity": 1, "shipping_address": "3 Oak Ave"
    })
    order_id = r.json()["order_id"]
    time.sleep(1.5)
    r2 = client.get(f"/orders/{order_id}")
    data = r2.json()
    assert data["saga_status"] == "failed"
    step_statuses = {s["step_number"]: s["status"] for s in data["saga_steps"]}
    assert step_statuses[1] == "compensated"
    assert step_statuses[2] == "failed"

def test_orders_list_paginated(client):
    r = client.get("/orders?page=1&size=5")
    assert r.status_code == 200
    data = r.json()
    assert "orders" in data
    assert "total" in data

def test_unknown_product_returns_404(client):
    r = client.post("/orders", json={
        "customer_id": "c4", "customer_email": "d@e.com",
        "product_id": "nonexistent", "quantity": 1, "shipping_address": "4 Pine Rd"
    })
    assert r.status_code == 404