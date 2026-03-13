#!/bin/bash
set -e

BROKER="${KAFKA_BROKER:-localhost:9092}"

echo "=== Creating Kafka Topics ==="
echo "Broker: $BROKER"
echo ""

TOPICS=("orders" "payment-success" "inventory-updated" "notifications")

for TOPIC in "${TOPICS[@]}"; do
    echo "Creating topic: $TOPIC"
    kafka-topics.sh --bootstrap-server "$BROKER" \
        --create --if-not-exists \
        --topic "$TOPIC" \
        --partitions 3 \
        --replication-factor 1
done

echo ""
echo "=== All Topics ==="
kafka-topics.sh --bootstrap-server "$BROKER" --list

echo ""
echo "Done!"
