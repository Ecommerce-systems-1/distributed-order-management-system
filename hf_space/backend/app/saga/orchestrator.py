import sqlite3, json
from datetime import datetime, timezone
from app.saga.state import SagaState
from app.saga.exceptions import SagaStepError
from app.services.inventory import InventoryService
from app.services.payment import PaymentService
from app.services.fulfillment import FulfillmentService
from app.services.notification import NotificationService

class SagaOrchestrator:
    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.state = SagaState(db)

    def _build_services(self, fail_at: str | None):
        return [
            InventoryService(force_fail=(fail_at == "inventory")),
            PaymentService(force_fail=(fail_at == "payment")),
            FulfillmentService(force_fail=(fail_at == "fulfillment")),
            NotificationService(),
        ]

    async def run(self, order: dict) -> None:
        self.state.create_order(order)
        fail_at = order.get("fail_at")
        services = self._build_services(fail_at)
        now = lambda: datetime.now(timezone.utc).isoformat()

        completed_steps: list[tuple[int, object, dict]] = []  # (step_num, svc, output)
        context_builders = [
            lambda o: {"product_id": o["product_id"], "quantity": o["quantity"], "order_id": o["id"]},
            lambda o: {"customer_id": o["customer_id"], "amount": o["total_amount"], "order_id": o["id"]},
            lambda o: {"order_id": o["id"], "address": o["shipping_address"]},
            lambda o: {"customer_id": o["customer_id"], "order_id": o["id"], "status": "completed"},
        ]

        for i, (svc, ctx_fn) in enumerate(zip(services, context_builders)):
            step_num = i + 1
            ctx = ctx_fn(order)
            self.state.update_step(order["id"], step_num, status="running", started_at=now(),
                                   input_data=json.dumps(ctx))
            try:
                output = await svc.execute(ctx)
                self.state.update_step(order["id"], step_num, status="completed",
                                       output_data=json.dumps(output), completed_at=now())
                completed_steps.append((step_num, svc, output))
            except SagaStepError as e:
                self.state.update_step(order["id"], step_num, status="failed",
                                       error_message=str(e), completed_at=now())
                await self._compensate(order["id"], completed_steps)
                self.state.update_order_status(order["id"], "failed")
                return

        self.state.update_order_status(order["id"], "completed")

    async def _compensate(self, order_id: str, completed_steps: list) -> None:
        now = lambda: datetime.now(timezone.utc).isoformat()
        for step_num, svc, forward_output in reversed(completed_steps):
            if svc.compensate_action is None:
                continue
            try:
                await svc.compensate(forward_output)
                self.state.update_step(order_id, step_num, status="compensated",
                                       compensated_at=now())
            except Exception as exc:
                # Log compensation failure but continue compensating other steps
                self.state.update_step(order_id, step_num, error_message=f"Compensation failed: {exc}")