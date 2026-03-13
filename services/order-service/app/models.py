from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class OrderRequest(BaseModel):
    user_id: str = Field(..., example="USER45")
    product_id: str = Field(..., example="PROD10")
    quantity: int = Field(..., gt=0, example=2)
    price: float = Field(..., gt=0, example=500.0)


class OrderEvent(BaseModel):
    order_id: str = Field(default_factory=lambda: f"ORD-{uuid.uuid4().hex[:8].upper()}")
    user_id: str
    product_id: str
    quantity: int
    price: float
    total_amount: float = 0.0
    status: str = "CREATED"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    def calculate_total(self):
        self.total_amount = self.quantity * self.price
        return self


class OrderResponse(BaseModel):
    order_id: str
    status: str
    message: str
