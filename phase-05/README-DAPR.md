# DAPR Integration for Taskflow Application

This document describes how to run the actual Taskflow application (backend, frontend, mcp-server) with DAPR integration.

## 🚀 Prerequisites

- Kubernetes cluster (tested with Minikube)
- Helm 3.x
- DAPR installed in Kubernetes cluster
- Docker (for local image building)

## 🏗️ Architecture

The Taskflow application consists of three main services with DAPR integration:
- **taskflow-backend**: Backend API service
- **taskflow-frontend**: Frontend web application
- **taskflow-mcp-server**: MCP server component

All services have DAPR sidecars for:
- Service-to-service invocation
- Pub/Sub messaging
- State management
- Configuration management
- Observability

## 📦 Deployment with Helm

The recommended way to deploy the Taskflow application is using the Helm chart:

```bash
# Deploy Taskflow with DAPR integration
helm install taskflow phase-05/charts/taskflow --values phase-05/charts/taskflow/values.yaml
```

To upgrade an existing deployment:
```bash
helm upgrade taskflow phase-05/charts/taskflow --values phase-05/charts/taskflow/values.yaml
```

## ⚙️ Configuration

The Helm chart includes DAPR integration by default. You can customize the DAPR settings in `values.yaml`:

```yaml
dapr:
  enabled: true          # Enable DAPR integration
  config: "dapr-config"  # DAPR configuration name
  logLevel: "info"       # DAPR log level
```

## 🛠️ Verifying Deployment

Check that services are running with DAPR sidecars:

```bash
# Check pods (should show 2/2 Ready for services with DAPR)
kubectl get pods

# Verify DAPR annotations on pods
kubectl describe pod [taskflow-pod-name] | grep -A 5 "Annotations:"

# Look for these DAPR annotations:
# - dapr.io/enabled: "true"
# - dapr.io/app-id: "taskflow-[service-name]"
# - dapr.io/app-port: "[port-number]"
```

Check services:
```bash
kubectl get services
```

## 📊 DAPR Components

The following DAPR components are configured:
- **pubsub**: In-memory pub/sub for messaging
- **config**: DAPR configuration with tracing and metrics

## 🔧 DAPR Operations

### Service Invocation
Use DAPR for service-to-service communication:
```bash
dapr invoke --app-id taskflow-backend --method [method-name]
```

### Pub/Sub Messaging
Publish and subscribe to events via DAPR pub/sub:
- Events can be published to the in-memory pubsub component
- Services can subscribe to topics for event-driven communication

### Health Checks
Monitor service health through DAPR sidecars:
- DAPR sidecars expose health endpoints
- Services include health probes

## 📈 Auto-scaling

The deployment includes Horizontal Pod Autoscaler (HPA) configurations:
- Scales from 1 to 50 replicas based on CPU/Memory usage
- Configurable in the values.yaml file

## 🧪 Verification

To verify the deployment is working:

1. Check that all pods are running:
   ```bash
   kubectl get pods
   ```

2. Verify DAPR annotations are present:
   ```bash
   kubectl describe pod taskflow-frontend-[hash] | grep dapr
   ```

3. Check that services are accessible:
   ```bash
   kubectl get services
   ```

4. Verify DAPR status:
   ```bash
   ./dapr status -k
   ```

## 🗑️ Cleanup

To remove the deployment:
```bash
helm uninstall taskflow
```

## 🔄 Updating

To update the application with new changes:
1. Update the Helm chart templates if needed
2. Run `helm upgrade` command
3. Verify the deployment

## ⚠️ Notes

- This deployment does NOT include the sample DAPR applications (publisher-app, subscriber-app, etc.)
- Only the actual Taskflow services (backend, frontend, mcp-server) are deployed
- DAPR sidecars are injected automatically via the Helm chart annotations
- Auto-scaling is configured from 1 to 50 instances as per requirements