import asyncio, uuid
from app.saga.exceptions import SagaStepError

class PaymentService:
    name = "PaymentService"
    forward_action = "charge"
    compensate_action = "refund"

    def __init__(self, force_fail: bool = False, delay_ms: int = 120):
        self.force_fail = force_fail
        self.delay_ms = delay_ms

    async def execute(self, context: dict) -> dict:
        await asyncio.sleep(self.delay_ms / 1000)
        if self.force_fail:
            raise SagaStepError(self.name, self.forward_action, "Card declined (simulated)")
        return {
            "transaction_id": f"txn_{uuid.uuid4().hex[:10]}",
            "amount": context["amount"],
            "charged": True,
        }

    async def compensate(self, forward_output: dict) -> dict:
        await asyncio.sleep(self.delay_ms / 1000)
        return {
            "refund_id": f"ref_{uuid.uuid4().hex[:8]}",
            "transaction_id": forward_output.get("transaction_id"),
            "refunded": True,
        }