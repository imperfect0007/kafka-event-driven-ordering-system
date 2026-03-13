# Kafka Event-Driven Order Processing System

A production-grade **microservices architecture** for real-time order processing using **Apache Kafka** for asynchronous, event-driven communication between services.

> Built as a portfolio project demonstrating Full-Stack + DevOps engineering skills.

---

## Architecture

```
                        ┌──────────────────┐
                        │   Client / API   │
                        └────────┬─────────┘
                                 │ POST /orders
                                 ▼
                        ┌──────────────────┐
                        │  Order Service   │ (FastAPI)
                        │    :8001         │
                        └────────┬─────────┘
                                 │ produce
                                 ▼
                  ┌──────────────────────────────┐
                  │        Apache Kafka           │
                  │                                │
                  │  ┌────────┐  ┌──────────────┐ │
                  │  │ orders │  │payment-success│ │
                  │  └────────┘  └──────────────┘ │
                  │  ┌─────────────────┐ ┌──────────────┐ │
                  │  │inventory-updated│ │notifications │ │
                  │  └─────────────────┘ └──────────────┘ │
                  └───┬──────────┬──────────┬─────────────┘
                      │          │          │
            consume   │          │          │  consume
                      ▼          ▼          ▼
              ┌────────────┐ ┌────────────┐ ┌──────────────────┐
              │  Payment   │ │ Inventory  │ │  Notification    │
              │  Service   │ │  Service   │ │    Service       │
              └──────┬─────┘ └──────┬─────┘ └──────────────────┘
                     │              │
                     │         ┌────┴─────┐
                     │         │PostgreSQL │
                     │         └──────────┘
                ┌────┴───┐
                │ Redis  │
                └────────┘
```

### Event Flow (Step by Step)

```
1. User places order ──────────────────────────► Order Service
2. Order Service publishes event ──────────────► Kafka topic: "orders"
3. Payment Service consumes "orders" ──────────► Processes payment
4. Payment Service publishes ──────────────────► Kafka topic: "payment-success"
5. Inventory Service consumes "payment-success" ► Reduces stock (PostgreSQL)
6. Inventory Service publishes ────────────────► Kafka topic: "inventory-updated"
7. Notification Service consumes ──────────────► Sends email / SMS / logs
8. Notification Service publishes ─────────────► Kafka topic: "notifications"
```

---

## Kafka Topics

| Topic                | Producer             | Consumer(s)                         | Purpose                    |
|----------------------|----------------------|-------------------------------------|----------------------------|
| `orders`             | Order Service        | Payment Service                     | New order events           |
| `payment-success`    | Payment Service      | Inventory Service, Notification Svc | Payment results            |
| `inventory-updated`  | Inventory Service    | Notification Service                | Stock updates              |
| `notifications`      | Notification Service | External / Logging                  | Notification audit trail   |

### Sample Event Payload

```json
{
  "order_id": "ORD-A1B2C3D4",
  "user_id": "USER45",
  "product_id": "PROD10",
  "quantity": 2,
  "price": 500,
  "total_amount": 1000,
  "status": "CREATED",
  "timestamp": "2026-03-13T12:00:00"
}
```

---

## Project Structure

```
kafka-order-system/
│
├── services/
│   ├── order-service/             # FastAPI REST API + Kafka Producer
│   │   ├── app/
│   │   │   ├── main.py            # FastAPI app + endpoints
│   │   │   ├── producer.py        # Kafka producer logic
│   │   │   ├── models.py          # Pydantic models
│   │   │   └── config.py          # Environment config
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── payment-service/           # Kafka Consumer + Producer
│   │   ├── main.py                # Entry point
│   │   ├── consumer.py            # Kafka consumer + publisher
│   │   ├── payment.py             # Payment processing logic
│   │   ├── config.py              # Environment config
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── inventory-service/         # Kafka Consumer + PostgreSQL
│   │   ├── main.py                # Entry point + DB init
│   │   ├── consumer.py            # Kafka consumer + publisher
│   │   ├── inventory.py           # Stock management + DB queries
│   │   ├── config.py              # Environment config
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   └── notification-service/      # Kafka Consumer + Email/SMS
│       ├── main.py                # Entry point
│       ├── consumer.py            # Kafka consumer
│       ├── email_service.py       # SMTP / notification logic
│       ├── config.py              # Environment config
│       ├── Dockerfile
│       └── requirements.txt
│
├── infrastructure/
│   ├── docker-compose.yml         # Full stack orchestration
│   └── kafka-config/              # Kafka broker configs
│
├── monitoring/
│   ├── prometheus.yml             # Prometheus scrape config
│   └── grafana/
│       └── provisioning/
│           └── datasources/       # Auto-provision Prometheus source
│
├── scripts/
│   └── create-topics.sh           # Manual topic creation script
│
├── .github/
│   └── workflows/
│       └── ci.yml                 # CI/CD pipeline (build → test → push)
│
├── .gitignore
└── README.md
```

