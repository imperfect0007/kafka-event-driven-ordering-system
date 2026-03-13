import json
import logging
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError
from config import (
    KAFKA_BROKER,
    KAFKA_TOPIC_INVENTORY_UPDATED,
    KAFKA_TOPIC_NOTIFICATIONS,
    KAFKA_GROUP_ID,
    SERVICE_NAME,
)
from email_service import send_notification

logger = logging.getLogger(SERVICE_NAME)


def create_consumer() -> KafkaConsumer:
    return KafkaConsumer(
        KAFKA_TOPIC_INVENTORY_UPDATED,
        bootstrap_servers=KAFKA_BROKER,
        group_id=KAFKA_GROUP_ID,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
    )


def create_producer() -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8") if k else None,
        acks="all",
    )


def start_consuming():
    consumer = create_consumer()
    producer = create_producer()

    logger.info(f"Consuming from topic: {KAFKA_TOPIC_INVENTORY_UPDATED}")

    try:
        for message in consumer:
            event = message.value
            order_id = event.get("order_id", "UNKNOWN")
            logger.info(
                f"Received inventory event: {order_id} "
                f"[partition={message.partition}, offset={message.offset}]"
            )

            result = send_notification(event)

            notification_event = {
                "order_id": order_id,
                "user_id": event.get("user_id"),
                **result,
            }

            try:
                future = producer.send(
                    KAFKA_TOPIC_NOTIFICATIONS,
                    key=order_id,
                    value=notification_event,
                )
                record = future.get(timeout=10)
                logger.info(
                    f"Logged notification → topic={record.topic} "
                    f"partition={record.partition} offset={record.offset}"
                )
            except KafkaError as e:
                logger.error(f"Failed to log notification event: {e}")

    except KeyboardInterrupt:
        logger.info("Shutting down consumer...")
    finally:
        consumer.close()
        producer.flush()
        producer.close()
        logger.info("Consumer closed")
