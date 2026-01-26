# Kafka Integration Implementation Plan

## Overview
This document outlines the plan for integrating Apache Kafka into the Todo Chatbot application to enable event-driven architecture using separate microservices.

## Goals
- Implement event-driven architecture using Kafka for real-time task notifications
- Deploy separate microservices for task management, event processing, notifications, and audit
- Ensure scalability, resilience, and maintainability through microservices architecture
- Follow cloud-native principles with containerized deployments

## Architecture Approach

### Option 2: Separate Microservices (Selected Approach)
- Separate services for task management, event processing, notifications, and audit
- Each service deployed independently as Docker containers
- Better for scaling and resilience in production
- Clear separation of concerns with independent development/deployment lifecycles
- Services communicate via Kafka topics
- Each service has its own database for data isolation

## Service Structure

### 1. Task Service
- Handles core task management operations (CRUD)
- Publishes task-related events to Kafka
- Container: `taskflow-task-service`
- Ports: 8001

### 2. Notification Service
- Consumes task events and sends notifications
- Handles email, push, and in-app notifications
- Container: `taskflow-notification-service`
- Ports: 8002

### 3. Audit Service
- Consumes all events for compliance logging
- Maintains audit trails
- Container: `taskflow-audit-service`
- Ports: 8003

### 4. Reminder Service
- Handles reminder scheduling and triggering
- Publishes reminder events at appropriate times
- Container: `taskflow-reminder-service`
- Ports: 8004

## Folder Structure

```
phase-05/
├── backend/                    # Existing backend code (minimally modified)
│   ├── src/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── models/
│   │   ├── services/
│   │   ├── kafka/              # New Kafka integration module
│   │   │   ├── producer.py      # Kafka producer for event publishing
│   │   │   ├── config.py        # Kafka configuration
│   │   │   └── events/          # Event schemas
│   │   │       ├── task_created.py
│   │   │       ├── task_updated.py
│   │   │       └── task_deleted.py
│   │   └── tests/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── pyproject.toml
├── notification-service/       # New notification service
│   ├── src/
│   │   ├── main.py
│   │   ├── config/
│   │   ├── services/
│   │   ├── kafka/
│   │   │   ├── consumer.py
│   │   │   ├── config.py
│   │   │   └── handlers/
│   │   │       ├── task_created_handler.py
│   │   │       └── task_updated_handler.py
│   │   └── tests/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── pyproject.toml
├── audit-service/              # New audit logging service
│   ├── src/
│   │   ├── main.py
│   │   ├── config/
│   │   ├── services/
│   │   ├── kafka/
│   │   │   ├── consumer.py
│   │   │   ├── config.py
│   │   │   └── handlers/
│   │   │       ├── base_handler.py
│   │   │       └── audit_handler.py
│   │   └── tests/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── pyproject.toml
├── reminder-service/           # New reminder scheduling service
│   ├── src/
│   │   ├── main.py
│   │   ├── config/
│   │   ├── services/
│   │   ├── kafka/
│   │   │   ├── producer.py
│   │   │   ├── consumer.py
│   │   │   ├── config.py
│   │   │   └── schedulers/
│   │   │       ├── reminder_scheduler.py
│   │   │       └── event_publisher.py
│   │   └── tests/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── pyproject.toml
├── shared/                     # Shared utilities
│   ├── kafka-common/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── serialization.py
│   │   ├── topics.py
│   │   └── schemas/
│   │       ├── base.py
│   │       ├── task_events.py
│   │       └── notification_events.py
│   └── docker/
│       └── docker-compose.microservices.yml
├── frontend/
│   └── (existing frontend code)
├── k8s/
│   ├── task-service.yaml
│   ├── notification-service.yaml
│   ├── audit-service.yaml
│   ├── reminder-service.yaml
│   ├── kafka.yaml
│   └── ingress.yaml
└── docs/
    ├── deployment-guide.md
    └── architecture-decision-record.md
```

## Implementation Phases

