# AI DevOps Copilot - Architecture

## System Architecture Diagram

```mermaid
graph TB
    subgraph "User Interface"
        UI[React Frontend<br/>TailwindCSS + shadcn/ui]
    end

    subgraph "Application Layer"
        ALB[AWS Application<br/>Load Balancer]
        NGINX[Nginx<br/>Reverse Proxy]
    end

    subgraph "Backend Services"
        API[FastAPI Backend<br/>Python 3.11]
        
        subgraph "Core Services"
            BEDROCK[Bedrock Service<br/>Claude 3 Sonnet]
            VECTOR[Vector Service<br/>Embeddings + Search]
            K8S[Kubernetes Service<br/>Pod Management]
        end
    end

    subgraph "AWS Services"
        BR[AWS Bedrock<br/>Claude 3 Models]
        CW[CloudWatch<br/>Logs & Metrics]
        IAM[IAM Roles<br/>IRSA]
    end

    subgraph "Vector Database"
        OS[OpenSearch<br/>Vector Store]
        PC[Pinecone<br/>Alternative]
    end

    subgraph "Kubernetes Cluster"
        subgraph "Control Plane"
            KAPI[Kubernetes API]
        end
        
        subgraph "Workloads"
            PODS[Application Pods]
            LOGS[Pod Logs]
            EVENTS[K8s Events]
        end
    end

    subgraph "Infrastructure"
        subgraph "Local Development"
            KIND[Kind Cluster<br/>Docker Desktop]
        end
        
        subgraph "Production"
            EKS[Amazon EKS<br/>Managed K8s]
            VPC[VPC<br/>Multi-AZ]
            NAT[NAT Gateway]
        end
    end

    UI -->|HTTPS| ALB
    ALB -->|Route /api| API
    ALB -->|Route /| NGINX
    NGINX -->|Serve Static| UI
    
    API -->|Invoke Model| BR
    API -->|Query/Index| OS
    API -->|Query/Index| PC
    API -->|Get Logs| CW
    API -->|List/Watch| KAPI
    API -->|Assume Role| IAM
    
    BEDROCK -->|API Call| BR
    VECTOR -->|Search| OS
    VECTOR -->|Search| PC
    K8S -->|kubectl| KAPI
    
    KAPI -->|Manage| PODS
    KAPI -->|Collect| LOGS
    KAPI -->|Monitor| EVENTS
    
    EKS -.->|Runs on| VPC
    KIND -.->|Local Dev| UI
    
    style UI fill:#61dafb,stroke:#333,stroke-width:2px
    style API fill:#009688,stroke:#333,stroke-width:2px
    style BR fill:#ff9900,stroke:#333,stroke-width:2px
    style OS fill:#005eb8,stroke:#333,stroke-width:2px
    style EKS fill:#ff9900,stroke:#333,stroke-width:2px
    style KIND fill:#326ce5,stroke:#333,stroke-width:2px
```

## Data Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant ALB
    participant Backend
    participant Bedrock
    participant VectorDB
    participant K8s

    User->>Frontend: Ask Question
    Frontend->>ALB: POST /api/v1/chat
    ALB->>Backend: Forward Request
    
    Backend->>VectorDB: Search Similar Docs
    VectorDB-->>Backend: Return Context
    
    Backend->>Bedrock: Generate Response<br/>(with RAG context)
    Bedrock-->>Backend: AI Response
    
    Backend-->>ALB: JSON Response
    ALB-->>Frontend: Forward Response
    Frontend-->>User: Display Answer
    
    Note over User,K8s: Log Analysis Flow
    
    User->>Frontend: Analyze Logs
    Frontend->>ALB: POST /api/v1/logs/analyze
    ALB->>Backend: Forward Request
    
    Backend->>K8s: Get Pod Logs
    K8s-->>Backend: Log Data
    
    Backend->>Bedrock: Analyze Logs
    Bedrock-->>Backend: Analysis + Issues
    
    Backend-->>Frontend: Analysis Results
    Frontend-->>User: Display Insights
