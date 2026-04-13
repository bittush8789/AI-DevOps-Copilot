# Setup Guide

This guide will help you set up the AI DevOps Copilot in both local (Kind) and production (EKS) environments.

## Prerequisites

### Local Development
- Docker Desktop
- Kind (Kubernetes in Docker)
- kubectl
- Node.js 18+ and npm
- Python 3.11+

### Production Deployment
- AWS CLI configured with appropriate credentials
- Terraform >= 1.0
- kubectl
- Docker (for building images)

## AWS Bedrock Setup

1. **Enable Bedrock Models**
   - Go to AWS Console → Bedrock → Model access
   - Request access to Claude 3 Sonnet model
   - Wait for approval (usually instant for most regions)

2. **Create IAM User/Role**
   ```bash
   # Create IAM policy for Bedrock access
   aws iam create-policy \
     --policy-name BedrockAccess \
     --policy-document '{
       "Version": "2012-10-17",
       "Statement": [{
         "Effect": "Allow",
         "Action": [
           "bedrock:InvokeModel",
           "bedrock:InvokeModelWithResponseStream"
         ],
         "Resource": "*"
       }]
     }'
   ```

## Local Development Setup

### 1. Install Dependencies

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### 2. Configure Environment

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and add your AWS credentials:
```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
```

### 3. Run Locally (Without Kubernetes)

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Access the application at http://localhost:3000

### 4. Deploy to Kind Cluster

Make the deployment script executable:
```bash
chmod +x scripts/deploy-kind.sh scripts/cleanup-kind.sh
```

Deploy:
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
./scripts/deploy-kind.sh
```

Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Production Deployment (EKS)

### 1. Deploy EKS Cluster

```bash
cd terraform/eks

# Copy and edit variables
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your settings

# Initialize and apply
terraform init
terraform plan
terraform apply
```

This will create:
- VPC with public and private subnets
- EKS cluster with managed node groups
- IAM roles for Bedrock access
- Security groups

### 2. Configure kubectl

```bash
aws eks update-kubeconfig --name ai-devops-copilot --region us-east-1
```

### 3. (Optional) Deploy OpenSearch

```bash
cd terraform/opensearch

# Copy and edit variables
cp terraform.tfvars.example terraform.tfvars

# Get VPC and subnet IDs from EKS outputs
terraform -chdir=../eks output vpc_id
terraform -chdir=../eks output private_subnets

# Edit terraform.tfvars with the VPC and subnet IDs

# Initialize and apply
terraform init
terraform plan
terraform apply
```

### 4. Create Kubernetes Secrets

```bash
# AWS credentials (if not using IRSA)
kubectl create secret generic aws-credentials \
  --from-literal=access_key_id=$AWS_ACCESS_KEY_ID \
  --from-literal=secret_access_key=$AWS_SECRET_ACCESS_KEY \
  -n ai-devops

# OpenSearch credentials (if using OpenSearch)
kubectl create secret generic opensearch-credentials \
  --from-literal=username=admin \
  --from-literal=password=YourSecurePassword \
  -n ai-devops

# Pinecone credentials (if using Pinecone)
kubectl create secret generic pinecone-credentials \
  --from-literal=api_key=your_pinecone_api_key \
  -n ai-devops
```

### 5. Build and Push Docker Images

```bash
# Set your ECR repository
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export AWS_REGION=us-east-1
export ECR_REPO=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Create ECR repositories
aws ecr create-repository --repository-name ai-devops-backend
aws ecr create-repository --repository-name ai-devops-frontend

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin $ECR_REPO

# Build and push backend
cd backend
docker build -t $ECR_REPO/ai-devops-backend:latest .
docker push $ECR_REPO/ai-devops-backend:latest

# Build and push frontend
cd ../frontend
docker build -t $ECR_REPO/ai-devops-frontend:latest .
docker push $ECR_REPO/ai-devops-frontend:latest
```

### 6. Update Kubernetes Manifests

Edit `k8s/base/backend-deployment.yaml` and `k8s/base/frontend-deployment.yaml` to use your ECR images:

```yaml
image: <AWS_ACCOUNT_ID>.dkr.ecr.<AWS_REGION>.amazonaws.com/ai-devops-backend:latest
```

### 7. Deploy to EKS

```bash
kubectl apply -k k8s/overlays/production
```

### 8. Install AWS Load Balancer Controller

```bash
# Add the EKS chart repo
helm repo add eks https://aws.github.io/eks-charts
helm repo update

