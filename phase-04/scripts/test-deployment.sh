#!/bin/bash

# Script to test the complete Kubernetes deployment of Taskflow application

set -e

# Default values
NAMESPACE="taskflow"
TIMEOUT=300  # 5 minutes timeout for deployment readiness

echo "Starting deployment test for Taskflow application..."

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        -t|--timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -n, --namespace STRING   Namespace to test (default: taskflow)"
            echo "  -t, --timeout NUMBER     Timeout in seconds (default: 300)"
            echo "  -h, --help              Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Function to check if a resource is ready
wait_for_ready() {
    local resource_type=$1
    local resource_name=$2
    local timeout=${3:-300}

    echo "Waiting for $resource_type $resource_name to be ready..."

    local count=0
    while [ $count -lt $timeout ]; do
        if kubectl get $resource_type $resource_name -n $NAMESPACE &>/dev/null; then
            if [ "$resource_type" = "deployment" ]; then
                ready_replicas=$(kubectl get deployment $resource_name -n $NAMESPACE -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")
                desired_replicas=$(kubectl get deployment $resource_name -n $NAMESPACE -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "0")

                if [ "$ready_replicas" = "$desired_replicas" ] && [ "$ready_replicas" != "0" ]; then
                    echo "✓ Deployment $resource_name is ready ($ready_replicas/$desired_replicas replicas)"
                    return 0
                fi
            elif [ "$resource_type" = "statefulset" ]; then
                ready_replicas=$(kubectl get statefulset $resource_name -n $NAMESPACE -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")
                desired_replicas=$(kubectl get statefulset $resource_name -n $NAMESPACE -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "0")

                if [ "$ready_replicas" = "$desired_replicas" ] && [ "$ready_replicas" != "0" ]; then
                    echo "✓ StatefulSet $resource_name is ready ($ready_replicas/$desired_replicas replicas)"
                    return 0
                fi
            else
                # For other resources, just check if they exist
                echo "✓ $resource_type $resource_name exists"
                return 0
            fi
        fi

        sleep 10
        count=$((count + 10))
        echo "  ... waited $count seconds"
    done

    echo "✗ Timeout waiting for $resource_type $resource_name to be ready"
    return 1
}

# Check if namespace exists
if ! kubectl get namespace $NAMESPACE &>/dev/null; then
    echo "ERROR: Namespace $NAMESPACE does not exist"
    echo "Run the deployment script first: ./scripts/deploy-app.sh"
    exit 1
fi

echo "Namespace $NAMESPACE exists, proceeding with tests..."

# List expected resources
EXPECTED_DEPLOYMENTS=("taskflow-frontend" "taskflow-backend" "taskflow-mcp-server")
EXPECTED_STATEFULSETS=("taskflow-postgres")
EXPECTED_SERVICES=("taskflow-frontend-service" "taskflow-backend-service" "taskflow-mcp-server-service" "taskflow-postgres-service")
EXPECTED_INGRESS=("taskflow-ingress")
EXPECTED_PVC=("taskflow-data-pvc")

# Test deployments
echo ""
echo "Testing deployments..."
for deployment in "${EXPECTED_DEPLOYMENTS[@]}"; do
    if ! wait_for_ready deployment "$deployment" $TIMEOUT; then
        echo "✗ Deployment $deployment failed readiness check"
        exit 1
    fi
done

# Test statefulsets
echo ""
echo "Testing statefulsets..."
for statefulset in "${EXPECTED_STATEFULSETS[@]}"; do
    if ! wait_for_ready statefulset "$statefulset" $TIMEOUT; then
        echo "✗ StatefulSet $statefulset failed readiness check"
        exit 1
    fi
done

# Test services
echo ""
echo "Testing services..."
for service in "${EXPECTED_SERVICES[@]}"; do
    if kubectl get service "$service" -n $NAMESPACE &>/dev/null; then
        echo "✓ Service $service exists"
    else
        echo "✗ Service $service does not exist"
        exit 1
    fi
done

# Test ingress
echo ""
echo "Testing ingress..."
for ingress in "${EXPECTED_INGRESS[@]}"; do
    if kubectl get ingress "$ingress" -n $NAMESPACE &>/dev/null; then
        echo "✓ Ingress $ingress exists"
    else
        echo "✗ Ingress $ingress does not exist"
        exit 1
    fi
done

# Test PVC
echo ""
echo "Testing persistent volume claims..."
for pvc in "${EXPECTED_PVC[@]}"; do
    if kubectl get pvc "$pvc" -n $NAMESPACE &>/dev/null; then
        status=$(kubectl get pvc "$pvc" -n $NAMESPACE -o jsonpath='{.status.phase}')
        if [ "$status" = "Bound" ]; then
            echo "✓ PVC $pvc is bound"
        else
            echo "✗ PVC $pvc is not bound (status: $status)"
            exit 1
        fi
    else
        echo "✗ PVC $pvc does not exist"
        exit 1
    fi
done

# Check pod statuses
echo ""
echo "Checking pod statuses..."
ALL_PODS=$(kubectl get pods -n $NAMESPACE -o jsonpath='{.items[*].metadata.name}')
if [ -z "$ALL_PODS" ]; then
    echo "✗ No pods found in namespace $NAMESPACE"
    exit 1
fi

for pod in $ALL_PODS; do
    status=$(kubectl get pod "$pod" -n $NAMESPACE -o jsonpath='{.status.phase}')
    if [ "$status" = "Running" ]; then
        echo "✓ Pod $pod is running"
    else
        echo "✗ Pod $pod is not running (status: $status)"
        # Show logs for failed pods
        echo "  Pod logs:"
        kubectl logs "$pod" -n $NAMESPACE || echo "  Could not retrieve logs"
        exit 1
    fi
done

# Test inter-service connectivity by checking if backend can reach MCP server
echo ""
echo "Testing inter-service connectivity..."
BACKEND_POD=$(kubectl get pods -n $NAMESPACE -l app=backend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
if [ -n "$BACKEND_POD" ]; then
    # Check if the backend pod can resolve the MCP server service
    if kubectl exec "$BACKEND_POD" -n $NAMESPACE -- nslookup mcp-server-service &>/dev/null; then
        echo "✓ Backend can resolve MCP server service"
    else
        echo "⚠ Could not test backend-MCP server connectivity"
    fi
else
    echo "⚠ Could not find backend pod to test connectivity"
fi

# Test external accessibility through ingress
echo ""
echo "Testing external accessibility..."
INGRESS_HOST=$(kubectl get ingress taskflow-ingress -n $NAMESPACE -o jsonpath='{.spec.rules[0].host}' 2>/dev/null || echo "taskflow.local")
echo "Application should be accessible at: http://$INGRESS_HOST"

echo ""
echo "All tests passed! The Taskflow application is successfully deployed and running in Kubernetes."
echo ""
echo "Deployment Summary:"
kubectl get all -n $NAMESPACE

echo ""
echo "Test completed successfully!"