---

## Tech Stack

| Layer            | Technology                            |
|------------------|---------------------------------------|
| **API**          | FastAPI (Python)                      |
| **Messaging**    | Apache Kafka + Zookeeper              |
| **Database**     | PostgreSQL 16                         |
| **Cache**        | Redis 7                               |
| **Containers**   | Docker / Docker Compose               |
| **Monitoring**   | Prometheus + Grafana                  |
| **CI/CD**        | GitHub Actions                        |
| **Kafka UI**     | provectuslabs/kafka-ui                |

---

## Getting Started

### Prerequisites

- [Docker](https://www.docker.com/) & Docker Compose installed
- Python 3.11+ (for local development)

### 1. Start the Full Stack

```bash
cd infrastructure
docker-compose up -d --build
```

This starts **11 containers**:

| Service              | Port   | URL                                    |
|----------------------|--------|----------------------------------------|
| Order Service (API)  | 8001   | http://localhost:8001/docs              |
| Kafka Broker         | 9092   | —                                      |
| Kafka UI             | 8080   | http://localhost:8080                   |
| PostgreSQL           | 5432   | —                                      |
| Redis                | 6379   | —                                      |
| Prometheus           | 9090   | http://localhost:9090                   |
| Grafana              | 3000   | http://localhost:3000 (admin/admin)     |

### 2. Place a Test Order

```bash
curl -X POST http://localhost:8001/orders \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USER45",
    "product_id": "PROD10",
    "quantity": 2,
    "price": 500
  }'
```

**Response:**
```json
{
  "order_id": "ORD-A1B2C3D4",
  "status": "CREATED",
  "message": "Order placed successfully"
}
```

### 3. Watch the Event Flow

Open the **Kafka UI** at http://localhost:8080 and watch events flow through:

```
orders → payment-success → inventory-updated → notifications
```

### 4. Check Service Logs

```bash
docker logs -f order-service
docker logs -f payment-service
docker logs -f inventory-service
docker logs -f notification-service
```

### 5. Stop Everything

```bash
cd infrastructure
docker-compose down -v
```

---

## API Endpoints

### Order Service (`localhost:8001`)

| Method | Endpoint   | Description        |
|--------|------------|--------------------|
| GET    | `/health`  | Health check       |
| POST   | `/orders`  | Create a new order |
| GET    | `/docs`    | Swagger UI         |

---

## CI/CD Pipeline

The GitHub Actions pipeline runs on every push/PR to `main`:

```
┌─────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│  Build   │───►│  Lint/Test   │───►│ Docker Build │───►│ Push to GHCR │
└─────────┘    └──────────────┘    └─────────────┘    └──────────────┘
```

- **Build**: Install Python dependencies
- **Lint**: flake8 code quality checks
- **Docker Build**: Build images for all 4 services
- **Push**: Push to GitHub Container Registry (on `main` only)

---

## Monitoring

| Tool       | URL                        | Credentials  |
|------------|----------------------------|--------------|
| Prometheus | http://localhost:9090       | —            |
| Grafana    | http://localhost:3000       | admin/admin  |

Grafana is auto-provisioned with Prometheus as a data source.

**Metrics tracked:**
- Kafka consumer lag
- Service latency
- Error rates
- Request throughput

---

## Development Roadmap

- [x] **Day 1** — Project Setup & Architecture
- [x] **Day 2** — Kafka Local Setup (Docker)
- [x] **Day 3** — Order Service (FastAPI Producer)
- [x] **Day 4** — Payment Service (Consumer + Producer)
- [x] **Day 5** — Inventory Service (Consumer + PostgreSQL)
- [x] **Day 6** — Notification Service (Consumer + Email)
- [x] **Day 7** — Docker Compose, CI/CD, Monitoring

---

## Resume Description

> **Built a Kafka-based event-driven microservices architecture** for real-time order processing with asynchronous communication between services. Designed and implemented 4 microservices (Order, Payment, Inventory, Notification) with FastAPI, Apache Kafka, PostgreSQL, and Redis. Set up CI/CD with GitHub Actions, containerized with Docker, and added monitoring with Prometheus + Grafana.
>
> **Technologies:** Apache Kafka, FastAPI, Python, Docker, PostgreSQL, Redis, Prometheus, Grafana, GitHub Actions

---

## License

MIT
