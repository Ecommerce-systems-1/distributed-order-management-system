import asyncio, uuid, random
from app.saga.exceptions import SagaStepError

class InventoryService:
    name = "InventoryService"
    forward_action = "reserve"
    compensate_action = "release"

    def __init__(self, force_fail: bool = False, delay_ms: int = 80):
        self.force_fail = force_fail
        self.delay_ms = delay_ms

    async def execute(self, context: dict) -> dict:
        await asyncio.sleep(self.delay_ms / 1000)
        if self.force_fail:
            raise SagaStepError(self.name, self.forward_action, "Simulated stockout")
        return {
            "reservation_id": f"res_{uuid.uuid4().hex[:8]}",
            "product_id": context["product_id"],
            "quantity": context["quantity"],
            "reserved": True,
        }

    async def compensate(self, forward_output: dict) -> dict:
        await asyncio.sleep(self.delay_ms / 1000)
        return {"released": True, "reservation_id": forward_output.get("reservation_id")}