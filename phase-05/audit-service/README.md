# Audit Service

Minimal audit service for the Todo Chatbot application.

## Overview
- Consumes Kafka events and creates audit logs for compliance
- Stores audit logs in PostgreSQL database
- Includes dead letter queue for failed message handling

## Features
- Event consumption from Kafka topics
- Audit log creation with user, entity, and operation tracking
- REST API for querying audit logs
- Health checks for service monitoring

## Tech Stack
- FastAPI
- SQLModel
- PostgreSQL
- Kafka (via AIOKafkaConsumer)

## Setup
```bash
uv sync
uv run -m src.main:app --reload
```

## Endpoints
- `GET /` - Service status
- `GET /health` - Health check
- `GET /audit-logs` - Retrieve audit logs
- `GET /audit-logs/search` - Search audit logs with filters
