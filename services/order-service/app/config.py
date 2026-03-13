import os


KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
KAFKA_TOPIC_ORDERS = os.getenv("KAFKA_TOPIC_ORDERS", "orders")
SERVICE_NAME = "order-service"
SERVICE_HOST = os.getenv("SERVICE_HOST", "0.0.0.0")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8001"))
