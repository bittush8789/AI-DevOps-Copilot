#!/bin/bash
set -e

echo "🧹 Cleaning up AI DevOps Copilot from Kind..."

# Delete Kubernetes resources
echo "Deleting Kubernetes resources..."
kubectl delete -k k8s/overlays/kind --ignore-not-found=true

# Delete Kind cluster
echo "Deleting Kind cluster..."
kind delete cluster --name ai-devops

echo "✅ Cleanup complete!"
