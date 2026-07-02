import uuid, asyncio
from fastapi import APIRouter, Depends, HTTPException, Query
from app.database import get_db
from app.models.schemas import OrderCreate, OrderDetail
from app.saga.orchestrator import SagaOrchestrator
from app.saga.state import SagaState
from app.data.products import PRODUCTS
import json

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("", status_code=202)
async def place_order(body: OrderCreate, fail_at: str | None = Query(None), db=Depends(get_db)):
    product = next((p for p in PRODUCTS if p["id"] == body.product_id), None)
    if not product:
        raise HTTPException(404, f"Product '{body.product_id}' not found")
    order_id = f"ord_{uuid.uuid4().hex[:8]}"
    order = {
        "id": order_id,
        "customer_id": body.customer_id,
        "customer_email": body.customer_email,
        "product_id": body.product_id,
        "product_name": product["name"],
        "quantity": body.quantity,
        "unit_price": product["price"],
        "total_amount": round(product["price"] * body.quantity, 2),
        "shipping_address": body.shipping_address,
        "fail_at": fail_at,
    }
    orchestrator = SagaOrchestrator(db)
    asyncio.create_task(orchestrator.run(order))
    return {"order_id": order_id, "status": "saga_started", "total_amount": order["total_amount"]}

@router.get("/{order_id}", response_model=OrderDetail)
def get_order(order_id: str, db=Depends(get_db)):
    row = db.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Order not found")
    state = SagaState(db)
    steps_raw = state.get_steps(order_id)
    steps = []
    for s in steps_raw:
        steps.append({
            **s,
            "input_data": json.loads(s["input_data"]) if s["input_data"] else None,
            "output_data": json.loads(s["output_data"]) if s["output_data"] else None,
        })
    return {**dict(row), "saga_steps": steps}

@router.get("")
def list_orders(page: int = 1, size: int = 10, db=Depends(get_db)):
    offset = (page - 1) * size
    total = db.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    rows = db.execute("SELECT id, customer_id, customer_email, product_name, total_amount, saga_status, created_at FROM orders ORDER BY created_at DESC LIMIT ? OFFSET ?", (size, offset)).fetchall()
    return {"total": total, "page": page, "size": size, "orders": [dict(r) for r in rows]}