# Kafka Integration Deployment Guide

This document provides instructions for deploying the Kafka-based event-driven architecture for the Todo Chatbot application.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Architecture Overview](#architecture-overview)
3. [Deployment Steps](#deployment-steps)
4. [Configuration](#configuration)
5. [Monitoring and Operations](#monitoring-and-operations)
6. [Troubleshooting](#troubleshooting)
7. [Scaling Guidelines](#scaling-guidelines)

## Prerequisites

### Infrastructure Requirements
- Kubernetes cluster (v1.20+) with sufficient resources:
  - Minimum 4 nodes with 8GB RAM each
  - Persistent storage for Kafka brokers
  - Network access between all components
- Helm 3.x or higher
- kubectl configured for the target cluster
- Docker registry access for image deployment

### External Services
- Redpanda Cloud account (or Kafka cluster) with appropriate credentials
- Monitoring stack (Prometheus/Grafana recommended)
- Logging infrastructure (ELK stack or similar)

## Architecture Overview

The deployed system consists of:

1. **Kafka Producers**: Task service components that publish events to Kafka topics
2. **Kafka Consumers**: Specialized services that consume events and perform actions
   - Task Consumer: Handles task-related events
   - Notification Consumer: Handles notification events
   - Audit Consumer: Handles audit logging events
3. **Health Checks**: Built-in endpoints for monitoring service health
4. **Metrics Collection**: Prometheus-compatible metrics for monitoring

## Deployment Steps

### 1. Prepare Environment

```bash
# Set up namespace
kubectl create namespace todo-app --dry-run=client -o yaml | kubectl apply -f -

# Create secrets for Kafka credentials
kubectl create secret generic kafka-credentials \
  --namespace=todo-app \
  --from-literal=REDPANDA_SASL_USERNAME=<your-username> \
  --from-literal=REDPANDA_SASL_PASSWORD=<your-password> \
  --dry-run=client -o yaml | kubectl apply -f -
```

### 2. Deploy Kafka Infrastructure

Deploy your Kafka cluster (Redpanda Cloud or self-hosted):

```bash
# For self-hosted Kafka using Strimzi operator
kubectl apply -f https://strimzi.io/install/latest?namespace=kafka
kubectl create -f - <<EOF
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: kafka-cluster
  namespace: todo-app
spec:
  kafka:
    version: 3.6.0
    replicas: 3
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
      - name: tls
        port: 9093
        type: internal
        tls: true
    config:
      offsets.topic.replication.factor: 3
      transaction.state.log.replication.factor: 3
      transaction.state.log.min.isr: 2
      default.replication.factor: 3
      min.insync.replicas: 2
      inter.broker.protocol.version: "3.6"
    storage:
      type: jbod
      volumes:
      - id: 0
        type: persistent-claim
        size: 10Gi
        deleteClaim: false
  zookeeper:
    replicas: 3
    storage:
      type: persistent-claim
      size: 5Gi
      deleteClaim: false
  entityOperator:
    topicOperator: {}
    userOperator: {}
EOF
```

### 3. Deploy Application Services

```bash
# Deploy producers
kubectl apply -f k8s/kafka-producers-deployment.yaml

# Deploy consumers
kubectl apply -f k8s/kafka-consumers-deployment.yaml
```

### 4. Verify Deployment

```bash
# Check if pods are running
kubectl get pods -n todo-app

# Check services
kubectl get svc -n todo-app

# Check logs for producers
kubectl logs -l app=kafka-producers -n todo-app

# Check logs for consumers
kubectl logs -l app=kafka-consumers -n todo-app
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| REDPANDA_BOOTSTRAP_SERVERS | Kafka cluster addresses | localhost:9092 | Yes |
| REDPANDA_SECURITY_PROTOCOL | Security protocol | SASL_SSL | No |
| REDPANDA_SASL_MECHANISM | SASL mechanism | SCRAM-SHA-256 | No |
| REDPANDA_SASL_USERNAME | SASL username | - | Yes |
| REDPANDA_SASL_PASSWORD | SASL password | - | Yes |
| REDPANDA_CLIENT_ID | Client identifier | todo-chatbot | No |
| REDPANDA_GROUP_ID | Consumer group ID | todo-chatbot-group | No |
| APP_ENV | Application environment | production | No |
| LOG_LEVEL | Logging level | INFO | No |

### Configuration Files

Configuration files are mounted as ConfigMaps in the deployments. Update them as needed:

```bash
# Update ConfigMap for consumers
kubectl patch configmap kafka-consumers-config -n todo-app --patch='{"data":{"KAFKA_CONFIG.json":"{\"bootstrap.servers\":\"new-kafka-address:9092\",\"security.protocol\":\"SASL_SSL\",\"sasl.mechanisms\":\"SCRAM-SHA-256\"}"}}'
```

## Monitoring and Operations

### Health Checks

Each service exposes health check endpoints:
- `/health` - General health status
- `/metrics` - Prometheus-compatible metrics

### Metrics

Key metrics to monitor:

| Metric | Purpose | Alert Condition |
|--------|---------|-----------------|
| kafka_consumer_lag_messages | Consumer lag per partition | > 1000 messages |
| kafka_produce_success_total | Successful message production | Sudden drop |
| kafka_produce_error_total | Failed message production | Sudden spike |
| kafka_consumer_group_lag_total | Total group lag | > 5000 messages |
| kafka_messages_received_total | Messages received | Sudden drop |

### Operational Runbooks

#### Scaling Consumers

To scale consumer deployments based on load:

```bash
# Scale consumers manually
kubectl scale deployment kafka-consumers -n todo-app --replicas=5

# Or update the HPA configuration
kubectl patch hpa kafka-consumers-hpa -n todo-app --patch='{"spec":{"minReplicas":3,"maxReplicas":10}}'
```

#### Managing Consumer Groups

```bash
# List consumer groups
kubectl exec -it <kafka-pod-name> -- bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list

# Describe consumer group
kubectl exec -it <kafka-pod-name> -- bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group <group-name>
```

## Troubleshooting

### Common Issues

#### Consumer Lag Increasing
1. Check consumer logs: `kubectl logs -l app=kafka-consumers -n todo-app`
2. Verify consumer group status: `kubectl exec -it <kafka-pod> -- bin/kafka-consumer-groups.sh ...`
3. Increase consumer replicas or optimize processing logic

#### Producer Failures
1. Check producer logs: `kubectl logs -l app=kafka-producers -n todo-app`
2. Verify network connectivity to Kafka
3. Check authentication credentials

#### High Memory Usage
1. Monitor garbage collection if using JVM-based Kafka
2. Tune batch sizes and buffer memory settings
3. Consider increasing pod resource limits

### Diagnostic Commands

```bash
# Check all resources in namespace
kubectl get all -n todo-app

# Describe specific pod for detailed info
kubectl describe pod <pod-name> -n todo-app

# Port forward to access health/metrics endpoints
kubectl port-forward -n todo-app deploy/kafka-consumers 8000:8000

# Check events for issues
kubectl get events -n todo-app --sort-by='.lastTimestamp'
```

## Scaling Guidelines

### Vertical Scaling
- Increase CPU/memory limits gradually based on observed usage
- Monitor CPU and memory utilization metrics
- Consider the impact on garbage collection for JVM-based components

### Horizontal Scaling
- Use HPA based on CPU/memory or custom metrics
- For consumer scaling, consider partition count vs consumer count ratio
- Ensure adequate partition distribution for optimal parallelism

### Performance Tuning
- Adjust batch size and linger.ms for throughput optimization
- Tune buffer.memory for high-throughput scenarios
- Configure appropriate retry and timeout values for reliability

---

For further assistance, contact the development team or consult the application logs.