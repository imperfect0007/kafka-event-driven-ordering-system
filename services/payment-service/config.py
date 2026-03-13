import os


KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
KAFKA_TOPIC_ORDERS = os.getenv("KAFKA_TOPIC_ORDERS", "orders")
KAFKA_TOPIC_PAYMENT_SUCCESS = os.getenv("KAFKA_TOPIC_PAYMENT_SUCCESS", "payment-success")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "payment-group")
SERVICE_NAME = "payment-service"
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
