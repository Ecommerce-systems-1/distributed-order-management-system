import asyncio, uuid

class NotificationService:
    name = "NotificationService"
    forward_action = "send"
    compensate_action = None  # no compensation

    def __init__(self, delay_ms: int = 50):
        self.delay_ms = delay_ms

    async def execute(self, context: dict) -> dict:
        await asyncio.sleep(self.delay_ms / 1000)
        return {
            "notification_id": f"ntf_{uuid.uuid4().hex[:8]}",
            "channel": "email",
            "sent": True,
        }

    async def compensate(self, forward_output: dict) -> dict:
        return {}  # notification compensation is a no-op