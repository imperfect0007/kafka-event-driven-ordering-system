# Kafka Event-Driven Ordering System

A microservices-based ordering system built with **Apache Kafka** for asynchronous, event-driven communication between services.

---

## Architecture Overview

```
┌──────────────┐       ┌─────────────────────────────────────────────────┐
│   Client /   │       │              Apache Kafka Cluster               │
│   API Call   │       │                                                 │
└──────┬───────┘       │  ┌────────────┐  ┌───────────────────────┐     │
       │               │  │   orders   │  │   payment-success     │     │
       ▼               │  └────────────┘  └───────────────────────┘     │
┌──────────────┐       │  ┌────────────────────┐  ┌───────────────┐     │
│    Order     │──────▶│  │ inventory-updated   │  │ notifications │     │
│   Service    │       │  └────────────────────┘  └───────────────┘     │
└──────────────┘       └──────────┬──────────────────────┬──────────────┘
                                  │                      │
              ┌───────────────────┼──────────────────────┼───────────┐
              │                   │                      │           │
              ▼                   ▼                      ▼           ▼
       ┌─────────────┐   ┌──────────────┐   ┌──────────────┐ ┌───────────────┐
       │   Payment   │   │  Inventory   │   │ Notification │ │   Kafka UI    │
       │   Service   │   │   Service    │   │   Service    │ │  (Monitoring) │
       └─────────────┘   └──────────────┘   └──────────────┘ └───────────────┘
```

### Event Flow

1. **Order Service** receives an order request and publishes an event to the `orders` topic.
2. **Payment Service** consumes from `orders`, processes payment, and publishes to `payment-success`.
3. **Inventory Service** consumes from `payment-success`, updates stock, and publishes to `inventory-updated`.
4. **Notification Service** consumes from `inventory-updated` and `payment-success` to send notifications.

---

## Kafka Topics

| Topic                | Producer            | Consumer(s)                        |
|----------------------|---------------------|------------------------------------|
| `orders`             | Order Service       | Payment Service                    |
| `payment-success`    | Payment Service     | Inventory Service, Notification    |
| `inventory-updated`  | Inventory Service   | Notification Service               |
| `notifications`      | Notification Service| (external / logging)               |

---

## Project Structure

```
kafka-order-system
│
├── services
│   ├── order-service          # Accepts orders, publishes to Kafka
│   ├── payment-service        # Processes payments
│   ├── inventory-service      # Manages stock/inventory
│   └── notification-service   # Sends email/SMS/push notifications
│
├── infrastructure
│   └── docker-compose.yml     # Kafka, Zookeeper, Kafka UI
│
└── README.md
```

---

## Tech Stack

| Layer           | Technology                          |
|-----------------|-------------------------------------|
| Messaging       | Apache Kafka                        |
| Orchestration   | Docker / Docker Compose             |
| Services        | Node.js (or language of choice)     |
| Monitoring      | Kafka UI                            |

---

## Getting Started

### Prerequisites

- [Docker](https://www.docker.com/) & Docker Compose installed
- Node.js 18+ (for service development)

### 1. Start Kafka Infrastructure

```bash
cd infrastructure
docker-compose up -d
```

This starts:
- **Zookeeper** on port `2181`
- **Kafka Broker** on port `9092`
- **Kafka UI** on port `8080` → [http://localhost:8080](http://localhost:8080)

### 2. Verify Kafka Topics

Topics are auto-created via the docker-compose configuration:
- `orders`
- `payment-success`
- `inventory-updated`
- `notifications`

You can also view and manage topics from the Kafka UI at [http://localhost:8080](http://localhost:8080).

### 3. Stop Infrastructure

```bash
cd infrastructure
docker-compose down
```

---

## Development Roadmap

- [x] **Day 1** — Project Setup & Architecture
- [x] **Day 2** — Kafka Local Setup (Docker)
- [ ] **Day 3** — Order Service (Producer)
- [ ] **Day 4** — Payment Service (Consumer + Producer)
- [ ] **Day 5** — Inventory Service
- [ ] **Day 6** — Notification Service
- [ ] **Day 7** — End-to-End Testing & Polish

---

## License

MIT
