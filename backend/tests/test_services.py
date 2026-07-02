import pytest
import asyncio
from app.services.inventory import InventoryService
from app.services.payment import PaymentService
from app.services.fulfillment import FulfillmentService
from app.services.notification import NotificationService
from app.saga.exceptions import SagaStepError

# --- InventoryService ---
@pytest.mark.asyncio
async def test_inventory_reserve_returns_reservation_id():
    svc = InventoryService()
    result = await svc.execute({"product_id": "prod_001", "quantity": 2, "order_id": "ord_test"})
    assert "reservation_id" in result
    assert result["reservation_id"].startswith("res_")

@pytest.mark.asyncio
async def test_inventory_release_returns_success():
    svc = InventoryService()
    fwd = await svc.execute({"product_id": "prod_001", "quantity": 1, "order_id": "ord_x"})
    result = await svc.compensate(fwd)
    assert result["released"] is True

@pytest.mark.asyncio
async def test_inventory_raises_on_forced_failure():
    svc = InventoryService(force_fail=True)
    with pytest.raises(SagaStepError, match="Inventory"):
        await svc.execute({"product_id": "prod_001", "quantity": 1, "order_id": "ord_fail"})

# --- PaymentService ---
@pytest.mark.asyncio
async def test_payment_charge_returns_transaction_id():
    svc = PaymentService()
    result = await svc.execute({"customer_id": "cust_1", "amount": 99.99, "order_id": "ord_test"})
    assert "transaction_id" in result
    assert result["transaction_id"].startswith("txn_")

@pytest.mark.asyncio
async def test_payment_refund_returns_refund_id():
    svc = PaymentService()
    fwd = await svc.execute({"customer_id": "cust_1", "amount": 49.99, "order_id": "ord_x"})
    result = await svc.compensate(fwd)
    assert "refund_id" in result

@pytest.mark.asyncio
async def test_payment_raises_on_forced_failure():
    svc = PaymentService(force_fail=True)
    with pytest.raises(SagaStepError, match="Payment"):
        await svc.execute({"customer_id": "cust_1", "amount": 9.99, "order_id": "ord_fail"})

# --- FulfillmentService ---
@pytest.mark.asyncio
async def test_fulfillment_route_returns_shipment_id():
    svc = FulfillmentService()
    result = await svc.execute({"order_id": "ord_test", "address": "123 Main St"})
    assert "shipment_id" in result
    assert result["carrier"] in ["FedEx","UPS","USPS","DHL"]

@pytest.mark.asyncio
async def test_fulfillment_cancel_returns_cancelled():
    svc = FulfillmentService()
    fwd = await svc.execute({"order_id": "ord_x", "address": "456 Elm Ave"})
    result = await svc.compensate(fwd)
    assert result["cancelled"] is True

@pytest.mark.asyncio
async def test_fulfillment_raises_on_forced_failure():
    svc = FulfillmentService(force_fail=True)
    with pytest.raises(SagaStepError, match="Fulfillment"):
        await svc.execute({"order_id": "ord_fail", "address": "789 Oak Rd"})

# --- NotificationService ---
@pytest.mark.asyncio
async def test_notification_send_returns_notification_id():
    svc = NotificationService()
    result = await svc.execute({"customer_id": "c1", "order_id": "ord_test", "status": "completed"})
    assert "notification_id" in result

@pytest.mark.asyncio
async def test_notification_has_no_compensate():
    svc = NotificationService()
    # compensate is a no-op — returns empty dict
    result = await svc.compensate({})
    assert result == {}