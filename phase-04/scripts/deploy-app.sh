#!/bin/bash

# Script to deploy the Taskflow application using Helm

set -e

# Default values
NAMESPACE="taskflow"
CHART_PATH="./charts/taskflow"
RELEASE_NAME="taskflow-release"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        -c|--chart)
            CHART_PATH="$2"
            shift 2
            ;;
        -r|--release)
            RELEASE_NAME="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -n, --namespace STRING   Namespace to deploy to (default: taskflow)"
            echo "  -c, --chart STRING       Path to the Helm chart (default: ./charts/taskflow)"
            echo "  -r, --release STRING     Release name (default: taskflow-release)"
            echo "  -h, --help              Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "Deploying Taskflow application to namespace: $NAMESPACE"

# Create namespace if it doesn't exist
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

# Install or upgrade the Helm release
if helm status "$RELEASE_NAME" -n "$NAMESPACE" >/dev/null 2>&1; then
    echo "Upgrading existing release: $RELEASE_NAME"
    helm upgrade "$RELEASE_NAME" "$CHART_PATH" -n "$NAMESPACE" --wait
else
    echo "Installing new release: $RELEASE_NAME"
    helm install "$RELEASE_NAME" "$CHART_PATH" -n "$NAMESPACE" --wait
fi

echo "Application deployed successfully!"

# Show deployment status
kubectl get pods -n "$NAMESPACE"
kubectl get services -n "$NAMESPACE"
kubectl get ingress -n "$NAMESPACE"

echo "Deployment complete!"