### Phase 1: Infrastructure Setup
1. Create separate service directories
2. Set up shared Kafka utilities
3. Create Dockerfiles for each service
4. Set up docker-compose for local development
5. Implement base Kafka configuration

### Phase 2: Task Service Development
1. Migrate existing task functionality to task-service
2. Implement Kafka producer for task events
3. Add event publishing to task operations
4. Create task event schemas
5. Implement error handling and retry logic

### Phase 3: Notification Service Development
1. Create notification service with Kafka consumer
2. Implement handlers for task events
3. Add notification delivery mechanisms (email, push, in-app)
4. Implement WebSocket bridge for real-time frontend updates
5. Add circuit breaker and resilience patterns

### Phase 4: Audit Service Development
1. Create audit service with Kafka consumer
2. Implement audit log persistence
3. Add compliance retention policies
4. Implement search functionality for audit logs
5. Add monitoring and alerting

### Phase 5: Reminder Service Development
1. Create reminder service with scheduler
2. Implement reminder event publishing
3. Add consumer for task update events to adjust reminders
4. Implement time-based event triggering
5. Add monitoring for reminder delivery

### Phase 6: Testing and Validation
1. Unit tests for each service
2. Integration tests between services
3. End-to-end event flow tests
4. Performance and resilience tests
5. Chaos engineering tests

## Event Flows

### Task Creation Flow
1. Frontend sends task creation request to Task Service
2. Task Service saves task to its database
3. Task Service publishes "task.created" event to Kafka
4. Notification Service consumes event, sends notification
5. Audit Service consumes event, logs to audit trail
6. Reminder Service consumes event, schedules reminders if needed

### Task Update Flow
1. Frontend sends task update request to Task Service
2. Task Service updates task in its database
3. Task Service publishes "task.updated" event to Kafka
4. Notification Service consumes event, sends update notifications
5. Audit Service consumes event, logs update to audit trail
6. Reminder Service adjusts scheduled reminders if due date changed

### Reminder Flow
1. Reminder Service checks scheduled reminders
2. Reminder Service publishes "task.reminder" event to Kafka at appropriate time
3. Notification Service consumes event, delivers reminder notification

## Deployment Architecture

### Local Development
- Docker Compose with all services and Kafka
- Shared Kafka cluster for all services
- Individual service containers with separate networks

### Production Deployment
- Kubernetes deployment with separate pods for each service
- Kafka cluster (Confluent Cloud or self-hosted)
- Service mesh for service-to-service communication
- Individual databases for each service
- Monitoring and logging aggregation

## Communication Patterns

### Service-to-Kafka Communication
- Services publish events to Kafka topics
- Services consume events from Kafka topics
- Event-driven asynchronous communication

### Direct Service Communication
- Minimal direct communication between services
- Mostly through Kafka events
- Health checks may use direct HTTP calls

## Data Management

### Data Isolation
- Each service has its own database
- Task Service: Task data
- Notification Service: Notification records
- Audit Service: Audit logs
- Reminder Service: Scheduled reminders

### Data Consistency
- Eventual consistency through event-driven architecture
- Idempotency in event handlers to handle duplicates
- Compensating actions for error recovery

## Monitoring and Observability

### Service-Level Metrics
- Health checks for each service
- Performance metrics
- Error rates and latencies

### Event-Level Metrics
- Event processing rates
- Consumer lag monitoring
- Event delivery success rates

### Distributed Tracing
- Trace events across service boundaries
- Monitor end-to-end event processing time

## Security Considerations

### Service Communication
- Mutual TLS between services
- SASL/SCRAM authentication for Kafka
- Role-based access control

### Data Protection
- Encryption at rest for databases
- Encryption in transit for all communications
- Secure secret management

## Scaling Strategy

### Horizontal Scaling
- Independent scaling of each service based on load
- Kafka partitioning for parallel processing
- Auto-scaling based on consumer lag

### Load Distribution
- Multiple instances of stateless services
- Kafka consumer groups for parallel processing
- Database read replicas where applicable