```

## Component Architecture

```mermaid
graph LR
    subgraph "Frontend Components"
        CHAT[Chat Page]
        LOGS[Logs Page]
        GEN[Generate Page]
        ANALYZE[Analyze Page]
        LAYOUT[Layout Component]
    end

    subgraph "API Endpoints"
        CHAT_API[/api/v1/chat]
        LOGS_API[/api/v1/logs]
        GEN_API[/api/v1/generate]
        RCA_API[/api/v1/analyze]
        HEALTH[/api/v1/health]
    end

    subgraph "Backend Services"
        BEDROCK_SVC[BedrockService]
        VECTOR_SVC[VectorService]
        K8S_SVC[KubernetesService]
    end

    CHAT --> CHAT_API
    LOGS --> LOGS_API
    GEN --> GEN_API
    ANALYZE --> RCA_API
    
    CHAT_API --> BEDROCK_SVC
    CHAT_API --> VECTOR_SVC
    LOGS_API --> K8S_SVC
    LOGS_API --> BEDROCK_SVC
    GEN_API --> BEDROCK_SVC
    RCA_API --> BEDROCK_SVC
    RCA_API --> K8S_SVC
    
    style CHAT fill:#61dafb
    style LOGS fill:#61dafb
    style GEN fill:#61dafb
    style ANALYZE fill:#61dafb
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "AWS Cloud"
        subgraph "Region: us-east-1"
            subgraph "VPC: 10.0.0.0/16"
                subgraph "Public Subnets"
                    ALB2[Application<br/>Load Balancer]
                    NAT1[NAT Gateway<br/>AZ-1]
                    NAT2[NAT Gateway<br/>AZ-2]
                end
                
                subgraph "Private Subnet AZ-1"
                    EKS1[EKS Node<br/>t3.large]
                    POD1[Backend Pod]
                    POD2[Frontend Pod]
                end
                
                subgraph "Private Subnet AZ-2"
                    EKS2[EKS Node<br/>t3.large]
                    POD3[Backend Pod]
                    POD4[Frontend Pod]
                end
                
                subgraph "Private Subnet AZ-3"
                    OS1[OpenSearch<br/>Data Node 1]
                    OS2[OpenSearch<br/>Data Node 2]
                end
            end
            
            BEDROCK2[Bedrock Service<br/>Claude 3]
            CW2[CloudWatch<br/>Logs]
        end
    end
    
    INTERNET[Internet] --> ALB2
    ALB2 --> POD1
    ALB2 --> POD3
    
    POD1 --> NAT1
    POD3 --> NAT2
    NAT1 --> BEDROCK2
    NAT2 --> BEDROCK2
    
    POD1 --> OS1
    POD3 --> OS2
    
    POD1 --> CW2
    POD3 --> CW2
    
    EKS1 -.->|Hosts| POD1
    EKS1 -.->|Hosts| POD2
    EKS2 -.->|Hosts| POD3
    EKS2 -.->|Hosts| POD4
    
    style ALB2 fill:#ff9900
    style BEDROCK2 fill:#ff9900
    style OS1 fill:#005eb8
    style OS2 fill:#005eb8
```

## Security Architecture

```mermaid
graph TB
    subgraph "Authentication & Authorization"
        USER[User Request]
        ALB_SEC[ALB<br/>HTTPS/TLS]
        
        subgraph "Kubernetes RBAC"
            SA[ServiceAccount<br/>ai-devops-backend]
            CR[ClusterRole<br/>Pod Access]
            CRB[ClusterRoleBinding]
        end
        
        subgraph "AWS IAM"
            IRSA[IRSA<br/>IAM Role for SA]
            POLICY1[Bedrock Policy]
            POLICY2[CloudWatch Policy]
        end
    end
    
    subgraph "Network Security"
        SG1[Security Group<br/>EKS Nodes]
        SG2[Security Group<br/>OpenSearch]
        NACL[Network ACL]
    end
    
    subgraph "Data Security"
        TLS[TLS 1.2+<br/>In Transit]
        ENC[Encryption<br/>At Rest]
        SECRETS[K8s Secrets<br/>Credentials]
    end
    
    USER --> ALB_SEC
    ALB_SEC --> SA
    SA --> IRSA
    IRSA --> POLICY1
    IRSA --> POLICY2
    
    SA --> CR
    CR --> CRB
    
    SG1 --> SG2
    SG2 --> NACL
    
    TLS --> ENC
    ENC --> SECRETS
    
    style IRSA fill:#ff9900
    style TLS fill:#00ff00
    style ENC fill:#00ff00
```

## RAG System Architecture

```mermaid
graph LR
    subgraph "Document Ingestion"
        DOC[Documentation<br/>Runbooks]
        CHUNK[Text Chunking<br/>512 tokens]
        EMBED[SentenceTransformer<br/>all-MiniLM-L6-v2]
    end
    
    subgraph "Vector Storage"
        VDB[(Vector Database<br/>OpenSearch/Pinecone)]
        INDEX[Vector Index<br/>Cosine Similarity]
    end
    
    subgraph "Query Processing"
        QUERY[User Query]
        QEMBED[Query Embedding]
        SEARCH[Semantic Search<br/>Top-K Results]
    end
    
    subgraph "Response Generation"
        CONTEXT[Retrieved Context]
        PROMPT[Augmented Prompt]
        LLM[Claude 3 Sonnet]
        RESPONSE[AI Response]
    end
    
    DOC --> CHUNK
    CHUNK --> EMBED
    EMBED --> VDB
    VDB --> INDEX
    
    QUERY --> QEMBED
    QEMBED --> SEARCH
    SEARCH --> VDB
    VDB --> CONTEXT
    
    CONTEXT --> PROMPT
    QUERY --> PROMPT
    PROMPT --> LLM
    LLM --> RESPONSE
    
    style VDB fill:#005eb8
    style LLM fill:#ff9900
    style EMBED fill:#009688
