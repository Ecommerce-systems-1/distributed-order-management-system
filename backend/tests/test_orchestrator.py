import pytest
import asyncio
import sqlite3
from app.saga.orchestrator import SagaOrchestrator
from app.saga.state import SagaState

@pytest.fixture
def db():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    SagaState.create_tables(conn)
    return conn

def make_order(order_id="ord_test", fail_at=None):
    return {
        "id": order_id, "customer_id": "cust_1", "customer_email": "test@test.com",
        "product_id": "prod_001", "product_name": "Test Product",
        "quantity": 1, "unit_price": 49.99, "total_amount": 49.99,
        "shipping_address": "123 Main St", "fail_at": fail_at,
    }

@pytest.mark.asyncio
async def test_happy_path_all_steps_completed(db):
    orchestrator = SagaOrchestrator(db)
    order = make_order("ord_happy")
    await orchestrator.run(order)
    state = SagaState(db)
    steps = state.get_steps("ord_happy")
    assert len(steps) == 4
    assert all(s["status"] == "completed" for s in steps)
    order_row = db.execute("SELECT saga_status FROM orders WHERE id='ord_happy'").fetchone()
    assert order_row["saga_status"] == "completed"

@pytest.mark.asyncio
async def test_payment_failure_compensates_inventory(db):
    orchestrator = SagaOrchestrator(db)
    order = make_order("ord_pay_fail", fail_at="payment")
    await orchestrator.run(order)
    state = SagaState(db)
    steps = {s["step_number"]: s for s in state.get_steps("ord_pay_fail")}
    assert steps[1]["status"] == "compensated"   # inventory released
    assert steps[2]["status"] == "failed"         # payment failed
    assert steps[3]["status"] == "pending"        # fulfillment never ran
    order_row = db.execute("SELECT saga_status FROM orders WHERE id='ord_pay_fail'").fetchone()
    assert order_row["saga_status"] == "failed"

@pytest.mark.asyncio
async def test_fulfillment_failure_compensates_payment_and_inventory(db):
    orchestrator = SagaOrchestrator(db)
    order = make_order("ord_ful_fail", fail_at="fulfillment")
    await orchestrator.run(order)
    state = SagaState(db)
    steps = {s["step_number"]: s for s in state.get_steps("ord_ful_fail")}
    assert steps[1]["status"] == "compensated"   # inventory released
    assert steps[2]["status"] == "compensated"   # payment refunded
    assert steps[3]["status"] == "failed"         # fulfillment failed
    assert steps[4]["status"] == "pending"        # notification never ran

@pytest.mark.asyncio
async def test_inventory_failure_no_compensation_needed(db):
    orchestrator = SagaOrchestrator(db)
    order = make_order("ord_inv_fail", fail_at="inventory")
    await orchestrator.run(order)
    state = SagaState(db)
    steps = {s["step_number"]: s for s in state.get_steps("ord_inv_fail")}
    assert steps[1]["status"] == "failed"
    # No compensation steps should have run for other services
    assert steps[2]["status"] == "pending"

@pytest.mark.asyncio
async def test_steps_persisted_after_each_forward(db):
    orchestrator = SagaOrchestrator(db)
    order = make_order("ord_persist")
    await orchestrator.run(order)
    rows = db.execute("SELECT * FROM saga_steps WHERE order_id='ord_persist' ORDER BY step_number").fetchall()
    assert len(rows) == 4
    for row in rows:
        assert row["output_data"] is not None  # forward output persisted
        assert row["completed_at"] is not None