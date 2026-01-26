# Reminder Service

Minimal reminder service for the Todo Chatbot application.

## Overview
- Manages task reminders and sends reminder events to Kafka
- Schedules reminders using APScheduler for timed execution
- Stores reminder data in PostgreSQL database
- Consumes task events to adjust or cancel reminders when tasks change

## Features
- Schedule reminders for specific times
- Bulk scheduling of multiple reminders
- Cancel scheduled reminders
- Get list of scheduled reminders
- Automatic adjustment of reminders when task due dates change
- Automatic cancellation of reminders when tasks are deleted
- REST API for managing reminders
- Health checks for service monitoring

## Tech Stack
- FastAPI
- SQLModel
- PostgreSQL
- Kafka (via AIOKafkaConsumer)
- APScheduler

## Setup
```bash
uv sync
uv run -m src.main:app --reload
```

## Endpoints
- `GET /` - Service status
- `GET /health` - Health check
- `GET /health/database` - Database connectivity check
- `POST /reminders/schedule` - Schedule a reminder
- `POST /reminders/bulk-schedule` - Schedule multiple reminders
- `DELETE /reminders/cancel/{id}` - Cancel a scheduled reminder
- `GET /reminders/scheduled` - Get all scheduled reminders
- `GET /reminders/task/{id}` - Get reminders for a specific task