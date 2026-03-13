import os


KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
KAFKA_TOPIC_PAYMENT_SUCCESS = os.getenv("KAFKA_TOPIC_PAYMENT_SUCCESS", "payment-success")
KAFKA_TOPIC_INVENTORY_UPDATED = os.getenv("KAFKA_TOPIC_INVENTORY_UPDATED", "inventory-updated")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "inventory-group")
SERVICE_NAME = "inventory-service"

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "inventory_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")

DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)
