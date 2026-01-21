# DAPR Implementation Quickstart Guide

## Prerequisites

- Kubernetes cluster (Minikube, Kind, or cloud-based)
- Helm 3.x
- DAPR CLI
- Docker
- kubectl

## Install DAPR on Kubernetes

```bash
# Install DAPR CLI (if not already installed)
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Initialize DAPR in Kubernetes
dapr init --wait

# Verify installation
dapr status -k
```

## Deploy DAPR Components

### 1. Create DAPR Components Directory
```bash
mkdir -p dapr-components
```

### 2. Create State Store Component (Redis)
Create `dapr-components/statestore.yaml`:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: redis-master:6379
  - name: redisPassword
    value: ""
  - name: actorStateStore
    value: "true"
```

### 3. Create Pub/Sub Component (NATS)
Create `dapr-components/pubsub.yaml`:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
spec:
  type: pubsub.nats
  version: v1
  metadata:
  - name: natsURL
    value: "nats://nats:4222"
```

### 4. Apply Components to Kubernetes
```bash
kubectl apply -f dapr-components/
```

## Deploy Sample Application with DAPR Sidecar

### 1. Create Application Deployment
Create `k8s/sample-app.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sample-app
  labels:
    app: sample-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: sample-app
  template:
    metadata:
      labels:
        app: sample-app
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "sample-app"
        dapr.io/app-port: "8080"
        dapr.io/log-level: "debug"
    spec:
      containers:
      - name: app
        image: nginx:latest
        ports:
        - containerPort: 8080
        env:
        - name: PORT
          value: "8080"
---
apiVersion: v1
kind: Service
metadata:
  name: sample-app
spec:
  selector:
    app: sample-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
  type: LoadBalancer
```

### 2. Deploy the Application
```bash
kubectl apply -f k8s/sample-app.yaml
```

## Test DAPR Functionality

### 1. Verify DAPR Sidecar Injection
```bash
kubectl get pods
# You should see 2 containers in your sample-app pod (app + daprd)
```

### 2. Test State Management
```bash
# Save state
dapr save bulk -k statestore -p '{"key1":{"value":"data1"},"key2":{"value":"data2"}}'

# Get state
dapr get statestore key1
```

### 3. Test Service Invocation
```bash
# Call the sample app through DAPR
dapr invoke --app-id sample-app --method healthz
```

### 4. Test Pub/Sub (if using the pubsub component)
```bash
# Publish a test message
curl -X POST http://localhost:3500/v1.0/publish/pubsub/topic1 -H "Content-Type: application/json" -d '{"message": "Hello DAPR"}'
```

## Production Considerations

### 1. Secure Installation
```bash
# For production, use secured Redis
helm install redis stable/redis \
  --set auth.enabled=true \
  --set auth.password=<secure-password>
```

### 2. Configure Production-Ready Components
- Use production-grade message brokers (RabbitMQ, Kafka)
- Configure proper authentication and encryption
- Set up monitoring and alerting

### 3. Auto-Scaling Configuration
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: sample-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: sample-app
  minReplicas: 1
  maxReplicas: 50
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Troubleshooting

### Common Issues
1. **Sidecar not injected**: Verify the `dapr.io/enabled: "true"` annotation
2. **State store not working**: Check Redis connection and credentials
3. **Service invocation failing**: Verify app-id matches between caller and callee

### Useful Commands
```bash
# Check DAPR logs
kubectl logs -l app=sample-app -c daprd

# Check DAPR status
dapr status -k

# Get DAPR configuration
dapr configurations -k
```