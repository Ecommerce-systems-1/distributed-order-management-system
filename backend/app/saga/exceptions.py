class SagaStepError(Exception):
    """Raised by a service when a saga step fails (triggering compensation)."""
    def __init__(self, service: str, action: str, reason: str):
        self.service = service
        self.action = action
        self.reason = reason
        super().__init__(f"{service}.{action} failed: {reason}")

class SagaCompensationError(Exception):
    """Raised when a compensation step itself fails (critical — log and alert)."""