import json
import logging
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError
from config import (
    KAFKA_BROKER,
    KAFKA_TOPIC_PAYMENT_SUCCESS,
    KAFKA_TOPIC_INVENTORY_UPDATED,
    KAFKA_GROUP_ID,
    SERVICE_NAME,
)
from inventory import reduce_stock

logger = logging.getLogger(SERVICE_NAME)


def create_consumer() -> KafkaConsumer:
    return KafkaConsumer(
        KAFKA_TOPIC_PAYMENT_SUCCESS,
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
        retries=3,
    )


def publish_inventory_event(producer: KafkaProducer, event: dict):
    try:
        future = producer.send(
            KAFKA_TOPIC_INVENTORY_UPDATED,
            key=event["order_id"],
            value=event,
        )
        record = future.get(timeout=10)
        logger.info(
            f"Published inventory update → topic={record.topic} "
            f"partition={record.partition} offset={record.offset}"
        )
    except KafkaError as e:
        logger.error(f"Failed to publish inventory event: {e}")


def start_consuming():
    consumer = create_consumer()
    producer = create_producer()

    logger.info(f"Consuming from topic: {KAFKA_TOPIC_PAYMENT_SUCCESS}")

    try:
        for message in consumer:
            payment = message.value
            order_id = payment.get("order_id", "UNKNOWN")
            logger.info(
                f"Received payment event: {order_id} "
                f"status={payment.get('payment_status')} "
                f"[partition={message.partition}, offset={message.offset}]"
            )

            if payment.get("payment_status") != "SUCCESS":
                logger.info(f"Skipping order {order_id} — payment not successful")
                continue

            inventory_result = reduce_stock(
                payment["product_id"],
                payment["quantity"],
            )

            event = {
                "order_id": order_id,
                "user_id": payment["user_id"],
                "product_id": payment["product_id"],
                "quantity": payment["quantity"],
                "total_amount": payment.get("total_amount"),
                "transaction_id": payment.get("transaction_id"),
                "inventory_status": inventory_result["status"],
                "inventory_details": inventory_result,
            }
            publish_inventory_event(producer, event)
    except KeyboardInterrupt:
        logger.info("Shutting down consumer...")
    finally:
        consumer.close()
        producer.flush()
        producer.close()
        logger.info("Consumer closed")
