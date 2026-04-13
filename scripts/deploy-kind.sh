#!/bin/bash
set -e

# Load .env file if it exists
if [ -f "$(dirname "$0")/../.env" ]; then
    echo "📄 Loading .env file..."
    set -a
    source "$(dirname "$0")/../.env"
    set +a
fi

echo "🚀 Deploying AI DevOps Copilot to Kind cluster..."

# Check if kind cluster exists
if ! kind get clusters | grep -q "ai-devops"; then
    echo "📦 Creating Kind cluster..."
    kind create cluster --name ai-devops --config - <<EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  extraPortMappings:
  - containerPort: 30080
    hostPort: 3000
    protocol: TCP
  - containerPort: 30081
    hostPort: 8000
    protocol: TCP
EOF
else
    echo "✅ Kind cluster 'ai-devops' already exists"
fi

# Set kubectl context
kubectl config use-context kind-ai-devops

echo "🔨 Building Docker images..."
cd "$(dirname "$0")/.."

# Build backend
echo "Building backend..."
docker build -t ai-devops-backend:latest ./backend

# Build frontend
echo "Building frontend..."
docker build -t ai-devops-frontend:latest ./frontend

# Load images into kind
echo "📥 Loading images into Kind cluster..."
kind load docker-image ai-devops-backend:latest --name ai-devops
kind load docker-image ai-devops-frontend:latest --name ai-devops

# Deploy using kustomize (this creates the namespace)
echo "☸️  Deploying to Kubernetes..."
kubectl apply -k k8s/overlays/kind

# Create secrets if they don't exist
echo "🔐 Creating secrets..."
if ! kubectl get secret bedrock-credentials -n ai-devops &> /dev/null; then
    kubectl create secret generic bedrock-credentials \
        --from-literal=api_key="${AWS_BEARER_TOKEN_BEDROCK:-}" \
        -n ai-devops
fi
if ! kubectl get secret aws-credentials -n ai-devops &> /dev/null; then
    kubectl create secret generic aws-credentials \
        --from-literal=access_key_id="${AWS_ACCESS_KEY_ID:-}" \
        --from-literal=secret_access_key="${AWS_SECRET_ACCESS_KEY:-}" \
        -n ai-devops
fi

# Wait for deployments
echo "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s \
    deployment/backend deployment/frontend -n ai-devops

# Expose services
echo "🌐 Exposing services..."
kubectl patch service frontend -n ai-devops -p '{"spec":{"type":"NodePort","ports":[{"port":80,"nodePort":30080}]}}'
kubectl patch service backend -n ai-devops -p '{"spec":{"type":"NodePort","ports":[{"port":8000,"nodePort":30081}]}}'

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📍 Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📊 Useful commands:"
echo "   kubectl get pods -n ai-devops"
echo "   kubectl logs -f deployment/backend -n ai-devops"
echo "   kubectl logs -f deployment/frontend -n ai-devops"
echo "   kubectl port-forward -n ai-devops svc/frontend 3000:80"
echo "   kubectl port-forward -n ai-devops svc/backend 8000:8000"
echo ""
