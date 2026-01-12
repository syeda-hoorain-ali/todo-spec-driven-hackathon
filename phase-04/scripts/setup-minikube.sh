#!/bin/bash

# Script to set up Minikube for the Taskflow application

set -e

echo "Setting up Minikube for Taskflow application..."

# Check if Minikube is installed
if ! command -v minikube &> /dev/null; then
    echo "Minikube is not installed. Please install it first:"
    echo "  For macOS: brew install minikube"
    echo "  For Ubuntu/Debian: curl -Lo minikube https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 && chmod +x minikube && sudo mv minikube /usr/local/bin/"
    echo "  For Windows: Download from https://minikube.sigs.k8s.io/docs/start/"
    echo ""
    echo "For Windows with Chocolatey: choco install minikube"
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "kubectl is not installed. Please install it first:"
    echo "  For macOS: brew install kubectl"
    echo "  For Ubuntu/Debian: sudo apt-get install kubectl"
    echo "  For Windows: Download from https://kubernetes.io/docs/tasks/tools/install-kubectl/"
    exit 1
fi

# Check if Helm is installed
if ! command -v helm &> /dev/null; then
    echo "Helm is not installed. Please install it first:"
    echo "  For macOS: brew install helm"
    echo "  For Ubuntu/Debian: curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash"
    echo "  For Windows: choco install kubernetes-helm"
    exit 1
fi

echo "All required tools are installed."

# Start Minikube with sufficient resources for our application
echo "Starting Minikube with 4 CPUs and 8GB of memory..."
minikube start --cpus=4 --memory=8192 --disk-size=20g

# Enable required addons
echo "Enabling required addons..."
minikube addons enable ingress
minikube addons enable metrics-server

# Verify the cluster is running
echo "Verifying cluster status..."
kubectl cluster-info

# Verify ingress controller is running
echo "Waiting for ingress controller to be ready..."
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=90s

echo "Minikube setup complete!"
echo "Current context: $(kubectl config current-context)"

echo ""
echo "You can now deploy the application using:"
echo "  ./scripts/deploy-app.sh"
