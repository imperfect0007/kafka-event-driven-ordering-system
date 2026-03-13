import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from app.models import OrderRequest, OrderEvent, OrderResponse
from app.producer import publish_order_event, close_producer
from app.config import SERVICE_NAME, SERVICE_HOST, SERVICE_PORT

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(SERVICE_NAME)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"{SERVICE_NAME} starting on {SERVICE_HOST}:{SERVICE_PORT}")
    yield
    close_producer()
    logger.info(f"{SERVICE_NAME} shut down")


app = FastAPI(
    title="Order Service",
    description="Accepts orders and publishes events to Kafka",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health_check():
    return {"service": SERVICE_NAME, "status": "healthy"}


@app.post("/orders", response_model=OrderResponse)
def create_order(request: OrderRequest):
    logger.info(f"Received order request: user={request.user_id} product={request.product_id}")

    order_event = OrderEvent(
        user_id=request.user_id,
        product_id=request.product_id,
        quantity=request.quantity,
        price=request.price,
    ).calculate_total()

    success = publish_order_event(order_event.model_dump())

    if not success:
        raise HTTPException(status_code=503, detail="Failed to publish order event to Kafka")

    logger.info(f"Order created: {order_event.order_id} total={order_event.total_amount}")

    return OrderResponse(
        order_id=order_event.order_id,
        status=order_event.status,
        message="Order placed successfully",
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=SERVICE_HOST, port=SERVICE_PORT, reload=True)