```

## Kubernetes Resource Hierarchy

```mermaid
graph TB
    subgraph "Namespace: ai-devops"
        subgraph "Deployments"
            BDEP[Backend Deployment<br/>Replicas: 3]
            FDEP[Frontend Deployment<br/>Replicas: 3]
        end
        
        subgraph "Services"
            BSVC[Backend Service<br/>ClusterIP:8000]
            FSVC[Frontend Service<br/>ClusterIP:80]
        end
        
        subgraph "ConfigMaps"
            CM[ai-devops-config<br/>Environment Variables]
        end
        
        subgraph "Secrets"
            SEC1[aws-credentials]
            SEC2[opensearch-credentials]
            SEC3[pinecone-credentials]
        end
        
        subgraph "RBAC"
            SA2[ServiceAccount]
            CR2[ClusterRole]
            CRB2[ClusterRoleBinding]
        end
        
        subgraph "Autoscaling"
            HPA1[Backend HPA<br/>Min:3 Max:10]
            HPA2[Frontend HPA<br/>Min:3 Max:10]
        end
        
        subgraph "Ingress"
            ING[ALB Ingress<br/>HTTPS + SSL]
        end
    end
    
    BDEP --> BSVC
    FDEP --> FSVC
    
    BDEP -.->|Uses| CM
    BDEP -.->|Uses| SEC1
    BDEP -.->|Uses| SEC2
    BDEP -.->|Uses| SA2
    
    SA2 --> CR2
    CR2 --> CRB2
    
    HPA1 -.->|Scales| BDEP
    HPA2 -.->|Scales| FDEP
    
    ING --> BSVC
    ING --> FSVC
    
    style BDEP fill:#009688
    style FDEP fill:#61dafb
    style ING fill:#ff9900
```

## Technology Stack

```mermaid
mindmap
  root((AI DevOps<br/>Copilot))
    Frontend
      React 18
      TypeScript
      TailwindCSS
      shadcn/ui
      React Query
      React Router
      Vite
    Backend
      Python 3.11
      FastAPI
      Pydantic
      boto3
      kubernetes-client
      SentenceTransformers
    AI/ML
      AWS Bedrock
      Claude 3 Sonnet
      RAG System
      Vector Embeddings
    Infrastructure
      Kubernetes
        EKS
        Kind
        kubectl
        Kustomize
      Terraform
        VPC Module
        EKS Module
        OpenSearch
      AWS
        Bedrock
        CloudWatch
        IAM/IRSA
        ALB
    Data Storage
      OpenSearch
      Pinecone
      Kubernetes Secrets
```

## CI/CD Pipeline (Future)

```mermaid
graph LR
    subgraph "Source Control"
        GIT[GitHub<br/>Repository]
        PR[Pull Request]
    end
    
    subgraph "CI Pipeline"
        LINT[Linting<br/>ESLint/Black]
        TEST[Unit Tests<br/>Pytest/Jest]
        BUILD[Build Images<br/>Docker]
    end
    
    subgraph "CD Pipeline"
        PUSH[Push to ECR]
        DEPLOY_DEV[Deploy to Dev<br/>Kind]
        DEPLOY_PROD[Deploy to Prod<br/>EKS]
    end
    
    subgraph "Monitoring"
        HEALTH_CHECK[Health Checks]
        ROLLBACK[Auto Rollback]
    end
    
    GIT --> PR
    PR --> LINT
    LINT --> TEST
    TEST --> BUILD
    BUILD --> PUSH
    PUSH --> DEPLOY_DEV
    DEPLOY_DEV --> DEPLOY_PROD
    DEPLOY_PROD --> HEALTH_CHECK
    HEALTH_CHECK -->|Failure| ROLLBACK
    
    style BUILD fill:#2088ff
    style DEPLOY_PROD fill:#28a745
```

## Key Features & Capabilities

| Feature | Technology | Purpose |
|---------|-----------|---------|
| **AI Chat** | Claude 3 Sonnet | Natural language infrastructure queries |
| **RAG System** | OpenSearch + Embeddings | Context-aware responses from docs |
| **Log Analysis** | Kubernetes API + Bedrock | Intelligent log parsing and insights |
| **Code Generation** | Bedrock | Generate IaC, K8s manifests, CI/CD |
| **RCA** | Bedrock + K8s Events | Root cause analysis for incidents |
| **Scalability** | HPA + Multi-AZ | Auto-scaling based on load |
| **Security** | IRSA + RBAC + TLS | Secure access to AWS and K8s |
| **Observability** | CloudWatch + Metrics | Monitoring and alerting |

