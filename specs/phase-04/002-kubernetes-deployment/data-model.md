# Data Model: Kubernetes Deployment for Taskflow

## Kubernetes Resources

### Frontend Deployment
- **Name**: frontend-deployment
- **Container Image**: taskflow-frontend:latest
- **Ports**: 3000 (Next.js server)
- **Environment Variables**:
  - REACT_APP_API_URL: URL of the backend service
  - NODE_ENV: production/development
- **Resource Requests**: 128Mi memory, 100m CPU
- **Resource Limits**: 256Mi memory, 200m CPU
- **Health Checks**:
  - Readiness probe on /api/health
  - Liveness probe on /api/health

### Backend Deployment
- **Name**: backend-deployment
- **Container Image**: taskflow-backend:latest
- **Ports**: 8000 (FastAPI server)
- **Environment Variables**:
  - MCP_SERVER_URL: URL of the MCP server service (e.g., http://mcp-server:8080)
  - DATABASE_URL: PostgreSQL connection string
  - API_KEY: Authentication key if needed
- **Resource Requests**: 256Mi memory, 200m CPU
- **Resource Limits**: 512Mi memory, 400m CPU
- **Health Checks**:
  - Readiness probe on /health
  - Liveness probe on /health

### MCP Server Deployment
- **Name**: mcp-server-deployment
- **Container Image**: taskflow-mcp-server:latest
- **Ports**: 8080 (MCP server)
- **Environment Variables**:
  - GEMINI_API_KEY: API key for the Gemini service
  - LOG_LEVEL: Logging verbosity
- **Resource Requests**: 512Mi memory, 300m CPU
- **Resource Limits**: 1Gi memory, 600m CPU
- **Health Checks**:
  - Readiness probe on /health
  - Liveness probe on /health

## Kubernetes Services

### Frontend Service
- **Name**: frontend-service
- **Type**: LoadBalancer
- **Port**: 80
- **Target Port**: 3000
- **Selector**: app=frontend

### Backend Service
- **Name**: backend-service
- **Type**: LoadBalancer
- **Port**: 80
- **Target Port**: 8000
- **Selector**: app=backend

### MCP Server Service
- **Name**: mcp-server-service
- **Type**: LoadBalancer
- **Port**: 80
- **Target Port**: 8080
- **Selector**: app=mcp-server

## Persistent Storage

### Database PersistentVolumeClaim
- **Name**: postgres-pvc
- **Storage Class**: standard (or hostpath for local development)
- **Size**: 10Gi
- **Access Mode**: ReadWriteOnce
- **Volume Mode**: Filesystem

## Configurations

### Frontend ConfigMap
- **Name**: frontend-config
- **Data**:
  - API_BASE_URL: http://backend-service:80

### Backend ConfigMap
- **Name**: backend-config
- **Data**:
  - MCP_SERVER_URL: http://mcp-server-service:80
  - LOG_LEVEL: INFO

### Secrets
- **Name**: app-secrets
- **Data**:
  - DATABASE_URL: (base64 encoded)
  - GEMINI_API_KEY: (base64 encoded)
  - JWT_SECRET: (base64 encoded)

## Ingress

### Application Ingress
- **Name**: taskflow-ingress
- **Host**: taskflow.local (for local development)
- **Paths**:
  - /: routes to frontend-service
  - /api/*: routes to backend-service
- **TLS**: Enabled with TLS termination at ingress controller

## Network Policies (Optional)
- **Name**: app-network-policy
- **Rules**: Allow traffic between services only on specified ports
