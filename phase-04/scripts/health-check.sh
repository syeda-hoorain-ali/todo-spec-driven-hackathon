#!/bin/bash

# Health check script for Taskflow application

set -e

# Default values
NAMESPACE="taskflow"
RELEASE_NAME="taskflow-release"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        -r|--release)
            RELEASE_NAME="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -n, --namespace STRING   Namespace to check (default: taskflow)"
            echo "  -r, --release STRING     Release name to check (default: taskflow-release)"
            echo "  -h, --help              Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "Checking health of Taskflow application in namespace: $NAMESPACE"

# Check if the namespace exists
if ! kubectl get namespace "$NAMESPACE" >/dev/null 2>&1; then
    echo "ERROR: Namespace $NAMESPACE does not exist"
    exit 1
fi

# Check deployment statuses
echo "Checking deployments..."
DEPLOYMENTS=$(kubectl get deployments -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}')
for deployment in $DEPLOYMENTS; do
    READY_REPLICAS=$(kubectl get deployment "$deployment" -n "$NAMESPACE" -o jsonpath='{.status.readyReplicas}')
    DESIRED_REPLICAS=$(kubectl get deployment "$deployment" -n "$NAMESPACE" -o jsonpath='{.spec.replicas}')

    if [ "$READY_REPLICAS" = "$DESIRED_REPLICAS" ] && [ "$READY_REPLICAS" != "0" ]; then
        echo "✓ Deployment $deployment is healthy ($READY_REPLICAS/$DESIRE_REPLICAS replicas ready)"
    else
        echo "✗ Deployment $deployment is not healthy ($READY_REPLICAS/$DESIRE_REPLICAS replicas ready)"
    fi
done

# Check pod statuses
echo "Checking pods..."
PODS=$(kubectl get pods -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}')
for pod in $PODS; do
    STATUS=$(kubectl get pod "$pod" -n "$NAMESPACE" -o jsonpath='{.status.phase}')
    if [ "$STATUS" = "Running" ]; then
        echo "✓ Pod $pod is running"
    else
        echo "✗ Pod $pod is not running (status: $STATUS)"
    fi
done

# Check service statuses
echo "Checking services..."
SERVICES=$(kubectl get services -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}')
for service in $SERVICES; do
    echo "✓ Service $service exists"
done

# Check ingress status
INGRESS=$(kubectl get ingress -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}' 2>/dev/null || echo "")
if [ -n "$INGRESS" ]; then
    echo "Checking ingress..."
    for ing in $INGRESS; do
        ADDRESS=$(kubectl get ingress "$ing" -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
        if [ "$ADDRESS" != "pending" ]; then
            echo "✓ Ingress $ing is available at $ADDRESS"
        else
            echo "⚠ Ingress $ing is still pending"
        fi
    done
else
    echo "No ingress resources found"
fi

echo "Health check complete!"
