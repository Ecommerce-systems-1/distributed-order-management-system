import asyncio, uuid, random
from app.saga.exceptions import SagaStepError

CARRIERS = ["FedEx", "UPS", "USPS", "DHL"]

class FulfillmentService:
    name = "FulfillmentService"
    forward_action = "route"
    compensate_action = "cancel_shipment"

    def __init__(self, force_fail: bool = False, delay_ms: int = 100):
        self.force_fail = force_fail
        self.delay_ms = delay_ms
        self._rng = random.Random(42)

    async def execute(self, context: dict) -> dict:
        await asyncio.sleep(self.delay_ms / 1000)
        if self.force_fail:
            raise SagaStepError(self.name, self.forward_action, "No carrier available (simulated)")
        return {
            "shipment_id": f"shp_{uuid.uuid4().hex[:8]}",
            "carrier": self._rng.choice(CARRIERS),
            "routed": True,
            "order_id": context["order_id"],
        }

    async def compensate(self, forward_output: dict) -> dict:
        await asyncio.sleep(self.delay_ms / 1000)
        return {"cancelled": True, "shipment_id": forward_output.get("shipment_id")}