import logging
import random
from config import SERVICE_NAME

logger = logging.getLogger(SERVICE_NAME)


def process_payment(order: dict) -> dict:
    """Simulate payment processing with 90% success rate."""
    order_id = order["order_id"]
    total = order.get("total_amount", order["quantity"] * order["price"])

    logger.info(f"Processing payment for order {order_id}, amount={total}")

    success = random.random() < 0.9

    if success:
        logger.info(f"Payment successful for order {order_id}")
        return {
            "order_id": order_id,
            "user_id": order["user_id"],
            "product_id": order["product_id"],
            "quantity": order["quantity"],
            "price": order["price"],
            "total_amount": total,
            "payment_status": "SUCCESS",
            "transaction_id": f"TXN-{order_id.split('-')[-1]}-{random.randint(1000,9999)}",
        }
    else:
        logger.warning(f"Payment failed for order {order_id}")
        return {
            "order_id": order_id,
            "user_id": order["user_id"],
            "payment_status": "FAILED",
            "reason": "Insufficient funds",
        }