# Install the controller
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=ai-devops-copilot \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller
```

### 9. Get Application URL

```bash
kubectl get ingress -n ai-devops
```

The ALB DNS name will be shown in the ADDRESS column.

## Configuration

### Vector Database Options

**Option 1: OpenSearch (Recommended for production)**
- Deployed via Terraform
- Fully managed by AWS
- Better for large-scale deployments

**Option 2: Pinecone**
- SaaS vector database
- Easier setup
- Good for getting started quickly

Update the ConfigMap in `k8s/base/configmap.yaml`:
```yaml
data:
  vector_db_type: "opensearch"  # or "pinecone"
  opensearch_endpoint: "https://your-opensearch-endpoint"
```

### Bedrock Model Selection

Available models:
- `anthropic.claude-3-sonnet-20240229-v1:0` (Default, balanced)
- `anthropic.claude-3-haiku-20240307-v1:0` (Faster, cheaper)
- `anthropic.claude-3-opus-20240229-v1:0` (Most capable)

Update in ConfigMap:
```yaml
data:
  bedrock_model_id: "anthropic.claude-3-sonnet-20240229-v1:0"
```

## Monitoring

### View Logs

```bash
# Backend logs
kubectl logs -f deployment/backend -n ai-devops

# Frontend logs
kubectl logs -f deployment/frontend -n ai-devops

# All pods
kubectl logs -f -l app.kubernetes.io/name=ai-devops-copilot -n ai-devops
```

### Check Pod Status

```bash
kubectl get pods -n ai-devops
kubectl describe pod <pod-name> -n ai-devops
```

### Metrics

The backend exposes Prometheus metrics at `/metrics`:
```bash
kubectl port-forward -n ai-devops svc/backend 8000:8000
curl http://localhost:8000/metrics
```

## Troubleshooting

### Backend Pod Not Starting

1. Check logs:
   ```bash
   kubectl logs deployment/backend -n ai-devops
   ```

2. Verify AWS credentials:
   ```bash
   kubectl get secret aws-credentials -n ai-devops -o yaml
   ```

3. Test Bedrock access:
   ```bash
   kubectl exec -it deployment/backend -n ai-devops -- python -c "
   import boto3
   client = boto3.client('bedrock-runtime', region_name='us-east-1')
   print('Bedrock client created successfully')
   "
   ```

### Frontend Not Accessible

1. Check service:
   ```bash
   kubectl get svc frontend -n ai-devops
   ```

2. Check ingress:
   ```bash
   kubectl describe ingress -n ai-devops
   ```

3. Verify ALB controller:
   ```bash
   kubectl get pods -n kube-system | grep aws-load-balancer
   ```

### Vector Database Connection Issues

1. Check OpenSearch endpoint:
   ```bash
   kubectl get configmap ai-devops-config -n ai-devops -o yaml
   ```

2. Test connectivity:
   ```bash
   kubectl exec -it deployment/backend -n ai-devops -- curl -k https://your-opensearch-endpoint
   ```

## Cleanup

### Local (Kind)

```bash
./scripts/cleanup-kind.sh
```

### Production (EKS)

```bash
# Delete Kubernetes resources
kubectl delete -k k8s/overlays/production

# Destroy OpenSearch (if deployed)
cd terraform/opensearch
terraform destroy

# Destroy EKS cluster
cd ../eks
terraform destroy
```

## Next Steps

1. **Upload Knowledge Base**: Use the `/api/v1/chat/upload-knowledge` endpoint to add your runbooks and documentation
2. **Configure Monitoring**: Set up CloudWatch or Prometheus for production monitoring
3. **Enable HTTPS**: Configure ACM certificate and update ingress annotations
4. **Set up CI/CD**: Create GitHub Actions workflows for automated deployments
5. **Backup Strategy**: Configure regular backups for OpenSearch data

## Support

For issues and questions:
- Check the logs first
- Review the API documentation at `/docs`
- Ensure AWS credentials have correct permissions
- Verify Bedrock model access is enabled
