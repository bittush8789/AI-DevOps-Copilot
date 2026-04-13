# AI DevOps Copilot 🤖

An intelligent AI assistant for DevOps engineers powered by AWS Bedrock models (Claude/Titan).

## Features

- 🔍 **Ask Infrastructure Questions** - Get instant answers about your infrastructure ("Why is my pod crashing?")
- 📊 **Log Analysis** - Analyze logs from CloudWatch, Loki, and Kubernetes
- 🛠️ **Code Generation** - Generate Terraform, Kubernetes YAML, and GitHub Actions pipelines
- 🔎 **Root Cause Analysis** - Get intelligent RCA suggestions for incidents
- 📚 **RAG-Powered** - Vector search over your runbooks, documentation, and logs
- 🎨 **Beautiful UI** - Modern, responsive interface built with React and TailwindCSS

## Tech Stack

### Backend
- **FastAPI** - High-performance Python web framework
- **AWS Bedrock** - Claude 3 and Titan models
- **Vector DB** - OpenSearch/Pinecone for RAG
- **Kubernetes Client** - For cluster interaction

### Frontend
- **React 18** - Modern UI framework
- **TailwindCSS** - Utility-first CSS
- **shadcn/ui** - Beautiful component library
- **Lucide Icons** - Modern icon set

### Infrastructure
- **EKS** - Production Kubernetes on AWS
- **Kind** - Local development cluster
- **Terraform** - Infrastructure as Code
- **GitHub Actions** - CI/CD pipelines

## Quick Start

### Local Development (Kind)

1. **Prerequisites**
   ```bash
   # Install Kind
   brew install kind
   
   # Install kubectl
   brew install kubectl
   
   # Install Docker Desktop
   ```

2. **Setup AWS Credentials**
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_REGION=us-east-1
   ```

3. **Deploy to Kind**
   ```bash
   ./scripts/deploy-kind.sh
   ```

4. **Access the Application**
   ```bash
   kubectl port-forward -n ai-devops svc/frontend 3000:80
   kubectl port-forward -n ai-devops svc/backend 8000:8000
   ```
   
   Open http://localhost:3000

### Production Deployment (EKS)

1. **Deploy Infrastructure**
   ```bash
   cd terraform/eks
   terraform init
   terraform plan
   terraform apply
   ```

2. **Configure kubectl**
   ```bash
   aws eks update-kubeconfig --name ai-devops-copilot --region us-east-1
   ```

3. **Deploy Application**
   ```bash
   kubectl apply -k k8s/overlays/production
   ```

## Project Structure

```
ai_devops_copilot/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── services/    # Business logic
│   │   ├── models/      # Data models
│   │   └── core/        # Core configuration
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # UI components
│   │   ├── pages/       # Page components
│   │   ├── hooks/       # Custom hooks
│   │   └── lib/         # Utilities
│   ├── package.json
│   └── Dockerfile
├── k8s/                 # Kubernetes manifests
│   ├── base/           # Base configurations
│   └── overlays/       # Environment-specific
├── terraform/          # Infrastructure code
│   ├── eks/           # EKS cluster
│   ├── opensearch/    # Vector database
│   └── modules/       # Reusable modules
└── scripts/           # Utility scripts
```

## Configuration

### Environment Variables

**Backend:**
- `AWS_REGION` - AWS region for Bedrock
- `BEDROCK_MODEL_ID` - Model ID (default: anthropic.claude-3-sonnet-20240229-v1:0)
- `VECTOR_DB_TYPE` - opensearch or pinecone
- `OPENSEARCH_ENDPOINT` - OpenSearch endpoint
- `PINECONE_API_KEY` - Pinecone API key (if using Pinecone)

**Frontend:**
- `VITE_API_URL` - Backend API URL

## Development

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

## Features Documentation

### 1. Ask Questions
Use natural language to query your infrastructure:
- "Why is my pod in CrashLoopBackOff?"
- "Show me high CPU usage pods"
- "What's causing the latency spike?"

### 2. Log Analysis
Analyze logs from multiple sources:
- CloudWatch Logs
- Kubernetes pod logs
- Loki queries

### 3. Code Generation
Generate production-ready code:
- Terraform modules
- Kubernetes deployments
- GitHub Actions workflows
- Helm charts

### 4. Root Cause Analysis
Get AI-powered RCA suggestions based on:
- Log patterns
- Metric anomalies
- Historical incidents

## Contributing

Contributions welcome! Please read our contributing guidelines.

## License

MIT License
# AI-DevOps-Copilot
