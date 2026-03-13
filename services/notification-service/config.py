import os


KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
KAFKA_TOPIC_INVENTORY_UPDATED = os.getenv("KAFKA_TOPIC_INVENTORY_UPDATED", "inventory-updated")
KAFKA_TOPIC_NOTIFICATIONS = os.getenv("KAFKA_TOPIC_NOTIFICATIONS", "notifications")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "notification-group")
SERVICE_NAME = "notification-service"

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
NOTIFICATION_FROM = os.getenv("NOTIFICATION_FROM", "noreply@orderservice.com")
