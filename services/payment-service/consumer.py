import json
import logging
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError
from config import (
    KAFKA_BROKER,
    KAFKA_TOPIC_ORDERS,
    KAFKA_TOPIC_PAYMENT_SUCCESS,
    KAFKA_GROUP_ID,
    SERVICE_NAME,
)
from payment import process_payment

logger = logging.getLogger(SERVICE_NAME)


def create_consumer() -> KafkaConsumer:
    return KafkaConsumer(
        KAFKA_TOPIC_ORDERS,
        bootstrap_servers=KAFKA_BROKER,
        group_id=KAFKA_GROUP_ID,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        max_poll_interval_ms=300000,
    )


def create_producer() -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8") if k else None,
        acks="all",
        retries=3,
    )


def publish_payment_result(producer: KafkaProducer, result: dict):
    try:
        future = producer.send(
            KAFKA_TOPIC_PAYMENT_SUCCESS,
            key=result["order_id"],
            value=result,
        )
        record = future.get(timeout=10)
        logger.info(
            f"Published payment result → topic={record.topic} "
            f"partition={record.partition} offset={record.offset}"
        )
    except KafkaError as e:
        logger.error(f"Failed to publish payment result: {e}")


def start_consuming():
    consumer = create_consumer()
    producer = create_producer()

    logger.info(f"Consuming from topic: {KAFKA_TOPIC_ORDERS}")

    try:
        for message in consumer:
            order = message.value
            logger.info(
                f"Received order: {order['order_id']} "
                f"[partition={message.partition}, offset={message.offset}]"
            )

            result = process_payment(order)
            publish_payment_result(producer, result)
    except KeyboardInterrupt:
        logger.info("Shutting down consumer...")
    finally:
        consumer.close()
        producer.flush()
        producer.close()
        logger.info("Consumer closed")
