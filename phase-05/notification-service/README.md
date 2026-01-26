# Notification Service

Minimal notification service for the Todo Chatbot application.

## Overview
- Consumes Kafka events and sends notifications to users via multiple channels
- Stores notifications and user preferences in PostgreSQL database
- Supports in-app, email, push, and SMS notifications
- Includes dead letter queue for failed message handling

## Features
- Event consumption from Kafka topics (task.events, reminder.events)
- Multi-channel notification delivery (in-app, email, push, SMS)
- User preference management for notification channels
- REST API for retrieving and managing notifications
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
- `GET /health/database` - Database connectivity check
- `GET /health/kafka` - Kafka connectivity check
- `GET /notifications` - Retrieve user notifications
- `POST /notifications/{id}/mark-read` - Mark notification as read
- `POST /notifications/process/{id}` - Process a specific notification