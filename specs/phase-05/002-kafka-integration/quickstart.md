# Quickstart Guide: Kafka Integration for Todo Chatbot

## Prerequisites

- Node.js 18+ (for backend services)
- Python 3.9+ (for Kafka consumers)
- Docker and Docker Compose (for local Kafka cluster)
- Dapr runtime installed and running

## Local Development Setup

### 1. Start Local Kafka Cluster

```bash
# Navigate to the project root
cd taskflow

# Start Kafka using Docker Compose
docker-compose -f .specify/docker/kafka-local.yml up -d

# Or if using a different setup:
docker run --name kafka-local -p 9092:9092 -d confluentinc/cp-kafka:latest
```

### 2. Install Dependencies

```bash
# Backend dependencies
npm install kafkajs @dapr/js

# Python consumer dependencies
pip install confluent-kafka fastapi uvicorn
```

### 3. Environment Configuration

Create a `.env` file with the following:

```env
# Kafka Configuration
KAFKA_BROKERS=localhost:9092
KAFKA_CLIENT_ID=taskflow
KAFKA_GROUP_ID=taskflow-group

# SASL/SCRAM Authentication (for production)
KAFKA_SASL_MECHANISM=SCRAM-SHA-256
KAFKA_USERNAME=kafka_user
KAFKA_PASSWORD=kafka_password

# Dapr Configuration
DAPR_HTTP_ENDPOINT=http://localhost:3500
DAPR_GRPC_ENDPOINT=grpc://localhost:50001
```

### 4. Initialize Kafka Topics

```bash
# Create required topics
docker exec -it kafka-local \
  kafka-topics --create --topic todo.task.events --bootstrap-server localhost:9092 --partitions 6 --replication-factor 1

docker exec -it kafka-local \
  kafka-topics --create --topic todo.audit.log --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

docker exec -it kafka-local \
  kafka-topics --create --topic todo.notifications --bootstrap-server localhost:9092 --partitions 4 --replication-factor 1

docker exec -it kafka-local \
  kafka-topics --create --topic todo.reminders --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

docker exec -it kafka-local \
  kafka-topics --create --topic todo.dead.letter --bootstrap-server localhost:9092 --partitions 2 --replication-factor 1
```

## Running the Services

### 1. Start Kafka Producer Service

```bash
# From backend directory
npm run start:kafka-producer
```

### 2. Start Kafka Consumer Services

```bash
# Terminal 1: Task Consumer
npm run start:consumer-task

# Terminal 2: Notification Consumer
npm run start:consumer-notification

# Terminal 3: Audit Consumer
npm run start:consumer-audit
```

### 3. Or Run All Services with Dapr

```bash
# Using Dapr to run with sidecars
dapr run --app-id kafka-producer -- npm run start:kafka-producer
dapr run --app-id task-consumer -- npm run start:consumer-task
dapr run --app-id notification-consumer -- npm run start:consumer-notification
dapr run --app-id audit-consumer -- npm run start:consumer-audit
```

## Basic Usage Examples

### Publishing an Event

```javascript
import { KafkaProducer } from './src/kafka/producer';

const producer = new KafkaProducer();

await producer.publish('todo.task.events', {
  eventId: 'uuid-v4-string',
  timestamp: new Date().toISOString(),
  eventType: 'task.created',
  source: 'task-service',
  userId: 'user-123',
  payload: {
    taskId: 'task-456',
    title: 'Sample Task',
    status: 'pending',
    createdAt: new Date().toISOString()
  }
});
```

### Consuming Events

```javascript
import { TaskConsumer } from './src/kafka/consumers/task-consumer';

const consumer = new TaskConsumer();
await consumer.start();

// Consumer will automatically process messages from todo.task.events topic
```

## Testing

### Unit Tests

```bash
# Run Kafka-related unit tests
npm run test:kafka
npm run test:kafka-unit
```

### Integration Tests

```bash
# Run integration tests with local Kafka cluster
npm run test:kafka-integration
```

## Production Deployment

### 1. Deploy to Kubernetes with Dapr

```bash
# Apply Kafka topics configuration
kubectl apply -f ./deploy/kafka/topics.yaml

# Deploy consumer services with Dapr sidecars
kubectl apply -f ./deploy/kafka/consumers/
kubectl apply -f ./deploy/kafka/producers/
```

### 2. Connect to Redpanda Cloud

Update configuration to use Redpanda Cloud:

```env
KAFKA_BROKERS=your-cluster.redpanda.cloud:9092
KAFKA_SASL_MECHANISM=SCRAM-SHA-256
KAFKA_USERNAME=redpanda_username
KAFKA_PASSWORD=redpanda_password
```

## Monitoring and Troubleshooting

### Check Kafka Topics

```bash
# List all topics
docker exec -it kafka-local kafka-topics --list --bootstrap-server localhost:9092

# Check topic details
docker exec -it kafka-local kafka-topics --describe --topic todo.task.events --bootstrap-server localhost:9092
```

### Monitor Consumer Groups

```bash
# Check consumer group status
docker exec -it kafka-local kafka-consumer-groups --bootstrap-server localhost:9092 --describe --group taskflow-group
```

### Common Issues

1. **Connection Refused**: Ensure Kafka broker is running and accessible
2. **Authentication Failed**: Verify SASL/SCRAM credentials are correct
3. **Consumer Lag**: Check consumer processing speed vs message rate
4. **Serialization Errors**: Ensure JSON format matches expected schema
