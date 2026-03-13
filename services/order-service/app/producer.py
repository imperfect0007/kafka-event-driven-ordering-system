import json
import logging
from kafka import KafkaProducer
from kafka.errors import KafkaError
from app.config import KAFKA_BROKER, KAFKA_TOPIC_ORDERS, SERVICE_NAME

logger = logging.getLogger(SERVICE_NAME)

_producer = None


def get_producer() -> KafkaProducer:
    global _producer
    if _producer is None:
        _producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
            acks="all",
            retries=3,
            max_in_flight_requests_per_connection=1,
        )
        logger.info(f"Kafka producer connected to {KAFKA_BROKER}")
    return _producer


def publish_order_event(order_data: dict) -> bool:
    try:
        producer = get_producer()
        future = producer.send(
            KAFKA_TOPIC_ORDERS,
            key=order_data["order_id"],
            value=order_data,
        )
        record_metadata = future.get(timeout=10)
        logger.info(
            f"Published order {order_data['order_id']} → "
            f"topic={record_metadata.topic} "
            f"partition={record_metadata.partition} "
            f"offset={record_metadata.offset}"
        )
        return True
    except KafkaError as e:
        logger.error(f"Failed to publish order event: {e}")
        return False


def close_producer():
    global _producer
    if _producer:
        _producer.flush()
        _producer.close()
        _producer = None
        logger.info("Kafka producer closed")
