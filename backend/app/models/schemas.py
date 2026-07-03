from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    customer_id: str = Field(..., min_length=1)
    customer_email: str = Field(..., min_length=3)
    product_id: str = Field(..., min_length=1)
    quantity: int = Field(1, ge=1)
    shipping_address: str = Field(..., min_length=1)


class SagaStepDetail(BaseModel):
    id: str
    order_id: str
    step_number: int
    service_name: str
    action: str
    status: str
    input_data: dict | None = None
    output_data: dict | None = None
    error_message: str | None = None
    started_at: str | None = None
    completed_at: str | None = None
    compensated_at: str | None = None


class OrderDetail(BaseModel):
    id: str
    customer_id: str
    customer_email: str
    product_id: str
    product_name: str
    quantity: int
    unit_price: float
    total_amount: float
    shipping_address: str
    saga_status: str
    fail_at: str | None = None
    created_at: str
    updated_at: str
    saga_steps: list[SagaStepDetail]
